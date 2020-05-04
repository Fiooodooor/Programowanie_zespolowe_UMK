from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    status = models.TextField(max_length=500, blank=True)
    organization = models.TextField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    user_activation_date = models.DateField(blank=True, null=True, verbose_name='activation date')
    user_deactivation_date = models.DateField(blank=True, null=True, verbose_name='deactivation date')


class Environment(models.Model):
    environment_name = models.CharField(max_length=100)
    environment_password = models.CharField(max_length=20)
    environment_creation_date = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Project(models.Model):
    project_name = models.CharField(blank=True, max_length=100)
    project_status = models.CharField(blank=True, max_length=100)
    project_password = models.CharField(max_length=128)
    project_creation_date = models.DateField(blank=True, null=True)
    project_closing_date = models.DateField(blank=True, null=True)
    project_content = models.CharField(blank=True, max_length=1000)
    project_category = models.CharField(blank=True, max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, null=True, blank=True)


class Comment(models.Model):
    comment_title = models.CharField(max_length=100)
    comment_content = models.CharField(max_length=2000)
    comment_date = models.DateField(blank=True, null=True)
    comment_reaction = models.CharField(max_length=50, default='none')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Attachments(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    attachment_content = models.CharField(max_length=2000)
    attachment_creation_date = models.DateField(blank=True, null=True)
    attachment_type = models.CharField(max_length=50)
    attachment_visible_date = models.DateField(blank=True, null=True)


class Votes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    vote_date = models.DateField(blank=True, null=True)
    vote_content = models.CharField(max_length=2000)


class Repository(models.Model):
    attachments = models.ForeignKey(Attachments, on_delete=models.CASCADE, null=True, blank=True)
    repository_file_content = models.CharField(max_length=2000)
    repository_file_date_created = models.DateField(blank=True, null=True)
    repository_file_status = models.CharField(max_length=100)
