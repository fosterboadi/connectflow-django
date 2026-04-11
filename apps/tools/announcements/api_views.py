from rest_framework import viewsets, permissions, filters
from .models import Announcement, AnnouncementReadReceipt
from .serializers import AnnouncementSerializer, AnnouncementReadReceiptSerializer

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'priority']

    def get_queryset(self):
        # Filtering for organization is done here
        return self.queryset.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )

class AnnouncementReadReceiptViewSet(viewsets.ModelViewSet):
    queryset = AnnouncementReadReceipt.objects.all()
    serializer_class = AnnouncementReadReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(announcement__organization=self.request.user.organization)
