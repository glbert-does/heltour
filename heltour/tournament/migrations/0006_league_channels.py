# Generated by Django 4.2.20 on 2025-05-06 19:59

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0005_remove_registration_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaguechannel',
            name='type',
            field=models.CharField(choices=[('mod', 'Mods'), ('captains', 'Captains'), ('scheduling', 'Scheduling'), ('games', 'Games')], max_length=255),
        ),
    ]
