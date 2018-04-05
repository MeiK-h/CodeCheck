from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'Checker'
urlpatterns = [
    path('', views.index, name='index'),
    path('check/', views.check_list, name='check_list'),
    path('check/<int:pk>/code/', views.code_list, name='code_list'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('create_check/', views.create_check, name='create_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
