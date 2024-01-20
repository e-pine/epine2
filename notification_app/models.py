from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from pine.models import Category

class FarmEvent(models.Model):
    event = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event

    
class BroadcastNotification(models.Model):
    name = models.ForeignKey(FarmEvent, on_delete=models.CASCADE, null=True)
    variety = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    # event = models.ManyToManyField(FarmEvent)
    broadcast_on = models.DateTimeField(null=True, blank=False)
    end_on = models.DateTimeField(null=True, blank=True)
    sent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Running')
    cost = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True) 
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name.event} - {self.status}"
    

    class Meta:
        ordering = ['-broadcast_on']

class FarmEventDetails(models.Model):
    broadcast_notification = models.ForeignKey(BroadcastNotification, on_delete=models.CASCADE, related_name='details')
    cost = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)

# class FarmEvent(models.Model):
#     event = models.CharField(max_length=50, blank=True, null=True)

#     def __str__(self):
#         return self.event
    
# class BroadcastNotification(models.Model):
#     message = models.ForeignKey(FarmEvent, on_delete=models.CASCADE, null=True)
#     broadcast_on = models.DateTimeField()
#     end_on = models.DateTimeField()
#     sent = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.message.event}"

#     class Meta:
#         ordering = ['-broadcast_on']

@receiver(post_save, sender=BroadcastNotification)
def notification_handler(sender, instance, created, **kwargs):
    # call group_send function directly to send notifications or you can create a dynamic task in celery beat
    if created:
        schedule, created = CrontabSchedule.objects.get_or_create(hour = instance.broadcast_on.hour, minute = instance.broadcast_on.minute, day_of_month = instance.broadcast_on.day, month_of_year = instance.broadcast_on.month)
        task = PeriodicTask.objects.create(crontab=schedule, name="broadcast-notification-"+str(instance.id), task="notification_app.tasks.broadcast_notification", args=json.dumps((instance.id,)))

class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tblevents"