from django.apps import AppConfig
from django.conf import settings as django_settings
import sys

from main.settings import PASSWORDS_HS256_MAIN_KEY

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_defaults(self):
        from . import app_settings as defaults
        for name in dir(defaults):
            if name.isupper() and not hasattr(django_settings, name):
                setattr(django_settings, name, getattr(defaults, name))

    def load_keys(self):
        if not hasattr(django_settings, "PASSWORDS_HS256_MAIN_KEY"):
            f = open(django_settings.PASSWORDS_HS256_MAIN_KEY_PATH, "rb")
            setattr(django_settings, "PASSWORDS_HS256_MAIN_KEY", f.read())
            f.close()

    def ready(self):
        self.set_defaults()
        self.load_keys()

    def dispose(self, *args, **kwargs):
        sys.exit()