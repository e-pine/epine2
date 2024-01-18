from notification_app.models import BroadcastNotification
from chat.models import *
def notifications(request):
    allnotifications = BroadcastNotification.objects.all()
    return {'notifications': allnotifications}

def messagerooms(request):
    allrooms = Room.objects.all()
    return{'messagerooms': allrooms}
