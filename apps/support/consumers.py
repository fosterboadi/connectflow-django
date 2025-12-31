import json
import time
import google.generativeai as genai
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async
from .ai_tools import (
    _db_get_tickets, _db_get_projects, _db_get_project_milestones, 
    _db_get_upcoming_meetings, _db_get_colleagues, _db_find_experts,
    get_platform_revenue, _db_get_tasks, _db_get_risks, _db_get_compliance,
    _db_get_project_summary, _db_get_recent_activity
)

class SupportAIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope["user"]
            if not self.user.is_authenticated:
                await self.close()
                return

            await self.accept()
            
            # --- API Key Management ---
            raw_keys = getattr(settings, 'GEMINI_API_KEY', '').split(',')
            self.api_keys = [k.strip() for k in raw_keys if k.strip()]
            self.current_key_index = 0
            
            if self.api_keys:
                # Use stable aliases for the highest possible quota (1,500/day)
                self.primary_model_name = 'gemini-flash-latest'
                self.backup_model_name = 'gemini-pro-latest'
                
                context_data = await self.get_user_context()
                self.user_context_str = context_data['instruction']
                self.display_name = context_data['display_name']
                
                # --- Define User-Bound Tools ---
                def get_my_tickets():
                    """Fetch the list of my recent support tickets and their status."""
                    return _db_get_tickets(self.user)

                def get_my_projects():
                    """List the shared projects I am currently a member of."""
                    return _db_get_projects(self.user)

                def get_project_milestones(project_id_prefix: str):
                    """Get the progress and milestones for a specific project."""
                    return _db_get_project_milestones(self.user, project_id_prefix)

                def get_upcoming_meetings():
                    """List all scheduled meetings for projects I am involved in."""
                    return _db_get_upcoming_meetings(self.user)

                def list_colleagues():
                    """List the people in my organization and their professional roles."""
                    return _db_get_colleagues(self.user)

                def find_experts_by_skill(skill_name: str):
                    """Search for colleagues who have a specific skill (e.g. 'Python')."""
                    return _db_find_experts(self.user, skill_name)

                def get_revenue_data():
                    """(Admin Only) Get total platform revenue and recent payments."""
                    return get_platform_revenue(self.user)

                def get_my_tasks(status: str = None):
                    """Get the list of tasks assigned to me or in my projects. Status can be 'TODO', 'IN_PROGRESS', etc."""
                    return _db_get_tasks(self.user, status)

                def get_project_risks(project_name: str = None):
                    """Get the identified risks for a project."""
                    return _db_get_risks(self.user, project_name)

                def get_compliance_requirements(project_name: str = None):
                    """Get compliance requirements and regulations for a project."""
                    return _db_get_compliance(self.user, project_name)

                def get_project_analytics(project_name: str):
                    """Get completion rate and task statistics for a project."""
                    return _db_get_project_summary(self.user, project_name)

                def get_weekly_snapshot():
                    """Get a summary of platform activity (new tasks/files) from the last 7 days."""
                    return _db_get_recent_activity(self.user)

                self.tools = [
                    get_my_tickets, get_my_projects, get_project_milestones, 
                    get_upcoming_meetings, list_colleagues, find_experts_by_skill, 
                    get_revenue_data, get_my_tasks, get_project_risks, 
                    get_compliance_requirements, get_project_analytics, get_weekly_snapshot
                ]

                # Initialize chat with primary model
                try:
                    await self.initialize_chat_session(self.primary_model_name)
                    
                    await self.send(text_data=json.dumps({
                        'type': 'bot_message',
                        'message': f"Hello {self.display_name}! I'm your ConnectFlow Assistant. How can I help you today?"
                    }))
                except Exception as e:
                    print(f"[AI ERROR] Initialization failed: {str(e)}")
                    await self.send(text_data=json.dumps({
                        'type': 'bot_message',
                        'message': "I'm sorry, I'm having trouble initializing. Please check the server logs."
                    }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'bot_message',
                    'message': "I'm sorry, the AI Assistant is currently unavailable (API key not configured)."
                }))
        except Exception as e:
            print(f"[AI ERROR] Connect failure: {str(e)}")
            await self.close()

    async def initialize_chat_session(self, model_name):
        """Initialize or re-initialize the chat session safely."""
        try:
            # We must use database_sync_to_async for the SDK calls as they can block
            await database_sync_to_async(self._sync_init_chat)(model_name)
        except Exception as e:
            print(f"[AI ERROR] Chat Init Error: {str(e)}")
            raise e

    def _sync_init_chat(self, model_name):
        """Synchronous part of chat initialization."""
        key = self.api_keys[self.current_key_index]
        
        # Configure is global, which is a limitation of the current SDK.
        # We try to mitigate by re-configuring right before starting the model.
        genai.configure(api_key=key)

        system_instruction = (
            "You are the ConnectFlow Pro Support Assistant. "
            "ConnectFlow Pro is an organizational communication platform. "
            "Help users with projects, meetings, and tickets. "
            "Be professional and helpful. "
            "Use your tools to look up real user data when asked.\n\n"
            f"User context: {self.user_context_str}"
        )

        model = genai.GenerativeModel(
            model_name=model_name,
            tools=self.tools,
            system_instruction=system_instruction
        )
        
        # Maintain history if we are rotating/recovering
        history = self.chat.history if hasattr(self, 'chat') else []
        
        self.chat = model.start_chat(
            history=history,
            enable_automatic_function_calling=True
        )
        self.current_model_name = model_name

    async def receive(self, text_data):
        try:
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                print(f"[AI ERROR] Invalid JSON received: {text_data}")
                return

            if data.get('type') == 'ping':
                return

            user_message = data.get('message')
            if not user_message or not hasattr(self, 'chat'): return

            # Get response with robust retry/fallback logic
            response_text = await self.get_ai_response(user_message)
            
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': response_text
            }))
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[AI ERROR] Receive loop error: {str(e)}")
            # Log to a file we can read
            with open("ai_debug.log", "a") as f:
                f.write(f"\n--- ERROR at {time.ctime()} ---\n")
                f.write(error_details)
                f.write("\n---------------------------\n")

            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': f"I encountered an error: {str(e)}"
            }))

    async def get_ai_response(self, prompt):
        """Wrapper for the retry logic."""
        return await database_sync_to_async(self._sync_send_with_retry)(prompt)

    def _sync_send_with_retry(self, prompt):
        """Handles quota limits and model fallbacks."""
        import time
        max_retries = len(self.api_keys) * 2 # Try keys, then try backup model
        
        for attempt in range(max_retries):
            try:
                # Ensure configuration is correct for THIS call (mitigate global state)
                genai.configure(api_key=self.api_keys[self.current_key_index])
                return self.chat.send_message(prompt).text
            except Exception as e:
                err = str(e)
                if "429" in err or "ResourceExhausted" in err:
                    print(f"[AI DEBUG] Quota exceeded for {self.current_model_name} (Key {self.current_key_index})")
                    
                    # Try next key
                    if self.current_key_index + 1 < len(self.api_keys):
                        self.current_key_index += 1
                        self._sync_init_chat(self.current_model_name)
                        time.sleep(1)
                        continue
                    
                    # If all keys exhausted for primary, try backup model
                    if self.current_model_name == self.primary_model_name:
                        print(f"[AI DEBUG] All keys exhausted for {self.primary_model_name}. Switching to backup...")
                        self.current_key_index = 0
                        self._sync_init_chat(self.backup_model_name)
                        continue
                
                # If it's not a quota error or we're totally exhausted
                raise e
        
        return "I'm currently overloaded with requests. Please try again in a minute."

    @database_sync_to_async
    def get_user_context(self):
        """Fetch user details and a Situational Snapshot safely."""
        from apps.organizations.models import SharedProject, ProjectTask
        from apps.support.models import Ticket
        
        display_name = self.user.first_name or self.user.username
        
        # Situational Snapshot (Low token cost, high context value)
        project_count = self.user.shared_projects.count()
        pending_tasks = ProjectTask.objects.filter(project__members=self.user).exclude(status='COMPLETED').count()
        open_tickets = Ticket.objects.filter(requester=self.user, status='OPEN').count()
        
        user_info = f"User: {self.user.get_full_name()} ({self.user.username})"
        if self.user.organization:
            user_info += f"\nOrganization: {self.user.organization.name}"
        user_info += f"\nRole: {self.user.get_role_display()}"
        
        # Add Snapshot to the instruction
        user_info += f"\n\nCURRENT SNAPSHOT:\n- Active Projects: {project_count}\n- Pending Tasks: {pending_tasks}\n- Open Support Tickets: {open_tickets}"
        user_info += "\nAlways use tools to fetch detailed lists if the user asks for them."
        
        return {
            'instruction': user_info,
            'display_name': display_name
        }
