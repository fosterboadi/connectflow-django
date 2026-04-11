from rest_framework import viewsets, permissions, filters
from apps.chat_channels.models import Call, CallParticipant
from .serializers import CallSerializer, CallParticipantSerializer

class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Users see calls they initiated or are participants in
        return self.queryset.filter(
            participants=self.request.user
        ).distinct()

class CallParticipantViewSet(viewsets.ModelViewSet):
    queryset = CallParticipant.objects.all()
    serializer_class = CallParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Participants can see their own status and others in the same calls
        return self.queryset.filter(
            call__participants=self.request.user
        ).distinct()
