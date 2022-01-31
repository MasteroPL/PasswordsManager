from django.contrib import admin
from django.urls import path, re_path, include
from main.api.v1.urls import urlpatterns as api_v1_urls

urlpatterns = [
    *api_v1_urls
]