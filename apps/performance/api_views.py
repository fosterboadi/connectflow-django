from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    KPIMetric, KPIThreshold, KPIAssignment, 
    PerformanceReview, PerformanceScore, PerformanceAuditLog, Responsibility
)
from .serializers import (
    KPIMetricSerializer, KPIThresholdSerializer, KPIAssignmentSerializer, 
    PerformanceReviewSerializer, PerformanceScoreSerializer,
    PerformanceAuditLogSerializer, ResponsibilitySerializer
)

class PerformanceBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        # Ensure users only see data from their organization
        return self.queryset.filter(organization=self.request.user.organization)

class KPIMetricViewSet(PerformanceBaseViewSet):
    queryset = KPIMetric.objects.all()
    serializer_class = KPIMetricSerializer
    filterset_fields = ['metric_type', 'is_active', 'role', 'team']
    search_fields = ['name', 'description']

class KPIThresholdViewSet(PerformanceBaseViewSet):
    queryset = KPIThreshold.objects.all()
    serializer_class = KPIThresholdSerializer

    def get_queryset(self):
        return self.queryset.filter(metric__organization=self.request.user.organization)

class KPIAssignmentViewSet(viewsets.ModelViewSet):
    queryset = KPIAssignment.objects.all()
    serializer_class = KPIAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users see their own assignments, managers see all in org
        if self.request.user.role in ['SUPER_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(metric__organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)

class PerformanceReviewViewSet(PerformanceBaseViewSet):
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer
    filterset_fields = ['status', 'user', 'reviewer']
    
    def get_queryset(self):
        # Users see their own reviews, reviewers see reviews they conducted
        if self.request.user.role in ['SUPER_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)

class PerformanceScoreViewSet(viewsets.ModelViewSet):
    queryset = PerformanceScore.objects.all()
    serializer_class = PerformanceScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(review__organization=self.request.user.organization)

class PerformanceAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PerformanceAuditLog.objects.all()
    serializer_class = PerformanceAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

class ResponsibilityViewSet(PerformanceBaseViewSet):
    queryset = Responsibility.objects.all()
    serializer_class = ResponsibilitySerializer
    filterset_fields = ['status', 'user']
    
    def get_queryset(self):
        if self.request.user.role in ['SUPER_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)
