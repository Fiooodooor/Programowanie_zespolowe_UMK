# Generated by Django 3.0.4 on 2020-03-19 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pznsi', '0005_auto_20200320_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_activation_date',
            field=models.DateField(blank=True, null=True, verbose_name='activation date'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_deactivation_date',
            field=models.DateField(blank=True, null=True, verbose_name='deactivation date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_category',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_content',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_status',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]