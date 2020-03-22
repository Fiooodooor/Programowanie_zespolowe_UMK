from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    organization = models.TextField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
