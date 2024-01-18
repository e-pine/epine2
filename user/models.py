from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Phone(models.Model):
    phone_number = models.CharField(max_length=200, null=True)

ROLE_CHOICES = (
    ('buyer', 'Buyer'),
    ('employee', 'Employee'),
    ('supplier', 'Supplier'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    

    def __str__(self):
        return self.user.username