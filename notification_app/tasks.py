from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import BroadcastNotification
import json
from celery import Celery, states
from celery.exceptions import Ignore
import asyncio

@shared_task(bind=True)
def broadcast_notification(self, data):
    print(f"Received data: {data}")
    try:
        notification_id = int(data)
        notification = BroadcastNotification.objects.filter(id=notification_id).first()

        if notification:
            channel_layer = get_channel_layer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(channel_layer.group_send(
                "notification_broadcast",
                {
                    'type': 'send_notification',
                    'message': json.dumps(notification.name.event)
                }))
            notification.sent = True
            notification.save()
            return 'Done'
        else:
            self.update_state(
                state='FAILURE',
                meta={'exe': "Not Found"}
            )
            raise Ignore()
    except Exception as e:
        print(f"Exception: {e}")
        self.update_state(
            state='FAILURE',
            meta={
                'exe': "Failed"
            }
        )
        raise Ignore()
