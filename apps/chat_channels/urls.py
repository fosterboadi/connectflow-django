from django.urls import path
from . import views

app_name = 'chat_channels'

urlpatterns = [
    path('', views.channel_list, name='channel_list'),
    path('create/', views.channel_create, name='channel_create'),
    path('project/<uuid:project_id>/create/', views.project_channel_create, name='project_channel_create'),
    path('direct/<int:user_id>/', views.start_direct_message, name='start_direct_message'),
    path('<uuid:pk>/', views.channel_detail, name='channel_detail'),
    path('<uuid:pk>/edit/', views.channel_edit, name='channel_edit'),
    path('<uuid:pk>/delete/', views.channel_delete, name='channel_delete'),
    
    # Breakout rooms
    path('<uuid:channel_id>/breakout/create/', views.breakout_create, name='breakout_create'),
    path('breakout/<uuid:pk>/close/', views.breakout_close, name='breakout_close'),
    
    # Message actions
    path('message/<uuid:pk>/edit/', views.message_edit, name='message_edit'),
    path('message/<uuid:pk>/delete/', views.message_delete, name='message_delete'),
    path('message/<uuid:pk>/react/', views.message_react, name='message_react'),
    path('message/<uuid:pk>/thread/', views.message_thread, name='message_thread'),
    path('message/<uuid:pk>/reply/', views.message_reply, name='message_reply'),
    path('<uuid:pk>/pinned/', views.channel_pinned_messages, name='channel_pinned_messages'),
]
