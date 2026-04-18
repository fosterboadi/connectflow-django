import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from apps.chat_channels.models import Call, CallParticipant, Channel

User = get_user_model()


class CallConsumer(AsyncWebsocketConsumer):
    """
    WebRTC signaling consumer for voice/video calls.
    Handles WebRTC signaling (SDP offer/answer, ICE candidates).
    """
    
    async def connect(self):
        """Accept WebSocket connection."""
        self.user = self.scope['user']
        self.call_id = self.scope['url_route']['kwargs']['call_id']
        self.room_group_name = f'call_{self.call_id}'

        if not self.user.is_authenticated:
            await self.close()
            return

        if not await self.check_call_access():
            await self.close()
            return
        
        # Join call room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': str(self.user.id),
                'user_name': self.user.get_full_name() or self.user.username,
                'username': self.user.username,
                'full_name': self.user.get_full_name(),
                'should_create_offer': True,
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect."""
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': str(self.user.id),
                'username': self.user.username,
            }
        )
        
        # Leave call room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        message_type = data.get('type')
        
        # Handle different signaling messages
        if message_type in ['offer', 'webrtc_offer']:
            await self.handle_offer(data)
        elif message_type in ['answer', 'webrtc_answer']:
            await self.handle_answer(data)
        elif message_type == 'ice_candidate':
            await self.handle_ice_candidate(data)
        elif message_type == 'toggle_audio':
            await self.handle_toggle_audio(data)
        elif message_type == 'toggle_video':
            await self.handle_toggle_video(data)
        elif message_type == 'start_screen_share':
            await self.handle_screen_share(data)
        elif message_type == 'end_call':
            await self.handle_end_call(data)
        elif message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'poll_created':
            await self.handle_poll_created(data)
        elif message_type == 'poll_vote':
            await self.handle_poll_vote(data)
    
    async def handle_offer(self, data):
        """Handle WebRTC offer."""
        to_user_id = data.get('to_user_id') or data.get('target_user_id')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_offer',
                'offer': data.get('offer'),
                'from_user_id': str(self.user.id),
                'sender_id': str(self.user.id),
                'sender_name': self.user.get_full_name() or self.user.username,
                'to_user_id': to_user_id,
            }
        )
    
    async def handle_answer(self, data):
        """Handle WebRTC answer."""
        to_user_id = data.get('to_user_id') or data.get('target_user_id')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_answer',
                'answer': data.get('answer'),
                'from_user_id': str(self.user.id),
                'sender_id': str(self.user.id),
                'sender_name': self.user.get_full_name() or self.user.username,
                'to_user_id': to_user_id,
            }
        )
    
    async def handle_ice_candidate(self, data):
        """Handle ICE candidate."""
        to_user_id = data.get('to_user_id') or data.get('target_user_id')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ice_candidate',
                'candidate': data.get('candidate'),
                'from_user_id': str(self.user.id),
                'sender_id': str(self.user.id),
                'to_user_id': to_user_id,
            }
        )

    async def handle_chat_message(self, data):
        """Relay in-call chat messages to all call participants."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_event',
                'message': data.get('message', ''),
                'sender_id': str(self.user.id),
                'sender_name': self.user.get_full_name() or self.user.username,
            }
        )

    async def handle_poll_created(self, data):
        """Relay poll creation events."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'poll_created_event',
                'poll': data.get('poll'),
                'sender_id': str(self.user.id),
            }
        )

    async def handle_poll_vote(self, data):
        """Relay poll vote events."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'poll_vote_event',
                'poll_id': data.get('poll_id'),
                'option_index': data.get('option_index'),
                'sender_id': str(self.user.id),
            }
        )
    
    async def handle_toggle_audio(self, data):
        """Handle audio toggle."""
        enabled = data.get('enabled', False)
        
        # Update participant record
        await self.update_participant_audio(enabled)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'audio_toggled',
                'user_id': str(self.user.id),
                'enabled': enabled,
            }
        )
    
    async def handle_toggle_video(self, data):
        """Handle video toggle."""
        enabled = data.get('enabled', False)
        
        # Update participant record
        await self.update_participant_video(enabled)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'video_toggled',
                'user_id': str(self.user.id),
                'enabled': enabled,
            }
        )
    
    async def handle_screen_share(self, data):
        """Handle screen sharing."""
        is_sharing = data.get('is_sharing', False)
        
        # Update participant record
        await self.update_participant_screen_share(is_sharing)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_toggled',
                'user_id': str(self.user.id),
                'is_sharing': is_sharing,
            }
        )
    
    async def handle_end_call(self, data):
        """Handle end call."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_ended',
                'user_id': str(self.user.id),
            }
        )
    
    # Handlers for group messages
    async def user_joined(self, event):
        """Send user_joined message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'user_name': event.get('user_name') or event.get('full_name') or event.get('username'),
            'username': event['username'],
            'full_name': event['full_name'],
            'should_create_offer': event.get('should_create_offer', True),
        }))
    
    async def user_left(self, event):
        """Send user_left message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def webrtc_offer(self, event):
        """Send WebRTC offer to specific user."""
        if str(self.user.id) == event['to_user_id']:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_offer',
                'offer': event['offer'],
                'from_user_id': event['from_user_id'],
                'sender_id': event.get('sender_id', event['from_user_id']),
                'sender_name': event.get('sender_name'),
            }))
    
    async def webrtc_answer(self, event):
        """Send WebRTC answer to specific user."""
        if str(self.user.id) == event['to_user_id']:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_answer',
                'answer': event['answer'],
                'from_user_id': event['from_user_id'],
                'sender_id': event.get('sender_id', event['from_user_id']),
                'sender_name': event.get('sender_name'),
            }))
    
    async def ice_candidate(self, event):
        """Send ICE candidate to specific user."""
        if str(self.user.id) == event['to_user_id']:
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'candidate': event['candidate'],
                'from_user_id': event['from_user_id'],
                'sender_id': event.get('sender_id', event['from_user_id']),
            }))
    
    async def audio_toggled(self, event):
        """Broadcast audio toggle."""
        await self.send(text_data=json.dumps({
            'type': 'audio_toggled',
            'user_id': event['user_id'],
            'enabled': event['enabled'],
        }))
    
    async def video_toggled(self, event):
        """Broadcast video toggle."""
        await self.send(text_data=json.dumps({
            'type': 'video_toggled',
            'user_id': event['user_id'],
            'enabled': event['enabled'],
        }))
    
    async def screen_share_toggled(self, event):
        """Broadcast screen share toggle."""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_toggled',
            'user_id': event['user_id'],
            'is_sharing': event['is_sharing'],
        }))
    
    async def call_ended(self, event):
        """Broadcast call ended."""
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'user_id': event['user_id'],
        }))

    async def chat_message_event(self, event):
        """Broadcast in-call chat message."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event.get('message', ''),
            'sender_id': event.get('sender_id'),
            'sender_name': event.get('sender_name'),
        }))

    async def poll_created_event(self, event):
        """Broadcast poll created event."""
        await self.send(text_data=json.dumps({
            'type': 'poll_created',
            'poll': event.get('poll'),
            'sender_id': event.get('sender_id'),
        }))

    async def poll_vote_event(self, event):
        """Broadcast poll vote event."""
        await self.send(text_data=json.dumps({
            'type': 'poll_vote',
            'poll_id': event.get('poll_id'),
            'option_index': event.get('option_index'),
            'sender_id': event.get('sender_id'),
        }))
    
    # Database operations
    @database_sync_to_async
    def update_participant_audio(self, enabled):
        """Update participant audio state."""
        try:
            participant = CallParticipant.objects.get(
                call_id=self.call_id,
                user=self.user
            )
            participant.is_audio_enabled = enabled
            participant.save()
        except CallParticipant.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_participant_video(self, enabled):
        """Update participant video state."""
        try:
            participant = CallParticipant.objects.get(
                call_id=self.call_id,
                user=self.user
            )
            participant.is_video_enabled = enabled
            participant.save()
        except CallParticipant.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_participant_screen_share(self, is_sharing):
        """Update participant screen share state."""
        try:
            participant = CallParticipant.objects.get(
                call_id=self.call_id,
                user=self.user
            )
            participant.is_screen_sharing = is_sharing
            participant.save()
        except CallParticipant.DoesNotExist:
            pass

    @database_sync_to_async
    def check_call_access(self):
        """Ensure only invited/participant users can connect to call signaling."""
        try:
            call = Call.objects.get(pk=self.call_id)
            return call.participants.filter(pk=self.user.pk).exists()
        except Call.DoesNotExist:
            return False
