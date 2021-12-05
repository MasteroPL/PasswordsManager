from .boards.boards_urls import urlpatterns as boards_urls
from .user_passwords.user_passwords_urls import urlpatterns as user_passwords_urls

urlpatterns = [
    *boards_urls,
    *user_passwords_urls
]
