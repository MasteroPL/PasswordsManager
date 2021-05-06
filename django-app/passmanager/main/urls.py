from django.contrib import admin
from django.urls import path, re_path, include
from main.api.passwords import UserPasswordsList, SharePasswordForUserAPI

urlpatterns = [
    path('api/passwords/', UserPasswordsList.as_view(), name='api_passwords_list'),
    path('api/password/<int:password_id>/share/', SharePasswordForUserAPI.as_view(), name='api_password_share'),
]