import base64

from django.contrib.auth import login
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import permissions, generics, mixins, viewsets
from rest_framework.mixins import CreateModelMixin

from rest_framework.response import Response
from rest_framework.views import APIView
from pznsi.models import User, Environment, Project
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


def test(request):
    return render(request, 'pznsi/test.html')


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main'))
    else:
        return render(request, 'pznsi/anonymous/index.html')


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
            login(request, user)
            return HttpResponseRedirect(reverse('main'))
