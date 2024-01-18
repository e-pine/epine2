from django.db import models
from django.contrib.auth.models import User
from pine.models import Category

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    start_bid_price = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
    class Meta:
        ordering = ('date_added',)

class RoomLowQuality(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class MessageLow(models.Model):
    room = models.ForeignKey(RoomLowQuality, related_name='messages_low', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages_low', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
    class Meta:
        ordering = ('date_added',)

class RoomRejected(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class MessageRejected(models.Model):
    room = models.ForeignKey(RoomRejected, related_name='messages_rejected', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages_rejected', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
    class Meta:
        ordering = ('date_added',)
        
# personal chat
class UserProfileModel(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=100)
    online_status = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username
    
class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    link = models.URLField(null=True, blank=True)

    def __str__(self) -> str:
        return self.message
    
class ChatNotification(models.Model):
    chat = models.ForeignKey(to=ChatModel, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)


    def __str__ (self) -> str:
        return self.user.username 