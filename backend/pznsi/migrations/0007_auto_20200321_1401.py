# Generated by Django 3.0.4 on 2020-03-21 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pznsi', '0006_auto_20200320_0019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_password',
            field=models.CharField(max_length=128),
        ),
    ]
