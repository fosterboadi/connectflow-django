from rest_framework import viewsets, permissions
from .models import Organization, Department, Team, SharedProject
from .serializers import OrganizationSerializer, DepartmentSerializer, TeamSerializer, SharedProjectSerializer

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
