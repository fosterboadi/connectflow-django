from rest_framework import serializers
from .models import LeaveType, LeaveRequest, LeaveBalance
from apps.accounts.serializers import UserSerializer

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'organization', 'name', 'description', 'requires_approval', 'counts_as_leave', 'color']

class LeaveRequestSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    leave_type_details = LeaveTypeSerializer(source='leave_type', read_only=True)
    approved_by_details = UserSerializer(source='approved_by', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'user', 'user_details', 'leave_type', 'leave_type_details', 
            'start_date', 'end_date', 'total_days', 'reason', 'status', 
            'approved_by', 'approved_by_details', 'rejection_reason', 'created_at'
        ]

class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_details = LeaveTypeSerializer(source='leave_type', read_only=True)
    remaining = serializers.ReadOnlyField()
    percent_used = serializers.ReadOnlyField()

    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'user', 'leave_type', 'leave_type_details', 'year', 
            'total_allocated', 'used', 'remaining', 'percent_used'
        ]
