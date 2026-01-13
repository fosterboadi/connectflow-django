"""URL configuration for performance management."""

from django.urls import path
from . import views

app_name = 'performance'

urlpatterns = [
    # Manager Views - KPI Management
    path('kpi/metrics/', views.kpi_metric_list, name='kpi_metric_list'),
    path('kpi/metrics/create/', views.kpi_metric_create, name='kpi_metric_create'),
    path('kpi/assign/', views.assign_kpi, name='assign_kpi'),
    
    # Manager Views - Reviews
    path('team/overview/', views.team_performance_overview, name='team_overview'),
    path('reviews/pending/', views.pending_reviews_list, name='pending_reviews'),
    path('review/create/', views.create_review, name='create_review'),
    path('review/<uuid:review_id>/', views.review_detail, name='review_detail'),
    path('review/<uuid:review_id>/finalize/', views.finalize_review, name='finalize_review'),
    
    # Manager Views - Member Portfolio
    path('member/<uuid:user_id>/portfolio/', views.member_kpi_portfolio, name='member_portfolio'),
    
    # Manager Views - Score Management
    path('score/<uuid:score_id>/override/', views.override_score, name='override_score'),
    
    # Member Views
    path('my/dashboard/', views.my_kpi_dashboard, name='my_dashboard'),
    path('my/history/', views.my_performance_history, name='my_history'),
    path('my/review/<uuid:review_id>/', views.my_review_detail, name='my_review_detail'),
    
    # API Endpoints
    path('api/metrics/', views.api_kpi_metrics, name='api_metrics'),
    path('api/my-performance/', views.api_my_performance, name='api_my_performance'),
    path('api/team-performance/', views.api_team_performance, name='api_team_performance'),
]
