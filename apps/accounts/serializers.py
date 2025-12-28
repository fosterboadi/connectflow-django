from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'avatar', 'professional_role', 'bio', 
            'status', 'theme', 'timezone'
        ]
        read_only_fields = ['id', 'role']

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None
