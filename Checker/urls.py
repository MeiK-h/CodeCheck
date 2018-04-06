from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'Checker'
urlpatterns = [
    path('', views.index, name='index'),
    path('check/', views.check_list, name='check_list'),
    path('check/<int:pk>/delete/', views.delete_check, name='delete_check'),
    path('check/<int:pk>/code/', views.code_list, name='code_list'),
    path('check/<int:pk1>/code/<int:pk2>/delete/', views.delete_code, name='delete_code'),
    path('check/<int:pk>/start/', views.check_start, name='check_start'),
    path('check/<int:pk>/result/', views.check_result, name='check_result'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('create_check/', views.create_check, name='create_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
