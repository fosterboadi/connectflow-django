from django.urls import path, include
from rest_framework import routers
from apps.accounts.api_views import UserViewSet
from apps.organizations.api_views import OrganizationViewSet, DepartmentViewSet, TeamViewSet, SharedProjectViewSet
from apps.chat_channels.api_views import ChannelViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'projects', SharedProjectViewSet, basename='project')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
