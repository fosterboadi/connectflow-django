from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Notification
from .serializers import UserSerializer, NotificationSerializer

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_login(request):
    """
    Login endpoint for Postman/API testing
    POST /api/v1/login/
    Body: {"email": "user@example.com", "password": "password"}
    Returns: {"token": "abc123...", "user": {...}}
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    
    if user is None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Set user ONLINE on API login
    user.status = User.Status.ONLINE
    user.last_seen = timezone.now()
    user.save(update_fields=['status', 'last_seen'])
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    
    # Return token and user data
    serializer = UserSerializer(user)
    return Response({
        'token': token.key,
        'user': serializer.data
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_logout(request):
    """
    Logout endpoint - deletes the user's token
    POST /api/v1/logout/
    """
    # Set user OFFLINE on logout
    request.user.status = User.Status.OFFLINE
    request.user.last_seen = timezone.now()
    request.user.save(update_fields=['status', 'last_seen'])
    
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})
    except:
        return Response({'message': 'Logged out'})

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

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all notifications marked as read'})
