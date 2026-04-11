from rest_framework import serializers
from apps.chat_channels.models import Call, CallParticipant
from apps.accounts.serializers import UserSerializer

class CallParticipantSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = CallParticipant
        fields = [
            'id', 'user', 'user_details', 'status', 'is_audio_enabled', 
            'is_video_enabled', 'is_screen_sharing', 'joined_at', 'left_at'
        ]

class CallSerializer(serializers.ModelSerializer):
    initiator_details = UserSerializer(source='initiator', read_only=True)
    participants_details = CallParticipantSerializer(source='participant_records', many=True, read_only=True)
    channel_name = serializers.ReadOnlyField(source='channel.name')

    class Meta:
        model = Call,
        fields = [
            'id', 'call_type', 'status', 'initiator', 'initiator_details', 
            'channel', 'channel_name', 'participants_details', 'room_id', 
            'started_at', 'ended_at', 'created_at'
        ]
        read_only_fields = ['room_id', 'started_at', 'ended_at', 'created_at']
