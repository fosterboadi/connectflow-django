from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'avatar', 'professional_role', 'bio', 
            'status', 'theme', 'timezone'
        ]
        read_only_fields = ['id', 'role']

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None
