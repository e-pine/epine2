# Generated by Django 4.2.4 on 2023-11-26 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_room_date_added'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomLowQuality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
