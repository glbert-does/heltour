# Generated by Django 2.2.13 on 2021-04-18 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0189_auto_20210221_0424'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='agreed_to_tos',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='consent_to_publish_lichess_username',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='consent_to_share_email_with_slack',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
