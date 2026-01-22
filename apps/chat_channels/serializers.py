from rest_framework import serializers
from .models import Channel, Message, Attachment, MessageReaction
from apps.accounts.serializers import UserSerializer

class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = ['id', 'url', 'is_image', 'is_video']

    def get_url(self, obj):
        return obj.file.url

class MessageReactionSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = MessageReaction
        fields = ['emoji', 'user', 'username']

class MessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    parent_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'channel', 'sender', 'sender_details', 'content', 
            'parent_message', 'parent_details', 'voice_message', 'voice_duration', 
            'is_edited', 'is_pinned', 'forwarded_from', 'star_count', 'is_starred',
            'is_deleted', 'deleted_at', 'deleted_by',
            'created_at', 'attachments', 'reactions'
        ]
        read_only_fields = ['sender', 'is_edited', 'is_deleted', 'created_at', 'is_pinned']

    def get_parent_details(self, obj):
        if obj.parent_message:
            return {
                'id': str(obj.parent_message.id),
                'sender_name': obj.parent_message.sender.get_full_name() or obj.parent_message.sender.username,
                'content': obj.parent_message.content[:100] if not obj.parent_message.is_deleted else 'This message was deleted.'
            }
        return None

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.starred_by.filter(id=request.user.id).exists()
        return False

class ChannelSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField(required=False)
    
    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'description', 'channel_type', 'organization', 
            'is_private', 'read_only', 'member_count', 'created_at', 'display_name'
        ]

    def get_member_count(self, obj):
        # Prefer annotated value if available (more efficient)
        if hasattr(obj, 'member_count_annotated'):
            return obj.member_count_annotated
        # Fallback to model property
        return obj.member_count
    
    def get_display_name(self, obj):
        """Get a friendly display name for the channel"""
        try:
            request = self.context.get('request')
            
            # For DM channels, show the other participant's name
            if obj.channel_type == Channel.ChannelType.DIRECT and request and request.user:
                # Get the other member (not the current user)
                other_member = obj.members.exclude(id=request.user.id).first()
                if other_member:
                    full_name = other_member.get_full_name()
                    return full_name if full_name else other_member.username
                return "Direct Message"
            
            # For other channels, use the name or description
            return obj.name
        except Exception as e:
            # Fallback to basic name if anything fails
            return obj.name
