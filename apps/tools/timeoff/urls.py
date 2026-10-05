from django.urls import path
from . import views

app_name = 'timeoff'

urlpatterns = [
    path('', views.leave_list, name='index'),
    path('request/', views.leave_request_create, name='request'),
    path('request/<uuid:pk>/edit/', views.leave_request_edit, name='edit'),
    path('request/<uuid:pk>/cancel/', views.leave_request_cancel, name='cancel'),
    path('request/<uuid:pk>/approve/<str:action>/', views.leave_approve, name='approve'),
]