from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Channel, Message
from .serializers import ChannelSerializer, MessageSerializer

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Channel, Message, Attachment

class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Channel.objects.filter(members=self.request.user, is_archived=False)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        channel = self.get_object()
        messages = Message.objects.filter(channel=channel, parent_message__isnull=True).order_by('-is_pinned', 'created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Use all_objects to include deleted messages for permission checks
        # The soft delete filter is in the default manager, but we need access to all for delete
        return Message.all_objects.filter(channel__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def perform_destroy(self, instance):
        # Use our soft delete logic
        instance.soft_delete(user=self.request.user)
        self._broadcast(instance, 'message_deleted')

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        message = self.get_object()
        message.is_pinned = not message.is_pinned
        message.save()
        
        self._broadcast(message, 'message_pinned' if message.is_pinned else 'message_unpinned')
        
        return Response({'status': 'pinned' if message.is_pinned else 'unpinned', 'is_pinned': message.is_pinned})

    @action(detail=True, methods=['post'])
    def star(self, request, pk=None):
        message = self.get_object()
        user = request.user
        if message.starred_by.filter(id=user.id).exists():
            message.starred_by.remove(user)
            status = 'unstarred'
        else:
            message.starred_by.add(user)
            status = 'starred'
        
        return Response({'status': status, 'is_starred': status == 'starred'})

    @action(detail=True, methods=['post'])
    def forward(self, request, pk=None):
        message = self.get_object()
        target_channel_id = request.data.get('target_channel_id')
        if not target_channel_id:
            return Response({'error': 'Target channel ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_channel = Channel.objects.get(id=target_channel_id, members=request.user)
        except (Channel.DoesNotExist, ValueError):
            return Response({'error': 'Target channel not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        new_message = Message.objects.create(
            channel=target_channel,
            sender=request.user,
            content=message.content,
            forwarded_from=message
        )
        
        if message.voice_message:
            new_message.voice_message = message.voice_message
            new_message.voice_duration = message.voice_duration
            new_message.save()
            
        for att in message.attachments.all():
            Attachment.objects.create(message=new_message, file=att.file)

        self._broadcast(new_message, 'chat_message')

        return Response(MessageSerializer(new_message).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        parent_message = self.get_object()
        content = request.data.get('content', '')
        
        if not content and 'voice_message' not in request.FILES:
            return Response({'error': 'Content or voice message required'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_message = Message.objects.create(
            channel=parent_message.channel,
            sender=request.user,
            content=content,
            parent_message=parent_message
        )
        
        if 'voice_message' in request.FILES:
            new_message.voice_message = request.FILES['voice_message']
            new_message.voice_duration = request.data.get('voice_duration')
            new_message.save()

        self._broadcast(new_message, 'chat_message')

        return Response(MessageSerializer(new_message, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def create_task(self, request, pk=None):
        """Create a project task from a message."""
        try:
            message = self.get_object()
            channel = message.channel
            
            if not channel.shared_project:
                return Response(
                    {'error': 'This channel is not linked to a project. Only project channels can create tasks.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from apps.organizations.models import ProjectTask
            task = ProjectTask.objects.create(
                project=channel.shared_project,
                creator=request.user,
                title=f"Task from chat: {message.content[:50]}...",
                description=message.content,
            )
            
            return Response({
                'status': 'task_created', 
                'task_id': str(task.id),
                'message': 'Task created successfully'
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to create task: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _broadcast(self, message, event_type):
        channel_layer = get_channel_layer()
        channel_id = str(message.channel.id)
        
        data = {
            'type': event_type,
            'message_id': str(message.id),
        }
        
        if event_type == 'chat_message':
            serializer = MessageSerializer(message)
            # Match the format expected by consumer's chat_message handler
            s_data = serializer.data
            data.update({
                'message': s_data['content'],
                'sender_id': s_data['sender'],
                'sender_name': s_data['sender_details']['full_name'] if s_data['sender_details'] else 'Unknown',
                'sender_avatar': s_data['sender_details']['avatar'] if s_data['sender_details'] else None,
                'timestamp': s_data['created_at'],
                'voice_message_url': s_data['voice_message'],
                'voice_duration': s_data['voice_duration'],
                'attachments': s_data['attachments'],
                'is_pinned': s_data['is_pinned'],
                'is_starred': s_data['is_starred'],
                'parent_details': s_data['parent_details']
            })
        elif event_type in ['message_pinned', 'message_unpinned']:
            data['is_pinned'] = message.is_pinned
        elif event_type == 'message_deleted':
            data['deleted_at'] = message.deleted_at.isoformat() if message.deleted_at else None
            data['deleted_by'] = self.request.user.id
            
        async_to_sync(channel_layer.group_send)(
            f'chat_{channel_id}',
            data
        )
