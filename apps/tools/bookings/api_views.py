from rest_framework import viewsets, permissions, filters
from .models import Resource, Booking
from .serializers import ResourceSerializer, BookingSerializer

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        if not (self.request.user.is_admin or self.request.user.role == 'SUPER_ADMIN'):
            raise permissions.PermissionDenied('Only organization administrators can manage resources.')
        serializer.save(organization=self.request.user.organization)

    def perform_update(self, serializer):
        if not (self.request.user.is_admin or self.request.user.role == 'SUPER_ADMIN'):
            raise permissions.PermissionDenied('Only organization administrators can manage resources.')
        serializer.save()

    def perform_destroy(self, instance):
        if not (self.request.user.is_admin or self.request.user.role == 'SUPER_ADMIN'):
            raise permissions.PermissionDenied('Only organization administrators can manage resources.')
        instance.delete()

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['start_time']

    def get_queryset(self):
        # Managers see all in org, users see their own
        if self.request.user.role in ['SUPER_ADMIN', 'ORG_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(resource__organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        resource = serializer.validated_data['resource']
        if resource.organization_id != self.request.user.organization_id:
            raise permissions.PermissionDenied('This resource is outside your organization.')
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if not (self.request.user.is_admin or self.request.user.role in ['SUPER_ADMIN', 'DEPT_HEAD']):
            raise permissions.PermissionDenied(
                'Only authorized managers can update bookings.'
            )
        serializer.save()
