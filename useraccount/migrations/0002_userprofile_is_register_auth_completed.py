# Generated by Django 4.2 on 2023-04-12 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('useraccount', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_register_auth_completed',
            field=models.BooleanField(default=False, verbose_name='Register Authenticated is complete '),
        ),
    ]
