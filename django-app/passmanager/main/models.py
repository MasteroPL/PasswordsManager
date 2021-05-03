from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django_mysql import models as mysql_models

class UserData(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

	first_name = models.CharField(max_length=30, null=False, blank=False, verbose_name=_("First_name"))
	last_name = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("Last_name"))

class Password(models.Model):
	title = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("Title"))
	description = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Description"))
	code = models.BinaryField(max_length=16, null=False, blank=False, verbose_name=_("Password_code"))
	signature = models.BinaryField(max_length=40, null=False, blank=False, verbose_name=_("Password_signature"))
	
	owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Password_owner"), related_name="password_owner")

	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Created_by"), related_name="password_created_by")
	created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name=_("Created_at"))
	updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Updated_by"), related_name="password_updated_by")
	updated_at = models.DateTimeField(null=False, blank=False, auto_now=True, verbose_name=_("Updated_at"))

	class Meta:
		indexes = (
			models.Index(fields=["code"], name="code_idx"),
			models.Index(fields=["title"], name="title_idx")
		)

class UserPasswordAssignment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User"))
	password = models.ForeignKey(Password, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Password"))

	read = mysql_models.Bit1BooleanField(default=True, verbose_name=_("Can_read"))
	share = mysql_models.Bit1BooleanField(default=False, verbose_name=_("Can_share"))
	update = mysql_models.Bit1BooleanField(default=False, verbose_name=_("Can_update"))
	owner = mysql_models.Bit1BooleanField(default=False, verbose_name=_("Is_owner"))

	class Meta:
		unique_together = ("user", "password")