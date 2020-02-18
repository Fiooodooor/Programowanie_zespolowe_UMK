from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions
from django.http import Http404


# Create your views here.
from rest_framework.response import Response


class HelloWorld(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "result": 1,
            "data": "Hello, world!"
        })


def test(request):
    return render(request, 'pznsi/test.html')


def index(request):
    return render(request, 'pznsi/index.html')


def main_page(request):
    if request.user.is_authenticated:
        return render(request, 'pznsi/MainPage.html')
    else:
        raise Http404
