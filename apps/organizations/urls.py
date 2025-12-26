from django.urls import path
from . import views, billing_views

app_name = 'organizations'

urlpatterns = [
    # Overview
    path('', views.organization_overview, name='overview'),
    path('settings/', views.organization_settings, name='organization_settings'),
    
    # Billing
    path('billing/plans/', billing_views.billing_select_plan, name='billing_select_plan'),
    path('billing/paystack/<uuid:plan_id>/', billing_views.paystack_checkout, name='paystack_checkout'),
    path('billing/success/', billing_views.billing_success, name='billing_success'),
    path('webhooks/paystack/', billing_views.paystack_webhook, name='paystack_webhook'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<uuid:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<uuid:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Teams
    path('teams/', views.team_list, name='team_list'),
    path('departments/<uuid:department_pk>/teams/', views.team_list, name='team_list_by_dept'),
    path('departments/<uuid:department_pk>/teams/create/', views.team_create, name='team_create'),
    path('teams/<uuid:pk>/edit/', views.team_edit, name='team_edit'),
    path('teams/<uuid:pk>/delete/', views.team_delete, name='team_delete'),
    
    # Members
    path('invite/', views.invite_member, name='invite_member'),
    path('members/', views.member_directory, name='member_directory'),
    path('members/<str:pk>/remove/', views.member_remove, name='member_remove'),
    
    # Shared Projects
    path('projects/', views.shared_project_list, name='shared_project_list'),
    path('projects/create/', views.shared_project_create, name='shared_project_create'),
    path('projects/join/', views.shared_project_join, name='shared_project_join'),
    path('projects/<uuid:pk>/', views.shared_project_detail, name='shared_project_detail'),
    path('projects/<uuid:pk>/delete/', views.shared_project_delete, name='shared_project_delete'),
    path('projects/<uuid:pk>/files/', views.project_files, name='project_files'),
    path('projects/<uuid:project_pk>/files/<uuid:file_pk>/delete/', views.project_file_delete, name='project_file_delete'),
    path('projects/<uuid:pk>/meetings/', views.project_meetings, name='project_meetings'),
    path('projects/<uuid:pk>/tasks/', views.project_tasks, name='project_tasks'),
    path('projects/<uuid:project_pk>/tasks/<uuid:task_pk>/edit/', views.project_task_edit, name='project_task_edit'),
    path('projects/<uuid:project_pk>/tasks/<uuid:task_pk>/delete/', views.project_task_delete, name='project_task_delete'),
    path('projects/<uuid:pk>/analytics/', views.project_analytics, name='project_analytics'),
    path('projects/<uuid:pk>/milestones/', views.project_milestones, name='project_milestones'),
    path('projects/<uuid:project_pk>/milestones/<uuid:milestone_pk>/edit/', views.project_milestone_edit, name='project_milestone_edit'),
    path('projects/<uuid:project_pk>/milestones/<uuid:milestone_pk>/delete/', views.project_milestone_delete, name='project_milestone_delete'),
    path('projects/<uuid:project_pk>/members/<int:member_pk>/remove/', views.shared_project_remove_member, name='shared_project_remove_member'),
    path('milestones/<uuid:pk>/toggle/', views.toggle_milestone, name='toggle_milestone'),
]
