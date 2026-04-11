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
        serializer.save(organization=self.request.user.organization)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['start_time']

    def get_queryset(self):
        # Managers see all in org, users see their own
        if self.request.user.role in ['SUPER_ADMIN', 'DEPT_HEAD']:
            return self.queryset.filter(resource__organization=self.request.user.organization)
        return self.queryset.filter(user=self.request.user)
