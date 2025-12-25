from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see others in their organization
        if self.request.user.is_authenticated:
            return User.objects.filter(organization=self.request.user.organization)
        return User.objects.none()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def toggle_theme(self, request):
        user = request.user
        user.theme = 'DARK' if user.theme == 'LIGHT' else 'LIGHT'
        user.save()
        return Response({'status': 'theme updated', 'theme': user.theme})
