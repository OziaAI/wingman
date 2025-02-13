"""
ASGI config for wingman project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from django.core.asgi import get_asgi_application

import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wingman.settings")

django_agsi_app = get_asgi_application()


ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
application = ProtocolTypeRouter(
    {
        "http": django_agsi_app,
        "websocket": OriginValidator(
            AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns)),
            [ALLOWED_ORIGIN],
        ),
    }
)
