from django.contrib import admin
from django.urls import path, re_path, include
from main.api.passwords import UserPasswordsListAPI, SharePasswordForUserAPI, UserPasswordCreateAPI, UserPasswordDecryptAPI

urlpatterns = [
    path('api/passwords/', UserPasswordsListAPI.as_view(), name='api_passwords_list'),
    path('api/password/new/', UserPasswordCreateAPI.as_view(), name='api_password_create'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/share/user/$', SharePasswordForUserAPI.as_view(), name='api_password_share'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/obtain/$', UserPasswordDecryptAPI.as_view(), name='api_password_obtain'),
]