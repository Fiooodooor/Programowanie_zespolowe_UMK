# Generated by Django 3.0.4 on 2020-04-29 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pznsi', '0008_auto_20200324_1936'),
    ]

    operations = [
        migrations.RenameField(
            model_name='environment',
            old_name='user',
            new_name='owner',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='user',
            new_name='owner',
        ),
    ]
