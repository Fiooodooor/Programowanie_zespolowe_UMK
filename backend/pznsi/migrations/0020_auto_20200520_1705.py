# Generated by Django 3.0.5 on 2020-05-20 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pznsi', '0019_merge_20200519_2056'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repository',
            name='attachments',
        ),
        migrations.AddField(
            model_name='attachment',
            name='repository',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pznsi.Repository'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pznsi.Project'),
        ),
        migrations.AlterField(
            model_name='repository',
            name='repository_file_content',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='repository',
            name='repository_file_status',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]