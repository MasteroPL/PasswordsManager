from django.urls import path, re_path
from .user_passwords_api import (
    UserPasswordsAPI,
    UserPasswordAPI,
    UserPasswordCopyAPI
)

urlpatterns = [
    path("api/v1/user-passwords/", UserPasswordsAPI.as_view(), name="api_v1_user_passwords"),
    re_path(r"^api/v1/user-password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))$", UserPasswordAPI.as_view(), name="api_v1_user_password"),
    re_path(r"^api/v1/user-password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/copy/$", UserPasswordCopyAPI.as_view(), name="api_v1_user_password_copy"),
]