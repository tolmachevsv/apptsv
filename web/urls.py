from django.urls import path

from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('auth', views.auth_with_code, name='auth'),
    path('redirect', views.vk_redirect, name='vk_redirect')
]