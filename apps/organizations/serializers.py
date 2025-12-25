from rest_framework import serializers
from .models import Organization, Department, Team, SharedProject, ProjectTask, ProjectMilestone
from apps.accounts.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'code', 'logo', 'description', 'timezone']

class DepartmentSerializer(serializers.ModelSerializer):
    head_details = UserSerializer(source='head', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'head', 'head_details', 'is_active', 'member_count']

class TeamSerializer(serializers.ModelSerializer):
    manager_details = UserSerializer(source='manager', read_only=True)
    department_name = serializers.ReadOnlyField(source='department.name')

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'department', 'department_name', 'manager', 'manager_details', 'member_count', 'is_active']

class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = ['id', 'title', 'description', 'target_date', 'is_completed', 'completed_at']

class SharedProjectSerializer(serializers.ModelSerializer):
    host_organization_name = serializers.ReadOnlyField(source='host_organization.name')
    creator_details = UserSerializer(source='created_by', read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = SharedProject
        fields = [
            'id', 'name', 'description', 'host_organization', 'host_organization_name', 
            'created_by', 'creator_details', 'access_code', 'created_at', 'milestones'
        ]
        read_only_fields = ['access_code', 'created_at']
