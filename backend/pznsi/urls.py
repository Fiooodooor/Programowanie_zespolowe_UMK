from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LogoutView, LoginView

from . import views

urlpatterns = [
    path('api/hello/', views.HelloWorld.as_view(), name='hello'),
    path('api/auth/', obtain_auth_token, name='auth'),
    path('', views.index, name='index'),
    path('test/', views.test),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('main/', views.main_page, name='main')
]
