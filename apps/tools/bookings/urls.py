from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='index'),
    path('resource/add/', views.resource_create, name='resource_create'),
    path('resource/<uuid:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('resource/<uuid:pk>/delete/', views.resource_delete, name='resource_delete'),
    path('resource/<uuid:resource_id>/book/', views.booking_create, name='booking_create'),
    path('<uuid:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('<uuid:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<uuid:pk>/approve/<str:action>/', views.booking_approve, name='booking_approve'),
]