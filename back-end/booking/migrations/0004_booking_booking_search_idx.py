# Generated by Django 5.2 on 2025-05-15 12:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_remove_roomstatus_room_booking_code_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['room', 'booking_status', 'check_in_date', 'check_out_date'], name='booking_search_idx'),
        ),
    ]
