# Generated by Django 2.2.28 on 2023-04-09 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0194_playerpairing_last_time_player_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerpairing',
            name='black_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='playerpairing',
            name='white_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
