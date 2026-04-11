from rest_framework import serializers
from .models import Resource, Booking
from apps.accounts.serializers import UserSerializer

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            'id', 'organization', 'name', 'resource_type', 'description', 
            'location', 'capacity', 'is_active', 'requires_approval'
        ]

class BookingSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    resource_details = ResourceSerializer(source='resource', read_only=True)
    approved_by_details = UserSerializer(source='approved_by', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'resource', 'resource_details', 'user', 'user_details', 
            'title', 'description', 'start_time', 'end_time', 'status', 
            'approved_by', 'approved_by_details', 'approval_notes', 'created_at'
        ]
