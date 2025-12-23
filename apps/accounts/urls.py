from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('signup-organization/', views.OrganizationSignupView.as_view(), name='organization_signup'),
    path('api/create-organization/', views.CreateOrganizationView.as_view(), name='create_organization_api'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.ProfileSettingsView.as_view(), name='profile_settings'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('notifications/mark-read/', views.mark_notifications_as_read, name='mark_notifications_read'),
]
