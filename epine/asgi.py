import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epine.settings')
django.setup()

from channels.auth import AuthMiddlewareStack
from notification_app.routing import websocket_urlpatterns as notification_websocket_urlpatterns
from chat.routing import websocket_urlpatterns as epine_websocket_urlpatterns

# Combine the URL patterns from both apps
websocket_urlpatterns = notification_websocket_urlpatterns + epine_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})
