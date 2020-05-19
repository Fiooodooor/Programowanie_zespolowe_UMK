import base64

from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Value, IntegerField, Case, When
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user, get_users_with_perms, get_perms
from guardian.utils import get_anonymous_user
from rest_framework import permissions, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from pznsi.models import User, Environment, Project, Comment, Attachment, Vote, ProjectCategory
from pznsi.serializers import EnvironmentSerializer, ProjectDetailSerializer


def remove_environment_view(environment, user):
    user_projects = get_objects_for_user(user, 'view_project_instance', environment.project_set)
    if not user_projects and not user.has_perm('edit_environment_instance', environment):
        group = Group.objects.get(name=f'{environment.id}_environment_viewers')
        user.groups.remove(group)
        return True
    else:
        return False


class Environments(mixins.ListModelMixin, viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = get_objects_for_user(self.request.user, 'view_environment_instance', super().get_queryset())
        return qs

    @action(detail=True, methods=['post'])
    def add_permissions(self, request, pk=None):
        environment = self.get_object()
        if request.user == environment.owner:
            user_id = int(request.data['user_id'])
            editor_group_name = f'{str(environment.id)}_environment_editors'
            viewer_group_name = f'{str(environment.id)}_environment_viewers'
            editor_group = Group.objects.get(name=editor_group_name)
            viewer_group = Group.objects.get(name=viewer_group_name)
            try:
                user = User.objects.get(id=user_id)
                user.groups.add(editor_group)
                user.groups.add(viewer_group)
                return Response({'result': '1'})
            except ObjectDoesNotExist:
                return Response({'result': '0',
                                 'detail': 'User does not exist'}, status.HTTP_400_BAD_REQUEST)
        else:
            raise PermissionDenied({"message": "You don't have permission to edit",
                                    "object_id": environment.id})

    @action(detail=True, methods=['post'])
    def remove_permissions(self, request, pk=None):
        environment = self.get_object()
        if request.user == environment.owner:
            user_id = int(request.data['user_id'])
            editor_group_name = f'{str(environment.id)}_environment_editors'
            editor_group = Group.objects.get(name=editor_group_name)
            try:
                user = User.objects.get(id=user_id)
                user.groups.remove(editor_group)
                remove_environment_view(environment, user)
                return Response({'result': '1'})
            except ObjectDoesNotExist:
                return Response({'result': '0',
                                 'detail': 'User does not exist'}, status.HTTP_400_BAD_REQUEST)
        else:
            raise PermissionDenied({"message": "You don't have permission to edit",
                                    "object_id": environment.id})


class Projects(mixins.CreateModelMixin,
               mixins.ListModelMixin,
               mixins.RetrieveModelMixin,
               viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = get_objects_for_user(self.request.user, 'view_project_instance', super().get_queryset())
        return qs

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        project = self.get_object()
        if request.user.has_perm('view_project_instance', project):
            try:
                comment_title = request.data['title']
            except KeyError:
                comment_title = None
            comment_text = request.data['comment']
            Comment.objects.create(comment_title=comment_title, comment_content=comment_text, project=project,
                                   user=self.request.user)
            return Response({'result': '1',
                             'detail': 'Added successfully'})
        else:
            raise PermissionDenied({"message": "No permission to add comment",
                                    "object_id": project.id})

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        project = self.get_object()
        if request.user.has_perm('view_project_instance', project):
            base64_file = request.data['file']
            if base64_file != '':
                format, imgstr = base64_file.split(';base64,')
                ext = format.split('/')[-1]
                file = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                Attachment.objects.create(project=project, user=request.user, content=file)
                return Response({'result': '1',
                                 'detail': 'Added successfully'})
            else:
                raise Http404
        else:
            raise PermissionDenied({"message": "No permission to add file",
                                    "object_id": project.id})

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        project = self.get_object()
        if request.user.has_perm('vote', project):
            rate = int(request.data['rate'])
            vote, created = Vote.objects.get_or_create(user=request.user, project=project)
            vote.vote_content = rate
            vote.save()
            if created:
                return Response({'result': '1',
                                 'detail': 'Vote added successfully'})
            else:
                return Response({'result': '1',
                                 'detail': 'Vote updated successfully'})  # TODO change date
        else:
            raise PermissionDenied({"message": "No permission to vote",
                                    "object_id": project.id})

    @action(detail=True, methods=['post'])
    def add_permissions(self, request, pk=None):
        project = self.get_object()
        project_voters = Group.objects.get(name=f'{project.id}_project_voters')
        project_editors = Group.objects.get(name=f'{project.id}_project_editors')
        project_viewers = Group.objects.get(name=f'{project.id}_project_viewers')
        if request.user == project.owner:
            user_id = int(request.data['user_id'])
            permissions = set(request.data['permissions'])
            user = User.objects.get(id=user_id)
            allowed_permissions = {'vote', 'edit_project_instance', 'view_project_instance'}
            if permissions.issubset(allowed_permissions):
                for permission in permissions:
                    if permission == 'vote':
                        user.groups.add(project_voters)
                    elif permission == 'edit_project_instance':
                        user.groups.add(project_editors)
                    elif permission == 'view_project_instance':
                        user.groups.add(project_viewers)
                return Response({'result': 1,
                                 'detail': 'Successfully added permissions'})
            else:
                return Response({'result': 0,
                                 'detail': 'Provided wrong permissions'}, status.HTTP_400_BAD_REQUEST)

        else:
            raise PermissionDenied({"message": "Unable to change user permissions",
                                    "object_id": project.id})

    @action(detail=True, methods=['post'])
    def remove_permissions(self, request, pk=None):
        project = self.get_object()
        project_voters = Group.objects.get(name=f'{project.id}_project_voters')
        project_editors = Group.objects.get(name=f'{project.id}_project_editors')
        project_viewers = Group.objects.get(name=f'{project.id}_project_viewers')
        if request.user == project.owner:
            user_id = int(request.data['user_id'])
            permissions = set(request.data['permissions'])
            user = User.objects.get(id=user_id)
            allowed_permissions = {'vote', 'edit_project_instance', 'view_project_instance'}
            if permissions.issubset(allowed_permissions):
                for permission in permissions:
                    if permission == 'vote':
                        user.groups.remove(project_voters)
                    elif permission == 'edit_project_instance':
                        user.groups.remove(project_editors)
                    elif permission == 'view_project_instance':
                        user.groups.remove(project_viewers)
                        environment = project.environment
                        remove_environment_view(environment, user)
                return Response({'result': 1,
                                 'detail': 'Successfully added permissions'})
            else:
                return Response({'result': 0,
                                 'detail': 'Provided wrong permissions'}, status.HTTP_400_BAD_REQUEST)

        else:
            raise PermissionDenied({"message": "Unable to change user permissions",
                                    "object_id": project.id})


def workspace(request):
    return render(request, 'pznsi/logged/workspace/workspace.html')


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main'))
    else:
        return HttpResponseRedirect(reverse('login'))


def main_page(request):
    if request.user.is_authenticated:
        return render(request, 'pznsi/logged/MainPage.html')
    else:
        return render(request, 'pznsi/anonymous/MainPage.html')


# TODO clean this up a bit
def edit_profile(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'pznsi/logged/accounts/EditUserProfile.html')
        elif request.method == 'POST':
            new_email = request.POST.get('email')
            new_password = request.POST.get('password')
            new_firstname = request.POST.get('imie')
            new_lastname = request.POST.get('nazwisko')
            new_organization = request.POST.get('organizacja')
            avatar_base64 = request.POST.get('avatar')
            db_user = User.objects.get(id=user.id)

            # TODO change to actual password requirements once we have them
            if new_password != '':
                db_user.set_password(new_password)
            if avatar_base64 != '':
                format, imgstr = avatar_base64.split(';base64,')
                ext = format.split('/')[-1]
                new_avatar = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                db_user.avatar = new_avatar

            db_user.email = new_email
            db_user.first_name = new_firstname
            db_user.last_name = new_lastname
            db_user.organization = new_organization
            db_user.save()
            return HttpResponseRedirect(reverse('edit_profile'))
    else:
        raise Http404


def register(request):
    if request.method == 'GET':
        return render(request, 'pznsi/anonymous/Registration.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return HttpResponseRedirect(reverse('edit_profile'))
        elif password != repassword:
            return HttpResponseRedirect(reverse('edit_profile'))
        else:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('main'))


def front_environments(request):
    if request.method == 'POST':
        page = int(request.POST.get('page'))
        keyword = request.POST.get('keyword')

        all_environment_list = get_objects_for_user(request.user, 'view_environment_instance', Environment)
        environment_list = all_environment_list[(page - 1) * 12:page * 12].annotate(
            isOwner=Case(
                When(owner=request.user.id, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ))
        context = {
            'page': page,
            'keyword': keyword,
            'environments': environment_list
        }
        return render(request, 'pznsi/logged/workspace/environments.html', context)
    else:
        raise Http404


def front_projects(request):
    if request.method == 'POST':
        environment = int(request.POST.get('numEnvi'))
        page = int(request.POST.get('page'))
        keyword = request.POST.get('keyword')
        id_project = request.POST.get('id_project', None)
        user_projects = get_objects_for_user(request.user, 'view_project_instance', Project)
        if id_project is not None:
            id_project = int(id_project)
            project_list = user_projects.filter(id=id_project).annotate(
                isOwner=Case(
                    When(owner=request.user.id, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        elif environment == 0:
            project_list = user_projects[(page - 1) * 12:page * 12].annotate(
                isOwner=Case(
                    When(owner=request.user.id, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        else:
            project_list = user_projects.filter(environment=environment)[(page - 1) * 12:page * 12].annotate(
                isOwner=Case(
                    When(owner=request.user.id, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        context = {
            'page': page,
            'keyword': keyword,
            'projects': project_list
        }
        return render(request, 'pznsi/logged/workspace/projects.html', context)
    else:
        raise Http404


def edit_environment(request):
    if request.method == 'POST' and request.user.has_perm('pznsi.'):
        requested_environment = int(request.POST.get('numEnvi'))
        environment = None
        if requested_environment != 0:
            environment = Environment.objects.get(id=requested_environment)
            if request.user.has_perm('edit_environment_instance', environment):
                mode = 0
            else:
                raise Http404
        else:
            if request.user.has_perm('pznsi.can_add_environment'):
                mode = 1
            else:
                raise Http404
        users = User.objects.all().exclude(id=get_anonymous_user().id)
        context = {
            'environment': environment,
            'users': users,
            'mode': mode
        }
        return render(request, 'pznsi/logged/workspace/edit_environment.html', context)
    else:
        raise Http404


def save_environment(request):
    if request.method == 'POST':
        requested_environment = int(request.POST.get('numEnvi'))
        requested_environment_name = request.POST.get('environment_name')
        image_base64 = request.POST.get('cover_image')
        requested_owner = int(request.POST.get('owner'))
        if requested_environment != 0:
            environment = Environment.objects.get(id=requested_environment)
            if request.user.has_perm('edit_environment_instance', environment):
                environment.environment_name = requested_environment_name
                environment.owner = User.objects.get(id=requested_owner)
            else:
                raise Http404
        else:
            if request.user.has_perm('pznsi.can_add_environment'):
                environment = Environment.objects.create(environment_name=requested_environment_name,
                                                         owner=User.objects.get(id=requested_owner))
            else:
                raise Http404
        if image_base64 != '':
            format, imgstr = image_base64.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            environment.cover_image = image
        environment.save()
        return JsonResponse({"result": 1})
    else:
        raise Http404


def save_project(request):
    if request.method == 'POST':
        requested_project = int(request.POST.get('project_id'))
        requested_project_name = request.POST.get('project_name')
        requested_project_category = request.POST.get('project_category')
        requested_project_desc = request.POST.get('project_description')
        image_base64 = request.POST.get('cover_image')
        requested_owner = int(request.POST.get('owner'))
        environment_id = int(request.POST.get('environment_id'))
        if requested_project != 0:
            project = Project.objects.get(id=requested_project)
            if request.user.has_perm('edit_project_instance', project):
                project.project_name = requested_project_name
                project.owner = User.objects.get(id=requested_owner)
                project.project_content = requested_project_desc
            else:
                raise Http404
        else:
            if request.user.has_perm('edit_environment_instance', Environment.objects.get(id=environment_id)):
                project = Project.objects.create(project_name=requested_project_name,
                                                 owner=User.objects.get(id=requested_owner),
                                                 project_category=ProjectCategory.objects.get(
                                                     id=requested_project_category),
                                                 project_content=requested_project_desc,
                                                 environment=Environment.objects.get(id=environment_id))
            else:
                raise Http404
        if image_base64 != '':
            format, imgstr = image_base64.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            project.cover_image = image
        project.save()
        return JsonResponse({"project_name": requested_project_name, "project_category": requested_project_category,
                             "project_content": requested_project_desc})
    else:
        raise Http404


def edit_project(request):
    if request.method == 'POST':
        requested_project = int(request.POST.get('id'))
        project = None
        if requested_project != 0:
            project = Project.objects.get(id=requested_project)
            if request.user.has_perm('edit_project_instance', project):
                mode = 0
            else:
                raise Http404
        else:
            mode = 1
        users = User.objects.all().exclude(id=get_anonymous_user().id)
        context = {
            'project': project,
            'users': users,
            'mode': mode,
            'project_id': requested_project
        }
        return render(request, 'pznsi/logged/workspace/edit_project.html', context)
    else:
        raise Http404


def can_add_envi(request):
    if request.method == 'POST':
        if request.user.has_perm('pznsi.can_add_environment'):
            can_add = True
        else:
            can_add = False
        return JsonResponse({"can_add": can_add})
    else:
        raise Http404


def can_add_project(request):
    if request.method == 'POST':
        requested_environment = int(request.POST.get('id'))
        environment = Environment.objects.get(id=requested_environment)
        if environment.owner == request.user or request.user.has_perm('edit_environment_instance', environment):
            can_add = True
        else:
            can_add = False
        return JsonResponse({"can_add": can_add})
    else:
        raise Http404


def PermEnviroment(request):
    if request.method == 'POST':
        environment_id = int(request.POST.get('environment_id'))
        environment = Environment.objects.get(id=environment_id)
        users = User.objects.all().exclude(id=get_anonymous_user().id)
        permitted_users = get_users_with_perms(environment, attach_perms=True)
        context = {
            'users': users,
            'permitted_users': permitted_users
        }
        return render(request, 'pznsi/logged/workspace/perm_environment.html', context)
    else:
        raise Http404


def permProject(request):
    if request.method == 'POST':
        project_id = int(request.POST.get('project_id'))
        project = Project.objects.get(id=project_id)
        users = User.objects.all().exclude(id=get_anonymous_user().id)
        permitted_users = get_users_with_perms(project, attach_perms=True)
        context = {
            'users': users,
            'permitted_users': permitted_users
        }
        return render(request, 'pznsi/logged/workspace/perm_project.html', context)
    else:
        raise Http404


def project(request):
    if request.method == 'POST':
        project_id = int(request.POST.get('project_id'))
        project = Project.objects.get(id=project_id)
        user_permissions = get_perms(request.user, project)
        context = {
            'project': project,
            'permissions': user_permissions
        }
        return render(request, 'pznsi/logged/workspace/project.html', context)
    else:
        raise Http404
