from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions

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