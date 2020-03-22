from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path('api/hello/', views.HelloWorld.as_view(), name='hello'),
    path('api/auth/', obtain_auth_token, name='auth'),
    path('api/environments/', views.Environments.as_view(), name='environments'),
    path('api/projects/<int:project_id>/', views.Projects.as_view(), name='projects'),
    path('', views.index, name='index'),
    path('test/', views.test),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('main/', views.main_page, name='main'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
