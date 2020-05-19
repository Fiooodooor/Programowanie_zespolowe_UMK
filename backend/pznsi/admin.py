from django.contrib import admin
from .models import User, Environment, Project, Comment, ProjectCategory

admin.site.register(User)
admin.site.register(Environment)
admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(ProjectCategory)