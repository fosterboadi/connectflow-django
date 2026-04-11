from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Organization, Department, Team, SharedProject, ProjectTask, 
    ProjectMilestone, ProjectFile, ProjectMeeting, ProjectRiskRegister,
    SubscriptionPlan, SubscriptionTransaction, AuditTrail, ControlTest,
    ComplianceRequirement, ComplianceEvidence
)
from .serializers import (
    OrganizationSerializer, DepartmentSerializer, TeamSerializer, SharedProjectSerializer,
    ProjectTaskSerializer, ProjectMilestoneSerializer, ProjectFileSerializer,
    ProjectMeetingSerializer, ProjectRiskRegisterSerializer, SubscriptionPlanSerializer,
    SubscriptionTransactionSerializer, AuditTrailSerializer, ControlTestSerializer,
    ComplianceRequirementSerializer, ComplianceEvidenceSerializer
)
from .permissions import HasSubscriptionFeature

class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(id=self.request.user.organization_id)

class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Department.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(department__organization=self.request.user.organization)

class SharedProjectViewSet(viewsets.ModelViewSet):
    serializer_class = SharedProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SharedProject.objects.filter(members=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, host_organization=self.request.user.organization)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, HasSubscriptionFeature('has_analytics')])
    def analytics(self, request, pk=None):
        project = self.get_object()
        # Scale-Ready: Return basic stats for the API
        data = {
            'member_count': project.members.count(),
            'channel_count': project.channels.count(),
            'file_count': project.files.count(),
            'task_count': project.tasks.count(),
        }
        return Response(data)

class ProjectTaskViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        return ProjectTask.objects.filter(project__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectMilestone.objects.filter(project__members=self.request.user)

class ProjectFileViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectFile.objects.filter(project__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

class ProjectMeetingViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectMeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectMeeting.objects.filter(project__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class ProjectRiskRegisterViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectRiskRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectRiskRegister.objects.filter(project__members=self.request.user)

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SubscriptionTransaction.objects.filter(organization=self.request.user.organization)

class AuditTrailViewSet(viewsets.ModelViewSet):
    serializer_class = AuditTrailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AuditTrail.objects.filter(project__members=self.request.user)

class ControlTestViewSet(viewsets.ModelViewSet):
    serializer_class = ControlTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ControlTest.objects.filter(project__members=self.request.user)

class ComplianceRequirementViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceRequirementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ComplianceRequirement.objects.filter(project__members=self.request.user)

class ComplianceEvidenceViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceEvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ComplianceEvidence.objects.filter(requirement__project__members=self.request.user)
