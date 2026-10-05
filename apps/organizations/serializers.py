from rest_framework import serializers
from .models import (
    Organization, Department, Team, SharedProject, ProjectTask, 
    ProjectMilestone, ProjectFile, ProjectMeeting, ProjectRiskRegister,
    SubscriptionPlan, SubscriptionTransaction, AuditTrail, ControlTest,
    ComplianceRequirement, ComplianceEvidence
)
from apps.accounts.serializers import UserSerializer

def _request_user(serializer):
    request = serializer.context.get('request')
    return request.user if request and request.user.is_authenticated else None

def _validate_project_access(serializer, project):
    user = _request_user(serializer)
    if user and not project.members.filter(pk=user.pk).exists():
        raise serializers.ValidationError(
            {'project': 'You do not have access to this project.'}
        )

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'code', 'logo', 'description', 'timezone', 'industry', 'website', 'size', 'headquarters']

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

    def validate_department(self, department):
        user = _request_user(self)
        if user and department.organization_id != user.organization_id:
            raise serializers.ValidationError(
                'You cannot use a department from another organization.'
            )
        return department

class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = ['id', 'project', 'title', 'description', 'target_date', 'is_completed', 'completed_at']

    def validate_project(self, project):
        _validate_project_access(self, project)
        return project

class ProjectTaskSerializer(serializers.ModelSerializer):
    creator_details = UserSerializer(source='creator', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)

    class Meta:
        model = ProjectTask
        fields = ['id', 'project', 'creator', 'creator_details', 'assigned_to', 'assigned_to_details', 'title', 'description', 'status', 'due_date', 'created_at']
        read_only_fields = ['creator']

    def validate_project(self, project):
        _validate_project_access(self, project)
        return project

class ProjectFileSerializer(serializers.ModelSerializer):
    uploader_details = UserSerializer(source='uploader', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectFile
        fields = ['id', 'project', 'uploader', 'uploader_details', 'file', 'file_url', 'name', 'description', 'created_at']
        read_only_fields = ['uploader']

    def validate_project(self, project):
        _validate_project_access(self, project)
        return project

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None

class ProjectMeetingSerializer(serializers.ModelSerializer):
    organizer_details = UserSerializer(source='organizer', read_only=True)

    class Meta:
        model = ProjectMeeting
        fields = ['id', 'project', 'organizer', 'organizer_details', 'title', 'description', 'start_time', 'end_time', 'meeting_link']
        read_only_fields = ['organizer']

    def validate_project(self, project):
        _validate_project_access(self, project)
        return project

class ProjectRiskRegisterSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = ProjectRiskRegister
        fields = ['id', 'project', 'category', 'description', 'probability', 'impact', 'mitigation_plan', 'owner', 'owner_details', 'status']

    def validate_project(self, project):
        _validate_project_access(self, project)
        return project

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
        read_only_fields = ['access_code', 'created_at', 'host_organization', 'created_by']

    def validate(self, data):
        """
        Scale Check: Ensure host organization isn't exceeding their project limit.
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            host_org = request.user.organization if request.user else None
            
            if host_org and not host_org.can_create_project():
                plan = host_org.get_plan()
                raise serializers.ValidationError(
                    f"Organization '{host_org.name}' has reached the limit of {plan.max_projects} project(s) for the '{plan.name}' plan."
                )
        return data

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTransaction
        fields = '__all__'

class AuditTrailSerializer(serializers.ModelSerializer):
    auditor_details = UserSerializer(source='auditor', read_only=True)

    class Meta:
        model = AuditTrail
        fields = '__all__'

class ControlTestSerializer(serializers.ModelSerializer):
    tester_details = UserSerializer(source='tester', read_only=True)

    class Meta:
        model = ControlTest
        fields = '__all__'

class ComplianceRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceRequirement
        fields = '__all__'

class ComplianceEvidenceSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceEvidence
        fields = '__all__'

    def get_file_url(self, obj):
        return obj.document.url if obj.document else None
