# Generated by Django 3.0.5 on 2020-05-16 17:47

from django.db import migrations, models
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('pznsi', '0012_auto_20200514_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachments',
            name='attachment_creation_date',
            field=models.DateField(blank=True, default=django.utils.datetime_safe.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment_date',
            field=models.DateField(blank=True, default=django.utils.datetime_safe.datetime.now, null=True),
        ),
    ]