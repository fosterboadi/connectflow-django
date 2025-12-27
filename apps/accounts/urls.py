from django.urls import path
from . import views, platform_admin_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('api/register/', views.RegisterAPIView.as_view(), name='register_api'),
    path('signup-organization/', views.OrganizationSignupView.as_view(), name='organization_signup'),
    path('api/create-organization/', views.CreateOrganizationView.as_view(), name='create_organization_api'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('api/sync-email-verification/', views.SyncEmailVerificationView.as_view(), name='sync_email_verification'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.ProfileSettingsView.as_view(), name='profile_settings'),
    path('profile/<str:pk>/', views.UserProfileView.as_view(), name='profile_detail'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('notifications/mark-read/', views.mark_notifications_as_read, name='mark_notifications_read'),
    path('setup/promote/', views.promote_me, name='promote_me'),
    path('global-search/', views.GlobalSearchView.as_view(), name='global_search'),
    
    # Platform Admin (Super Admin only)
    path('platform/dashboard/', platform_admin_views.platform_dashboard, name='platform_dashboard'),
    path('platform/organizations/', platform_admin_views.platform_org_list, name='platform_org_list'),
    path('platform/organizations/<uuid:pk>/toggle/', platform_admin_views.platform_toggle_org_status, name='platform_toggle_org_status'),
    path('platform/organizations/<uuid:pk>/subscription/', platform_admin_views.platform_manage_org_subscription, name='platform_manage_org_subscription'),
    path('platform/users/', platform_admin_views.platform_user_list, name='platform_user_list'),
    path('platform/users/<str:pk>/permissions/', platform_admin_views.platform_user_permissions, name='platform_user_permissions'),
    
    # Subscription Tiers
    path('platform/plans/', platform_admin_views.platform_plan_list, name='platform_plan_list'),
    path('platform/plans/create/', platform_admin_views.platform_plan_edit, name='platform_plan_create'),
    path('platform/plans/<uuid:pk>/edit/', platform_admin_views.platform_plan_edit, name='platform_plan_edit'),
    path('platform/plans/<uuid:pk>/delete/', platform_admin_views.platform_plan_delete, name='platform_plan_delete'),
]
