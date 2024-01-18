from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(BroadcastNotification)
admin.site.register(FarmEvent)
admin.site.register(Events)
admin.site.register(FarmEventDetails)