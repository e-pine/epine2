from django.urls import path, re_path

from .consumers import *

websocket_urlpatterns = [
    path("ws/realtime_updates/", RealtimeUpdatesConsumer.as_asgi()),
    re_path(r"ws/notification/(?P<room_name>\w+)/$", NotificationConsumer.as_asgi()),
]