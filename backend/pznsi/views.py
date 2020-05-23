import base64
from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import Value, IntegerField, Case, When
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils.datetime_safe import datetime
from guardian.shortcuts import get_objects_for_user, get_users_with_perms, get_perms
from guardian.utils import get_anonymous_user
from rest_framework import permissions, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from pznsi.models import User, Environment, Project, Comment, Attachment, Vote, ProjectCategory, RepositoryFile
from pznsi.serializers import EnvironmentSerializer, ProjectDetailSerializer, RepositorySerializer


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
            permissions = set(request.data['permissions'])
            allowed_permissions = {'edit_environment_instance', 'view_environment_instance'}
            editor_group = Group.objects.get(name=editor_group_name)
            viewer_group = Group.objects.get(name=viewer_group_name)
            try:
                user = User.objects.get(id=user_id)
                if permissions.issubset(allowed_permissions):
                    for permission in permissions:
                        if permission == 'edit_environment_instance':
                            user.groups.add(editor_group)
                        elif permission == 'view_environment_instance':
                            user.groups.add(viewer_group)
                    return Response({'result': 1,
                                     'detail': 'Successfully added permissions'})
                else:
                    return Response({'result': 0,
                                     'detail': 'Provided wrong permissions'}, status.HTTP_400_BAD_REQUEST)
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
            viewer_group_name = f'{str(environment.id)}_environment_viewers'
            permissions = set(request.data['permissions'])
            allowed_permissions = {'edit_environment_instance', 'view_environment_instance'}
            editor_group = Group.objects.get(name=editor_group_name)
            viewer_group = Group.objects.get(name=viewer_group_name)
            try:
                user = User.objects.get(id=user_id)
                if permissions.issubset(allowed_permissions):
                    for permission in permissions:
                        if permission == 'edit_environment_instance':
                            user.groups.remove(editor_group)
                        elif permission == 'view_environment_instance':
                            user.groups.remove(viewer_group)
                    return Response({'result': 1,
                                     'detail': 'Successfully removed permissions'})
                else:
                    return Response({'result': 0,
                                     'detail': 'Provided wrong permissions'}, status.HTTP_400_BAD_REQUEST)
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
        environments = get_objects_for_user(self.request.user, 'view_environment_instance', Environment)
        qs = Project.objects.filter(environment__in=environments)
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
            file = request.FILES['file']
            title = request.data['title']
            if file:
                Attachment.objects.create(project=project, user=request.user, content=file, attachment_name=title)
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
        if request.user.has_perm('vote', project) and project.vote_starting < datetime.now() < project.vote_closing:
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
                return Response({'result': 1,
                                 'detail': 'Successfully removed permissions'})
            else:
                return Response({'result': 0,
                                 'detail': 'Provided wrong permissions'}, status.HTTP_400_BAD_REQUEST)

        else:
            raise PermissionDenied({"message": "Unable to change user permissions",
                                    "object_id": project.id})


class Repository(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = RepositoryFile.objects.all()
    serializer_class = RepositorySerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user, file_date_created=datetime.now())

    @action(detail=True, methods=['post'])
    def add_to_project(self, request, pk=None):
        repository_file = self.get_object()
        project_id = int(request.data['project_id'])
        project = Project.objects.get(id=project_id)
        if request.user.has_perm('view_project_instance', project):
            repository_file.copy_to_project(project)
            return Response({'result': 1,
                             'detail': 'Successfully moved project'})
        else:
            raise PermissionDenied({"message": "No permission to the project",
                                    "object_id": project.id})


@login_required
def workspace(request):
    repository_files = RepositoryFile.objects.filter(user=request.user)
    categories = ProjectCategory.objects.all()
    context = {
        'repository_files': repository_files,
        'categories': categories
    }
    return render(request, 'pznsi/logged/workspace/workspace.html', context)


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('workspace'))
    else:
        return HttpResponseRedirect(reverse('login'))


def main_page(request):
    if request.user.is_authenticated:
        return render(request, 'pznsi/logged/MainPage.html')
    else:
        return render(request, 'pznsi/anonymous/MainPage.html')


