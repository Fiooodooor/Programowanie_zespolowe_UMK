from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views
from .views import Environments, Projects, Repository

router = routers.DefaultRouter()
router.register(r'environments', Environments)
router.register(r'projects', Projects)
router.register(r'repository', Repository)

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('main/', views.main_page, name='main'),
    path('workspace/', views.workspace, name='workspace'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('front/environments/', views.front_environments, name='front_environments'),
    path('front/projects/', views.front_projects, name='front_projects'),
    path('front/editEnvi', views.edit_environment, name='editEnvi'),
    path('front/editProject', views.edit_project, name='editProject'),
    path('front/environmentsperms/', views.PermEnviroment),
    path('front/projectperms/', views.permProject),
    path('front/project/', views.project),
    path('api/', include(router.urls)),
    path('api/auth/', obtain_auth_token, name='auth'),
    path('api/editEnviSave', views.save_environment, name='saveEnvi'),
    path('api/editprojectSave', views.save_project, name='saveProject'),
    path('api/canAddEnvi', views.can_add_envi, name='canAddEnvi'),
    path('api/canAddProject', views.can_add_project, name='canAddProject')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
