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
    
    class Meta:
        model = Message
        fields = [
            'id', 'channel', 'sender', 'sender_details', 'content', 
            'parent_message', 'voice_message', 'voice_duration', 
            'is_edited', 'is_deleted', 'deleted_at', 'deleted_by',
            'created_at', 'attachments', 'reactions'
        ]
        read_only_fields = ['sender', 'is_edited', 'is_deleted', 'created_at']

class ChannelSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'description', 'channel_type', 'organization', 
            'is_private', 'read_only', 'member_count', 'created_at'
        ]
