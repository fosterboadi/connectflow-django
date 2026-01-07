from django.urls import path
from . import views

app_name = 'calls'

urlpatterns = [
    path('initiate/', views.initiate_call, name='initiate_call'),
    path('<uuid:call_id>/', views.call_room, name='call_room'),
    path('<uuid:call_id>/join/', views.join_call, name='join_call'),
    path('<uuid:call_id>/leave/', views.leave_call, name='leave_call'),
    path('<uuid:call_id>/end/', views.end_call, name='end_call'),
    path('<uuid:call_id>/reject/', views.reject_call, name='reject_call'),
    path('<uuid:call_id>/missed/', views.missed_call, name='missed_call'),
    path('<uuid:call_id>/status/', views.call_status, name='call_status'),
]
