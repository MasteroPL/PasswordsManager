from django.urls import path, re_path
from .user_passwords_api import (
    UserPasswordsAPI,
    UserPasswordAPI,
    UserPasswordCopyAPI,
    UserPasswordSharesAPI,
    UserPasswordShareAPI,
    UserPasswordMySharesAPI,
    UserPasswordDuplicateAPI,
    UserTabsAPI,
    UserTabAPI
)

urlpatterns = [
    path("api/v1/user-passwords/", UserPasswordsAPI.as_view(), name="api_v1_user_passwords"),
    re_path(r"^api/v1/user-password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))$", UserPasswordAPI.as_view(), name="api_v1_user_password"),

    re_path(r"^api/v1/user-password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/copy/$", UserPasswordCopyAPI.as_view(), name="api_v1_user_password_copy"),

    re_path(r"api/v1/user-password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/shares/$", UserPasswordSharesAPI.as_view(), name="api_v1_user_password_shares"),

    re_path(r"api/v1/user-password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/share/(?P<share_id>([0-9]+))$", UserPasswordShareAPI.as_view(), name="api_v1_user_password_share"),

    re_path(r"api/v1/user-passwords/shared-to-me/$", UserPasswordMySharesAPI.as_view(), name="api_v1_user_password_shared_to_me"),

    re_path(r"^api/v1/user-password/(?P<password_code>([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}))/duplicate/$", UserPasswordDuplicateAPI.as_view(), name="api_v1_user_password_duplicate"),

    path("api/v1/user-passwords/tabs/", UserTabsAPI.as_view(), name="api_v1_user_tabs"),

    path("api/v1/user-passwords/tab/<int:tab_id>", UserTabAPI.as_view(), name="api_v1_user_tab"),

    
]