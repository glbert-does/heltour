# Generated by Django 4.2.9 on 2024-12-21 23:00

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0004_start_games_automatically'),
    ]

    operations = [
        migrations.AddField(
            model_name='playersetting',
            name='zen_mode',
            field=models.BooleanField(default=False),
        ),
   ]
