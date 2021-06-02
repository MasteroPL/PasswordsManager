from django.contrib import admin
from django.urls import path, re_path, include
from main.api.passwords import (
    DeletePasswordAPI,
    RemoveMyPasswordAssignmentAPI,
    UserPasswordsListAPI, 
    SharePasswordForUserAPI, 
    UserPasswordCreateAPI, 
    UserPasswordDecryptAPI,
    EditPasswordAPI,
    ChangePasswordOwnerAPI
)

urlpatterns = [
    path('api/passwords/', UserPasswordsListAPI.as_view(), name='api_passwords_list'),
    path('api/password/new/', UserPasswordCreateAPI.as_view(), name='api_password_create'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/share/user/$', SharePasswordForUserAPI.as_view(), name='api_password_share'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/obtain/$', UserPasswordDecryptAPI.as_view(), name='api_password_obtain'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/edit/', EditPasswordAPI.as_view(), name='api_password_edit'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/change-owner/', ChangePasswordOwnerAPI.as_view(), name='api_password_change_owner'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/delete/', DeletePasswordAPI.as_view(), name='api_password_delete'),
    re_path(r'^api/password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/deassign-me/', RemoveMyPasswordAssignmentAPI.as_view(), name='api_password_deassign_me')
]