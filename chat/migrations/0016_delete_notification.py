# Generated by Django 4.2.7 on 2023-12-27 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0015_notification'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
