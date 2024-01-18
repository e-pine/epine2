from django.contrib import admin
from .models import *

admin.site.register(Room)
admin.site.register(RoomLowQuality)
admin.site.register(RoomRejected)
admin.site.register(Message)
admin.site.register(MessageLow)
admin.site.register(MessageRejected)
admin.site.register(UserProfileModel)
admin.site.register(ChatModel)
admin.site.register(ChatNotification)