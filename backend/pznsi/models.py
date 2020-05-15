from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, get_objects_for_user


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
    cover_image = models.ImageField(upload_to='environment_covers', blank=True, null=True)

    class Meta:
        permissions = (
            ('view_environment_instance', 'view environment instance'),
            ('edit_environment_instance', 'edit environment instance')
        )

    def __str__(self):
        return f'{self.environment_name} ({self.id})'

    def get_projects(self, user):
        return get_objects_for_user(user, 'view_project_instance', self.project_set)


class ProjectCategory(models.Model):
    category_name = models.CharField(blank=True, max_length=100)


class Project(models.Model):
    project_name = models.CharField(blank=True, max_length=100)
    project_status = models.CharField(blank=True, max_length=100)
    project_password = models.CharField(max_length=128)
    project_creation_date = models.DateField(blank=True, null=True)
    project_closing_date = models.DateField(blank=True, null=True)
    project_content = models.CharField(blank=True, max_length=1000)
    project_category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, null=True, blank=True)
    cover_image = models.ImageField(upload_to='project_covers', blank=True, null=True)

    class Meta:
        permissions = (
            ('view_project_instance', 'view project instance'),
            ('edit_project_instance', 'edit project instance'),
            ('vote', 'vote'),
        )

    def __str__(self):
        return f'{self.project_name} ({self.id})'


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


@receiver(post_save, sender=Project)
def project_post_save(sender, **kwargs):
    """
    Creates groups that have set permissions for project instance
    """
    project, created = kwargs["instance"], kwargs["created"]
    if created:
        name_prefix = str(project.id) + '_project_'
        viewers_name = name_prefix + 'viewers'
        voters_name = name_prefix + 'voters'
        editors_name = name_prefix + 'editors'
        viewers, _ = Group.objects.get_or_create(name=viewers_name)
        editors, _ = Group.objects.get_or_create(name=editors_name)
        voters, _ = Group.objects.get_or_create(name=voters_name)
        assign_perm('view_project_instance', viewers, project)
        assign_perm('edit_project_instance', editors, project)
        assign_perm('vote', voters, project)
        if project.owner is not None:
            project.owner.groups.add(viewers)
            project.owner.groups.add(editors)
            project.owner.groups.add(voters)  # TODO should owner be able to vote?


@receiver(post_save, sender=Environment)
def environment_post_save(sender, **kwargs):
    """
    Creates groups that have set permissions for environment instance
    """
    environment, created = kwargs["instance"], kwargs["created"]
    if created:
        name_prefix = str(environment.id) + '_environment_'
        viewers_name = name_prefix + 'viewers'
        editors_name = name_prefix + 'editors'
        viewers, _ = Group.objects.get_or_create(name=viewers_name)
        editors, _ = Group.objects.get_or_create(name=editors_name)
        assign_perm('view_environment_instance', viewers, environment)
        assign_perm('edit_environment_instance', editors, environment)
        if environment.owner is not None:
            environment.owner.groups.add(viewers)
            environment.owner.groups.add(editors)
