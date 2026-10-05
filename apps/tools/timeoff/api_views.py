from rest_framework import viewsets, permissions, filters
from .models import LeaveType, LeaveRequest, LeaveBalance
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer, LeaveBalanceSerializer

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['SUPER_ADMIN', 'ORG_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(leave_type__organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role not in ['SUPER_ADMIN', 'DEPT_HEAD', 'ORG_ADMIN']:
            raise permissions.PermissionDenied(
                'Only authorized managers can update leave requests.'
            )
        serializer.save()

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['SUPER_ADMIN', 'ORG_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(leave_type__organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role not in ['SUPER_ADMIN', 'DEPT_HEAD', 'ORG_ADMIN']:
            raise permissions.PermissionDenied(
                'Only authorized managers can create leave balances.'
            )
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role not in ['SUPER_ADMIN', 'DEPT_HEAD', 'ORG_ADMIN']:
            raise permissions.PermissionDenied(
                'Only authorized managers can update leave balances.'
            )
        serializer.save()
