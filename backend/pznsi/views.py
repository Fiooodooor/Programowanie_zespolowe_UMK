import base64

from django.contrib.auth import login
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from pznsi.models import User


class HelloWorld(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'result': 1,
            'data': 'Hello, world!'
        })


class Environments(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Todo remove hard coded data and replace with actual data from database after models are done
    def get(self, request):
        json_response = {
            'result': 1,
            'data': [
                {
                    'id': 1,
                    'name': 'środowisko 1',
                    'projects': [
                        {'id': 1,
                         'name': 'projekt 1'},
                        {'id': 2,
                         'name': 'projekt 2'},
                        {'id': 3,
                         'name': 'projekt 3'}
                    ]
                },
                {
                    'id': 2,
                    'name': 'środowisko 2',
                    'projects': [
                        {'id': 4,
                         'name': 'projekt 4'},
                        {'id': 5,
                         'name': 'projekt 5'}
                    ]
                },
                {
                    'id': 3,
                    'name': 'środowisko 3',
                    'projects': []
                }
            ]
        }
        return Response(json_response)


class Projects(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Todo remove hard coded data and replace with actual data from database after models are done
    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        json_response = {
            'result': 1,
            'data': {}
        }
        if project_id == 1:
            json_response['data'] = {
                'id': 1,
                'name': 'projekt 1',
                'status': 'status projektu',
                'category': 'kategoria projektu',
                'content': 'zawartosc projektu',
                'comments': [
                    {
                        'commenter': 'Komentujący',
                        'title': 'tytuł komentarza',
                        'content': 'zawartość komentarza',
                        'reaction': ':shrug:',
                        'date': '2019-03-03'
                    },
                    {
                        'commenter': 'Komentujący2',
                        'title': 'tytuł komentarza 2',
                        'content': 'zawartość komentarza2',
                        'reaction': ':shrug:',
                        'date': '2019-03-04'
                    }
                ]
            }
        elif project_id == 2:
            json_response['data'] = {
                'id': 2,
                'name': 'projekt 2',
                'status': 'status projektu',
                'category': 'kategoria projektu',
                'content': 'zawartosc projektu',
                'comments': [
                    {
                        'commenter': 'Komentujący2',
                        'title': 'tytuł komentarza 2',
                        'content': 'zawartość komentarza2',
                        'reaction': ':shrug:',
                        'date': '2019-03-04'
                    }
                ]
            }
        elif project_id == 3:
            json_response['data'] = {
                'id': 3,
                'name': 'projekt 3',
                'status': 'status projektu',
                'category': 'kategoria projektu',
                'content': 'zawartosc projektu',
                'comments': []
            }
        elif project_id == 4:
            json_response['data'] = {
                'id': 4,
                'name': 'projekt 4',
                'status': 'status projektu',
                'category': 'kategoria projektu',
                'content': 'zawartosc projektu',
                'comments': []
            }
        elif project_id == 5:
            json_response['data'] = {
                'id': 5,
                'name': 'projekt 5',
                'status': 'status projektu',
                'category': 'kategoria projektu',
                'content': 'zawartosc projektu',
                'comments': []
            }
        else:
            json_response['result'] = 0,
            json_response['data'] = {'error': 'Couldn\'t find project'}
        return Response(json_response)


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
