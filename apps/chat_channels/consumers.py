import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Channel, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = f'chat_{self.channel_id}'
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user has access to channel
        if not await self.check_channel_access():
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Update user status to ONLINE
        await self.update_user_status('ONLINE')
        
        # Broadcast presence
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status_change',
                'user_id': self.user.id,
                'status': 'ONLINE'
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            # Update user status to OFFLINE
            await self.update_user_status('OFFLINE')
            
            # Broadcast presence
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status_change',
                    'user_id': self.user.id,
                    'status': 'OFFLINE'
                }
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'chat_message':
            message_id = data.get('message_id')
            content = data.get('message', '')
            voice_url = data.get('voice_message_url')
            attachments = data.get('attachments', [])
            parent_id = data.get('parent_message_id')
            
            # Prepare common broadcast data
            broadcast_data = {
                'type': 'chat_message',
                'message': content,
                'sender_id': self.user.id,
                'sender_name': self.user.get_full_name(),
                'sender_avatar': self.user.avatar.url if self.user.avatar else None,
                'timestamp': data.get('timestamp', timezone.now().strftime('%b %d, %I:%M %p')),
                'voice_message_url': voice_url,
                'voice_duration': data.get('voice_duration'),
                'attachments': attachments,
                'parent_message_id': parent_id
            }

            if message_id:
                # Message already exists (e.g. voice/file upload via AJAX)
                broadcast_data['message_id'] = message_id
                await self.channel_layer.group_send(self.room_group_name, broadcast_data)
            elif content or voice_url:
                # New message to save
                saved_message = await self.save_message(content, parent_id)
                broadcast_data['message_id'] = str(saved_message.id)
                broadcast_data['timestamp'] = saved_message.created_at.strftime('%b %d, %I:%M %p')
                
                # Trigger notifications
                await self.trigger_notifications(saved_message)
                
                # Send to room
                await self.channel_layer.group_send(self.room_group_name, broadcast_data)

        elif message_type == 'message_edit':
            message_id = data.get('message_id')
            content = data.get('message')
            if message_id and content:
                # Update message in database
                success = await self.edit_message(message_id, content)
                if success:
                    # Send updated message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_update',
                            'message_id': message_id,
                            'message': content
                        }
                    )
        elif message_type == 'message_delete':
            message_id = data.get('message_id')
            if message_id:
                success, deleted_at = await self.delete_message(message_id)
                if success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'message_deleted',
                            'message_id': message_id,
                            'deleted_at': deleted_at.isoformat() if deleted_at else None,
                            'deleted_by': self.user.id
                        }
                    )
        elif message_type == 'typing':
            # Send typing indicator to room group (excluding the sender)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'sender_id': self.user.id,
                    'sender_name': self.user.get_full_name(),
                    'is_typing': data.get('is_typing', False)
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event.get('message', ''),
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event['sender_avatar'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
            'voice_message_url': event.get('voice_message_url'),
            'voice_duration': event.get('voice_duration'),
            'attachments': event.get('attachments', [])
        }))

    async def user_typing(self, event):
        # Send typing indicator to WebSocket (only if it's not the sender themselves)
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'sender_id': event['sender_id'],
                'sender_name': event['sender_name'],
                'is_typing': event['is_typing']
            }))

    async def message_update(self, event):
        # Send message update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message_update',
            'message_id': event['message_id'],
            'message': event['message']
        }))

    async def message_deleted(self, event):
        # Send message deletion to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message_delete',
            'message_id': event['message_id'],
            'deleted_at': event.get('deleted_at'),
            'deleted_by': event.get('deleted_by')
        }))

    async def user_status_change(self, event):
        # Send status change to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'user_id': event['user_id'],
            'status': event['status']
        }))

    async def trigger_notifications(self, message):
        """Logic to determine who needs a notification for this new message."""
        from apps.accounts.models import Notification, User
        from django.urls import reverse
        import re
        
        channel = await database_sync_to_async(lambda: message.channel)()
        channel_type = await database_sync_to_async(lambda: channel.channel_type)()
        channel_url = reverse('chat_channels:channel_detail', kwargs={'pk': str(channel.id)})
        
        # 1. Handle Mentions (@username)
        mentions = re.findall(r'@(\w+)', message.content)
        recipient_ids = set() # Track who we've notified to avoid duplicates
        
        if mentions:
            for username in set(mentions):
                try:
                    recipient = await database_sync_to_async(User.objects.get)(username=username)
                    if recipient.id != self.user.id:
                        notification = await database_sync_to_async(Notification.notify)(
                            recipient=recipient,
                            sender=self.user,
                            title=f"Mentioned in #{channel.name}",
                            content=f"{self.user.get_full_name()} mentioned you: {message.content[:50]}...",
                            notification_type='MENTION',
                            link=channel_url
                        )
                        await self.broadcast_notification(recipient.id, notification)
                        recipient_ids.add(recipient.id)
                except Exception:
                    continue
        
        # 2. Handle Replies (Notify original sender)
        parent = await database_sync_to_async(lambda: message.parent_message)()
        if parent:
            parent_sender = await database_sync_to_async(lambda: parent.sender)()
            if parent_sender.id != self.user.id and parent_sender.id not in recipient_ids:
                notification = await database_sync_to_async(Notification.notify)(
                    recipient=parent_sender,
                    sender=self.user,
                    title=f"New reply in #{channel.name}",
                    content=f"{self.user.get_full_name()} replied to your message: {message.content[:50]}...",
                    notification_type='MESSAGE',
                    link=channel_url
                )
                await self.broadcast_notification(parent_sender.id, notification)
                recipient_ids.add(parent_sender.id)

        # 3. Handle Direct Messages (Notify the other person if not already notified)
        if channel_type == 'DIRECT':
            other_members = await database_sync_to_async(
                lambda: list(channel.members.exclude(id=self.user.id))
            )()
            )()
            
            for recipient in other_members:
                if recipient.id not in recipient_ids:
                    notification = await database_sync_to_async(Notification.notify)(
                        recipient=recipient,
                        sender=self.user,
                        title=f"New message from {self.user.get_full_name()}",
                        content=message.content[:100],
                        notification_type='MESSAGE',
                        link=channel_url
                    )
                    await self.broadcast_notification(recipient.id, notification)

    async def broadcast_notification(self, recipient_id, notification):
        """Send a notification message to a specific user's notification group."""
        await self.channel_layer.group_send(
            f"notifications_{recipient_id}",
            {
                'type': 'send_notification',
                'id': str(notification.id),
                'title': notification.title,
                'content': notification.content,
                'notification_type': notification.notification_type,
                'link': notification.link,
                'created_at': "Just now"
            }
        )

    @database_sync_to_async
    def check_channel_access(self):
        try:
            channel = Channel.objects.get(id=self.channel_id)
            return channel.can_user_view(self.user)
        except Channel.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, parent_id=None):
        channel = Channel.objects.get(id=self.channel_id)
        parent = None
        if parent_id:
            try:
                parent = Message.objects.get(id=parent_id)
            except Message.DoesNotExist:
                pass
                
        return Message.objects.create(
            channel=channel,
            sender=self.user,
            content=content,
            parent_message=parent
        )

    @database_sync_to_async
    def edit_message(self, message_id, content):
        try:
            message = Message.objects.get(id=message_id, sender=self.user)
            message.content = content
            message.is_edited = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            # Allow sender or admin to delete
            message = Message.objects.get(id=message_id)
            if message.sender == self.user or self.user.is_admin:
                message.delete(user=self.user) # Uses the soft delete implemented in models.py
                return True, message.deleted_at
            return False, None
        except Message.DoesNotExist:
            return False, None

    @database_sync_to_async
    def update_user_status(self, status):
        User.objects.filter(id=self.user.id).update(status=status, last_seen=timezone.now())
