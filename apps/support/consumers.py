import json
import google.generativeai as genai
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async
from .ai_tools import (
    _db_get_tickets, _db_get_projects, _db_get_project_milestones, 
    _db_get_upcoming_meetings, _db_get_colleagues, _db_find_experts
)

class SupportAIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        await self.accept()
        
        # Initialize Gemini
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # --- Define User-Bound Tools ---
            def get_my_tickets():
                """Fetch the list of my recent support tickets and their status."""
                return _db_get_tickets(self.user)

            def get_my_projects():
                """List the shared projects I am currently a member of."""
                return _db_get_projects(self.user)

            def get_project_milestones(project_id_prefix: str):
                """Get the progress and milestones for a specific project. Use the first few characters of the project ID."""
                return _db_get_project_milestones(self.user, project_id_prefix)

            def get_upcoming_meetings():
                """List all scheduled meetings for projects I am involved in."""
                return _db_get_upcoming_meetings(self.user)

            def list_colleagues():
                """List the people in my organization and their professional roles."""
                return _db_get_colleagues(self.user)

            def find_experts_by_skill(skill_name: str):
                """Search for colleagues who have a specific skill or expertise (e.g. 'Python', 'Design')."""
                return _db_find_experts(self.user, skill_name)

            self.tools = [
                get_my_tickets, 
                get_my_projects, 
                get_project_milestones, 
                get_upcoming_meetings, 
                list_colleagues, 
                find_experts_by_skill
            ]

            # Model Strategy
            # Primary: The high-speed 2.0 version confirmed in your list
            self.primary_model_name = 'gemini-2.0-flash' 
            # Backup: The stable production alias (which points to current stable Flash)
            self.backup_model_name = 'gemini-flash-latest'
            
            # Start with primary
            self.current_model_name = self.primary_model_name
            self._init_chat(self.current_model_name)
            
            # Send welcome message
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': f"Hello {self.user.first_name or self.user.username}! I'm your ConnectFlow Assistant. How can I help you today?"
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': "I'm sorry, but the AI Assistant is currently unavailable (API key missing). Please create a support ticket instead."
            }))

    def _init_chat(self, model_name, history=[]):
        """Initialize chat session with a specific model and history."""
        # Get user info for system instruction
        user_info = f"User: {self.user.get_full_name()} ({self.user.username})"
        if self.user.organization:
            user_info += f"\nOrganization: {self.user.organization.name}"
        user_info += f"\nRole: {self.user.get_role_display()}"

        system_instruction = (
            "You are the ConnectFlow Pro Support Assistant. "
            "ConnectFlow Pro is an organizational communication platform with real-time messaging, "
            "role-based access control, file uploads (Cloudinary), and project management features. "
            "Help the user with their questions about using the platform. "
            "Be professional, concise, and helpful. "
            "You have access to tools to look up the user's tickets and projects. "
            "ALWAYS check these tools if the user asks about their specific data. "
            "If you cannot help, suggest they create a support ticket.\n\n"
            f"Context about the user you are chatting with:\n{user_info}"
        )

        self.model = genai.GenerativeModel(
            model_name,
            tools=self.tools,
            system_instruction=system_instruction
        )
        self.chat = self.model.start_chat(
            history=history,
            enable_automatic_function_calling=True
        )
        self.current_model_name = model_name

    async def receive(self, text_data):
        print(f"[AI DEBUG] Received message from user: {self.user.username}")
        try:
            data = json.loads(text_data)
            user_message = data.get('message')

            if not user_message:
                return

            if not hasattr(self, 'chat'):
                print("[AI DEBUG] Error: Chat object not initialized")
                await self.send(text_data=json.dumps({
                    'type': 'bot_message',
                    'message': "AI Assistant is not properly configured."
                }))
                return

            # Use fallback-aware response getter
            print(f"[AI DEBUG] Sending request to Gemini (Model: {self.current_model_name})...")
            response = await self.get_ai_response(user_message)
            print("[AI DEBUG] Gemini responded successfully.")
            
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': response
            }))
        except Exception as e:
            import traceback
            print(f"[AI DEBUG] EXCEPTION in receive: {str(e)}")
            traceback.print_exc()
            
            error_msg = str(e)
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                friendly_msg = "I'm currently overwhelmed with requests (Daily/Minute Quota Exceeded). Please try again in a few minutes."
            else:
                friendly_msg = f"I encountered an error while processing your request. Please try again."

            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': friendly_msg
            }))

    @database_sync_to_async
    def get_user_context(self):
        """Fetch user details safely in a sync context."""
        user_info = f"User: {self.user.get_full_name()} ({self.user.username})"
        # Accessing foreign keys triggers DB queries, so this must be sync
        if self.user.organization:
            user_info += f"\nOrganization: {self.user.organization.name}"
        user_info += f"\nRole: {self.user.get_role_display()}"
        return user_info

    async def get_ai_response(self, prompt):
        # Run the sync logic (with retry) in a thread
        return await database_sync_to_async(self._send_message_with_retry)(prompt)

    def _send_message_with_retry(self, prompt):
        """Try sending message with current model, switch to backup on 429."""
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            # Check for quota error (429 or ResourceExhausted)
            error_str = str(e)
            if ("429" in error_str or "ResourceExhausted" in error_str) and self.current_model_name == self.primary_model_name:
                # Switch to backup
                # Preserve history
                current_history = self.chat.history
                
                # Re-init with backup model
                self._init_chat(self.backup_model_name, history=current_history)
                
                # Retry send
                response = self.chat.send_message(prompt)
                return response.text
            else:
                # Re-raise if it's not a quota error OR we are already on backup
                raise e
