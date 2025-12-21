from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Overview
    path('', views.organization_overview, name='overview'),
    
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
    
    # Shared Projects
    path('projects/', views.shared_project_list, name='shared_project_list'),
    path('projects/create/', views.shared_project_create, name='shared_project_create'),
    path('projects/join/', views.shared_project_join, name='shared_project_join'),
    path('projects/<uuid:pk>/', views.shared_project_detail, name='shared_project_detail'),
    path('projects/<uuid:pk>/files/', views.project_files, name='project_files'),
    path('projects/<uuid:pk>/meetings/', views.project_meetings, name='project_meetings'),
    path('projects/<uuid:pk>/tasks/', views.project_tasks, name='project_tasks'),
    path('projects/<uuid:pk>/analytics/', views.project_analytics, name='project_analytics'),
    path('projects/<uuid:pk>/milestones/', views.project_milestones, name='project_milestones'),
    path('milestones/<uuid:pk>/toggle/', views.toggle_milestone, name='toggle_milestone'),
]
