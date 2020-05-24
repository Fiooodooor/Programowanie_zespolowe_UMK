# Generated by Django 3.0.5 on 2020-05-22 17:38

from django.db import migrations, models
import django.utils.datetime_safe
import pznsi.models


class Migration(migrations.Migration):

    dependencies = [
        ('pznsi', '0023_auto_20200521_1917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='project_closing_date',
        ),
        migrations.AddField(
            model_name='project',
            name='vote_closing',
            field=models.DateTimeField(default=pznsi.models.get_default_time),
        ),
        migrations.AddField(
            model_name='project',
            name='vote_starting',
            field=models.DateTimeField(default=django.utils.datetime_safe.datetime.now),
        ),
    ]
