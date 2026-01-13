"""URL configuration for forms management."""

from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    # Form Management
    path('', views.form_list, name='form_list'),
    path('create/', views.form_create, name='form_create'),
    path('<uuid:form_id>/edit/', views.form_edit, name='form_edit'),
    path('<uuid:form_id>/responses/', views.form_responses, name='form_responses'),
    path('<uuid:form_id>/analytics/', views.form_analytics, name='form_analytics'),
    path('<uuid:form_id>/export/', views.form_export_csv, name='form_export'),
    path('<uuid:form_id>/delete/', views.form_delete, name='form_delete'),
    
    # AJAX endpoints for field management
    path('<uuid:form_id>/field/add/', views.form_field_add, name='form_field_add'),
    path('<uuid:form_id>/field/<uuid:field_id>/update/', views.form_field_update, name='form_field_update'),
    path('<uuid:form_id>/field/<uuid:field_id>/delete/', views.form_field_delete, name='form_field_delete'),
]
