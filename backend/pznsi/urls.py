from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('api/hello/', views.HelloWorld.as_view(), name='hello'),
    path('api/auth/', obtain_auth_token, name='auth'),
    path('test/', views.test)
]
