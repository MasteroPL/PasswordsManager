from django.contrib import admin
from django.urls import path, re_path, include
from main.api.passwords import UserPasswordsList, SharePasswordForUserAPI, UserPasswordCreate

urlpatterns = [
    path('api/passwords/', UserPasswordsList.as_view(), name='api_passwords_list'),
    path('api/password/new/', UserPasswordCreate.as_view(), name='api_password_create'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/share/user/$', SharePasswordForUserAPI.as_view(), name='api_password_share'),
]