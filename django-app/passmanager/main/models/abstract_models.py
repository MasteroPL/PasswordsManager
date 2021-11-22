from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from crequest.middleware import CrequestMiddleware
from django.conf import settings


class AuditModel(models.Model):
    '''
    This abstract model adds audit functionalities to your model. The only thing you need to do is inherit from this model. The audit functionalities will work automatically
    '''

    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name=_("Created_at"))
    created_by = models.CharField(max_length=150, null=True, blank=True, default=None, verbose_name=_("Created_by"))
    updated_at = models.DateTimeField(null=False, blank=False, auto_now=True, verbose_name=_("Updated_at"))
    updated_by = models.CharField(max_length=150, null=True, blank=True, default=None, verbose_name=_("Updated_by"))

    def save(self, *args, **kwargs):
        request = CrequestMiddleware.get_request()
        if request is not None and hasattr(request, "user"):
            user = request.user
        else:
            user = None

        username = getattr(user, "username", None)

        if self._state.adding:
            self.created_by = username
        self.updated_by = username

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


