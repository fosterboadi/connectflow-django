from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # User views
    path('', views.ticket_list, name='ticket_list'),
    path('chat/', views.chatbot, name='chatbot'),
    path('create/', views.ticket_create, name='ticket_create'),
    path('<uuid:pk>/', views.ticket_detail, name='ticket_detail'),

    # Platform Admin views
    path('platform/', views.platform_ticket_list, name='platform_ticket_list'),
    path('platform/<uuid:pk>/', views.platform_ticket_detail, name='platform_ticket_detail'),
]
