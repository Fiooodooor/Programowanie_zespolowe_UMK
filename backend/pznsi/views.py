import base64

from django.contrib.auth import login
from django.core.files.base import ContentFile
from django.db.models import Value, IntegerField, Case, When
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user
from guardian.utils import get_anonymous_user
from rest_framework import permissions, mixins, viewsets

from pznsi.models import User, Environment, Project, ProjectCategory
from pznsi.serializers import EnvironmentSerializer, ProjectDetailSerializer


class Environments(mixins.ListModelMixin, viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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
        # TODO fix when permissions are done
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
        if id_project is not None:
            id_project = int(id_project)
            project_list = Project.objects.filter(id=id_project).annotate(
                isOwner=Case(
                    When(owner=request.user.id, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        elif environment == 0:
            project_list = Project.objects.all()[(page - 1) * 12:page * 12].annotate(
                isOwner=Case(
                    When(owner=request.user.id, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
            # TODO
        else:
            project_list = Project.objects.filter(environment=environment)[(page - 1) * 12:page * 12].annotate(
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
    if request.method == 'POST':
        requested_environment = int(request.POST.get('numEnvi'))
        environment = None
        if requested_environment != 0:
            environment = Environment.objects.get(id=requested_environment)
            mode = 0
        else:
            mode = 1
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
            environment.environment_name = requested_environment_name
            environment.owner = User.objects.get(id=requested_owner)
        else:
            environment = Environment.objects.create(environment_name=requested_environment_name,
                                                     owner=User.objects.get(id=requested_owner))
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
        requested_project_category = request.POST.get('project_category')  # byl kom
        requested_project_desc = request.POST.get('project_description')
        image_base64 = request.POST.get('cover_image')
        requested_owner = int(request.POST.get('owner'))
        environment_id = int(request.POST.get('environment_id'))
        if requested_project != 0:
            project = Project.objects.get(id=requested_project)
            project.project_name = requested_project_name
            project.owner = User.objects.get(id=requested_owner)
            project.project_content = requested_project_desc
        else:
            project = Project.objects.create(project_name=requested_project_name,
                                             owner=User.objects.get(id=requested_owner),
                                             project_category=ProjectCategory.objects.get(
                                                 id=requested_project_category),
                                             # project_category=requested_project_category,
                                             project_content=requested_project_desc,
                                             environment=Environment.objects.get(id=environment_id))
        if image_base64 != '':
            format, imgstr = image_base64.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            project.cover_image = image
        project.save()
        return JsonResponse({"project_name": requested_project_name,
                             "project_category": requested_project_category,  # byl kom
                             "project_content": requested_project_desc})
    else:
        raise Http404


def edit_project(request):
    if request.method == 'POST':
        requested_project = int(request.POST.get('id'))
        project = None
        if requested_project != 0:
            project = Project.objects.get(id=requested_project)
            mode = 0
        else:
            mode = 1
        users = User.objects.all().exclude(id=get_anonymous_user().id)
        context = {
            'project': project,
            'users': users,
            'mode': mode,
            'project_id': requested_project,
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
        if environment.owner == request.user:
            can_add = True
        else:
            can_add = False
        return JsonResponse({"can_add": can_add})
    else:
        raise Http404


def PermEnviroment(request):
    return render(request, 'pznsi/logged/workspace/perm_environment.html')


def permProject(request):
    return render(request, 'pznsi/logged/workspace/perm_project.html')


def project(request):
    return render(request, 'pznsi/logged/workspace/project.html')
