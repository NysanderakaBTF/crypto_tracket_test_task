"""
ASGI config for crypto_tracker project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import django
from django.core.asgi import get_asgi_application

from prices.urls import urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_tracker.settings')
djangp_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": djangp_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(urlpatterns))
        ),
    }
)