# TODO clean this up a bit
@login_required
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


@login_required
def front_environments(request):
    if request.method == 'POST':
        page = int(request.POST.get('page'))
        keyword = request.POST.get('keyword', None)
        all_environment_list = get_objects_for_user(request.user, 'view_environment_instance', Environment)
        if keyword is not None:
            all_environment_list = all_environment_list.filter(environment_name__icontains=keyword)
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


@login_required
def front_projects(request):
    if request.method == 'POST':
        environment = int(request.POST.get('numEnvi'))
        page = int(request.POST.get('page'))
        keyword = request.POST.get('keyword', None)
        id_project = request.POST.get('id_project', None)
        id_category = int(request.POST.get('category_id', 0))
        environments = get_objects_for_user(request.user, 'view_environment_instance', Environment)
        categories = ProjectCategory.objects.all()
        user_projects = Project.objects.filter(environment__in=environments)
        if id_project is None and id_category != 0:
            category = ProjectCategory.objects.get(id=id_category)
            user_projects = user_projects.filter(project_category=category)
        if id_project is None and keyword is not None:
            user_projects = user_projects.filter(project_name__icontains=keyword)
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
            'projects': project_list,
            'categories': categories
        }
        return render(request, 'pznsi/logged/workspace/projects.html', context)
    else:
        raise Http404


@login_required
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


@login_required
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
                if environment.owner == request.user:
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


@login_required
def save_project(request):
    if request.method == 'POST':
        requested_project = int(request.POST.get('project_id'))
        requested_project_name = request.POST.get('project_name')
        requested_project_category = request.POST.get('project_category')
        requested_project_desc = request.POST.get('project_description')
        vote_start = request.POST.get('startVoteDate', datetime.now())
        vote_end = request.POST.get('endVoteDate', datetime.now()+timedelta(days=14))
        image_base64 = request.POST.get('cover_image')
        requested_owner = int(request.POST.get('owner'))
        environment_id = int(request.POST.get('environment_id'))
        if type(vote_start) == str or type(vote_end) == str:
            vote_start = parse_datetime(vote_start)
            vote_end = parse_datetime(vote_end)
        if requested_project != 0:
            project = Project.objects.get(id=requested_project)
            if request.user.has_perm('edit_project_instance', project):
                project.project_name = requested_project_name
                project.project_content = requested_project_desc
                project.project_category = ProjectCategory.objects.get(id=requested_project_category)
                if request.user == project.owner:
                    project.owner = User.objects.get(id=requested_owner)
                    if vote_start < vote_end:
                        project.vote_starting = vote_start
                        project.vote_closing = vote_end
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
        return JsonResponse(
            {"project_id": project.id,
             "project_name": project.project_name,
             "project_category": project.project_category.id,
             "project_content": project.project_content})
    else:
        raise Http404


@login_required
def edit_project(request):
    if request.method == 'POST':
        requested_project = int(request.POST.get('id'))
        project = None
        start_vote_date = datetime.now()
        end_vote_date = datetime.now() + timedelta(days=14)
        if requested_project != 0:
            project = Project.objects.get(id=requested_project)
            if request.user.has_perm('edit_project_instance', project):
                start_vote_date = project.vote_starting
                end_vote_date = project.vote_closing
                mode = 0
            else:
                raise Http404
        else:
            mode = 1
        users = User.objects.all().exclude(id=get_anonymous_user().id)
        categories = ProjectCategory.objects.all()
        context = {
            'project': project,
            'users': users,
            'mode': mode,
            'project_id': requested_project,
            'categories': categories,
            'startVoteDate': start_vote_date,
            'endVoteDate': end_vote_date
        }
        return render(request, 'pznsi/logged/workspace/edit_project.html', context)
    else:
        raise Http404


@login_required
def can_add_envi(request):
    if request.method == 'POST':
        if request.user.has_perm('pznsi.can_add_environment'):
            can_add = True
        else:
            can_add = False
        return JsonResponse({"can_add": can_add})
    else:
        raise Http404


@login_required
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


@login_required
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


@login_required
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


@login_required
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
