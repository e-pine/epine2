from django.urls import path
from .import consumers

websocket_urlpatterns = [
    path('ws/high-quality/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/low_quality/<str:room_name>/', consumers.ChatConsumerLowQuality.as_asgi()),
    path('ws/rejected/<str:room_name>/', consumers.ChatConsumerRejected.as_asgi()),

    path('ws/<int:id>/', consumers.PersonalChatConsumer.as_asgi()),
    path('ws/notify/', consumers.NotificationConsumer.as_asgi()),
    # path('ws/<str:dashboard_slug>/', consumers.DashboardConsumer.as_asgi())
]
