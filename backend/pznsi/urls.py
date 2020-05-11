from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers


from . import views
from .views import Environments, Projects

router = routers.DefaultRouter()
router.register(r'environments', Environments)
router.register(r'projects', Projects)


urlpatterns = [
    path('api/auth/', obtain_auth_token, name='auth'),
    path('', views.index, name='index'),
    path('workspace/', views.workspace, name='workspace'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('main/', views.main_page, name='main'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('api/', include(router.urls)),
    path('register/', views.register, name='register'),
    path('front/environments/', views.front_environments, name='front_environments'),
    path('front/projects/', views.front_projects, name='front_projects'),
    path('front/editEnvi', views.edit_environment, name='editEnvi'),
    path('front/editProject', views.edit_project, name='editProject'),
    path('api/editEnviSave', views.save_environment, name='saveEnvi'),
    path('api/editprojectSave', views.save_project, name='saveProject'),
    path('api/canAddEnvi', views.can_add_envi, name='canAddEnvi'),
    path('api/canAddProject', views.can_add_project, name='canAddProject'),
    path('front/environmentsperms/', views.PermEnviroment),
    path('front/projectperms/', views.permProject),
    path('front/project/', views.project)
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
