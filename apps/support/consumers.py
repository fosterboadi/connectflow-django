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
        try:
            self.user = self.scope["user"]
            print(f"[AI DEBUG] Connecting user: {self.user}")
            if not self.user.is_authenticated:
                print("[AI DEBUG] Rejecting: User not authenticated")
                await self.close()
                return

            await self.accept()
            print("[AI DEBUG] WebSocket accepted")
            
            # --- API Key Management ---
            # Support comma-separated keys for rotation
            raw_keys = settings.GEMINI_API_KEY.split(',')
            self.api_keys = [k.strip() for k in raw_keys if k.strip()]
            self.current_key_index = 0
            
            if self.api_keys:
                print(f"[AI DEBUG] Initializing with {len(self.api_keys)} available keys.")
                
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

                self.tools = [get_my_tickets, get_my_projects, get_project_milestones, get_upcoming_meetings, list_colleagues, find_experts_by_skill]

                # Model Strategy
                # 8B is much more reliable for high-frequency free-tier usage
                self.primary_model_name = 'gemini-1.5-flash-8b'
                self.backup_model_name = 'gemini-1.5-flash'
                
                # Fetch user info safely
                self.user_context_str = await self.get_user_context()
                
                # Start (Wrap initialization in sync_to_async to be 100% safe)
                print(f"[AI DEBUG] Setting up chat with {self.primary_model_name}...")
                await database_sync_to_async(self._init_chat)(self.primary_model_name, self.user_context_str)
                print("[AI DEBUG] Chat initialization complete")
                
                # Send welcome message
                await self.send(text_data=json.dumps({
                    'type': 'bot_message',
                    'message': f"Hello {self.user.first_name or self.user.username}! I'm your ConnectFlow Assistant. How can I help you today?"
                }))
            else:
                print("[AI DEBUG] Warning: GEMINI_API_KEY missing")
                await self.send(text_data=json.dumps({
                    'type': 'bot_message',
                    'message': "I'm sorry, but the AI Assistant is currently unavailable (API key missing)."
                }))
        except Exception as e:
            import traceback
            print(f"[AI DEBUG] CRITICAL ERROR IN CONNECT: {str(e)}")
            traceback.print_exc()
            await self.close()

    def _init_chat(self, model_name, user_info, history=[]):
        """Initialize chat session with a specific model and key."""
        try:
            # Use current key
            key = self.api_keys[self.current_key_index]
            genai.configure(api_key=key)

            system_instruction = (
                "You are the ConnectFlow Pro Support Assistant. "
                "ConnectFlow Pro is an organizational communication platform. "
                "Help users with projects, meetings, and tickets. "
                "Be professional and helpful. "
                "Use your tools to look up real user data when asked.\n\n"
                f"User context: {user_info}"
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
        except Exception as e:
            print(f"[AI DEBUG] ERROR IN _INIT_CHAT: {str(e)}")
            raise e

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            user_message = data.get('message')
            if not user_message or not hasattr(self, 'chat'): return

            # Get response with robust fallback
            response = await self.get_ai_response(user_message)
            
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': response
            }))
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            if "429" in error_msg:
                friendly_msg = "I'm currently receiving too many requests. Please wait 60 seconds and try again."
            else:
                friendly_msg = "I encountered an error. Please try again."

            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': friendly_msg
            }))

    async def get_ai_response(self, prompt):
        return await database_sync_to_async(self._send_message_with_retry)(prompt)

    def _send_message_with_retry(self, prompt):
        """Retry loop that handles Quota errors by switching keys and models."""
        import time
        
        # 1. Try Primary
        try:
            return self.chat.send_message(prompt).text
        except Exception as e:
            error_str = str(e)
            if "429" not in error_str and "ResourceExhausted" not in error_str:
                raise e # Not a quota error
            
            print(f"[AI DEBUG] Quota Hit on {self.current_model_name}")
            
            # 2. Key Rotation Fallback
            if self.current_key_index + 1 < len(self.api_keys):
                self.current_key_index += 1
                print(f"[AI DEBUG] Rotating to Key #{self.current_key_index + 1}...")
                time.sleep(1) # Tiny breather
                self._init_chat(self.current_model_name, self.user_context_str, self.chat.history)
                return self.chat.send_message(prompt).text

            # 3. Model Fallback (If we're out of keys for primary model)
            if self.current_model_name == self.primary_model_name:
                print(f"[AI DEBUG] Switching to backup model {self.backup_model_name}...")
                self.current_key_index = 0 # Reset keys for the new model
                self._init_chat(self.backup_model_name, self.user_context_str, self.chat.history)
                return self.chat.send_message(prompt).text
            
            # 4. Total Exhaustion
            raise e
