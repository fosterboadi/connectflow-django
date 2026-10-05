from rest_framework import serializers
from .models import Announcement, AnnouncementReadReceipt
from apps.accounts.serializers import UserSerializer

class AnnouncementSerializer(serializers.ModelSerializer):
    creator_details = UserSerializer(source='created_by', read_only=True)
    target_department_name = serializers.ReadOnlyField(source='target_department.name')
    target_team_name = serializers.ReadOnlyField(source='target_team.name')
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Announcement
        fields = [
            'id', 'organization', 'title', 'content', 'priority', 
            'target_department', 'target_department_name', 'target_team', 
            'target_team_name', 'target_role', 'is_published', 
            'scheduled_at', 'expires_at', 'require_acknowledgement', 
            'is_pinned', 'created_by', 'creator_details', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['organization', 'created_by', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        organization = getattr(request.user, 'organization', None) if request else None
        for field_name in ('target_department', 'target_team'):
            target = attrs.get(field_name)
            if target and organization and target.organization_id != organization.id:
                raise serializers.ValidationError(
                    {field_name: 'This target must belong to your organization.'}
                )
        return attrs

class AnnouncementReadReceiptSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = AnnouncementReadReceipt
        fields = ['id', 'announcement', 'user', 'user_details', 'read_at', 'acknowledged_at']
        read_only_fields = ['user', 'read_at', 'acknowledged_at']

    def validate_announcement(self, announcement):
        request = self.context.get('request')
        if request and announcement.organization_id != request.user.organization_id:
            raise serializers.ValidationError(
                'You cannot acknowledge an announcement from another organization.'
            )
        return announcement
