from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path('hello/', views.HelloWorld.as_view(), name='hello'),
    path('auth/', obtain_auth_token, name='auth')
]
