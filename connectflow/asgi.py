"""
ASGI config for connectflow project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.chat_channels.routing import websocket_urlpatterns as chat_urlpatterns
from apps.accounts.routing import websocket_urlpatterns as notification_urlpatterns

# Auto-detect environment
if os.environ.get('RENDER'):  # Render.com
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_render')
elif os.environ.get('WEBSITE_SITE_NAME'):  # Azure App Service
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_azure')
elif os.environ.get('RAILWAY_ENVIRONMENT'):  # Railway
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings_prod')
else:  # Local development
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_urlpatterns + notification_urlpatterns
        )
    ),
})
