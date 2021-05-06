from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django_mysql import models as mysql_models

class Password(models.Model):
	title = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("Title"))
	description = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Description"))
	code = models.CharField(max_length=36, null=False, blank=False, unique=True, verbose_name=_("Password_code"))
	signature = models.BinaryField(max_length=40, null=False, blank=False, verbose_name=_("Password_signature"))
	
	owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Password_owner"), related_name="password_owner")

	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Created_by"), related_name="password_created_by")
	created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name=_("Created_at"))
	updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Updated_by"), related_name="password_updated_by")
	updated_at = models.DateTimeField(null=False, blank=False, auto_now=True, verbose_name=_("Updated_at"))

	class Meta:
		indexes = (
			models.Index(fields=["title"], name="title_idx"),
		)

	def __str__(self):
		return "(" + str(self.id) + ") " + self.title

class UserPasswordAssignment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User"))
	password = models.ForeignKey(Password, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Password"))

	read = models.BooleanField(default=True, verbose_name=_("Can_read"))
	share = models.BooleanField(default=False, verbose_name=_("Can_share"))
	update = models.BooleanField(default=False, verbose_name=_("Can_update"))
	owner = models.BooleanField(default=False, verbose_name=_("Is_owner"))

	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Created_by"), related_name="userpasswordassignment_created_by")
	created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name=_("Created_at"))
	updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Updated_by"), related_name="userpasswordassignment_updated_by")
	updated_at = models.DateTimeField(null=False, blank=False, auto_now=True, verbose_name=_("Updated_at"))

	class Meta:
		unique_together = ("user", "password")