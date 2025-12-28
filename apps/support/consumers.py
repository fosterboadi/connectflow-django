import json
import google.generativeai as genai
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async

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
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.chat = self.model.start_chat(history=[])
            
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get('message')

        if not user_message:
            return

        if not hasattr(self, 'chat'):
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': "AI Assistant is not properly configured."
            }))
            return

        try:
            # System prompt to give context
            user_info = await self.get_user_context()

            system_context = (
                "You are the ConnectFlow Pro Support Assistant. "
                "ConnectFlow Pro is an organizational communication platform with real-time messaging, "
                "role-based access control, file uploads (Cloudinary), and project management features. "
                "Help the user with their questions about using the platform. "
                "Be professional, concise, and helpful. "
                "If you cannot help, suggest they create a support ticket.\n\n"
                f"Context about the user you are chatting with:\n{user_info}"
            )
            
            response = await self.get_ai_response(f"{system_context}\n\nUser says: {user_message}")
            
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': response
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'bot_message',
                'message': f"I encountered an error while processing your request: {str(e)}"
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
        # Run the blocking API call in a thread
        response = await database_sync_to_async(self.chat.send_message)(prompt)
        return response.text
