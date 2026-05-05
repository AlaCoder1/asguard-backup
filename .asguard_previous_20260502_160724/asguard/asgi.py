"""
ASGI config for asguard project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/

"""


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import os
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asguard.settings')
# application = get_asgi_application()
import django
django.setup()
from asguard.urls import websocket_urlpatterns
django_asgi_app = ASGIStaticFilesHandler(get_asgi_application())
application=ProtocolTypeRouter(
    {   'http': django_asgi_app,
        'websocket': AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
