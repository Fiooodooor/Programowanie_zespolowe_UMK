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
    path('test/', views.test),
    path('login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('main/', views.main_page, name='main'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('api/', include(router.urls))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
