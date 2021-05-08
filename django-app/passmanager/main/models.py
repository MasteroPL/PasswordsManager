from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django_mysql import models as mysql_models
from django.core.exceptions import ValidationError
from Crypto.Cipher import AES
import os
import uuid
from django.conf import settings

class Password(models.Model):
	TARGET_DIRECTORY = os.path.join("protected", "passwords")

	title = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("Title"))
	description = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Description"))
	code = models.CharField(max_length=36, null=False, blank=False, unique=True, verbose_name=_("Password_code"))
	signature = models.BinaryField(max_length=40, null=False, blank=False, verbose_name=_("Password_signature"))
	
	owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Password_owner"), related_name="password_owner")

	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Created_by"), related_name="password_created_by")
	created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name=_("Created_at"))
	updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Updated_by"), related_name="password_updated_by")
	updated_at = models.DateTimeField(null=False, blank=False, auto_now=True, verbose_name=_("Updated_at"))

	class FailedToCreatePasswordFileError(IntegrityError):
		pass

	@staticmethod
	def create(password:str, title:str, description:str, owner_id:int, created_by_id:int=None):
		if created_by_id is None:
			created_by_id = owner_id

		if len(password) > 100:
			raise ValidationError({
				'password': ValidationError(message="Max allowed password length is 100 charates", code="PASSWORD_TOO_LONG")
			})
		valid_code = False
		for i in range(5):
			code = str(uuid.uuid4())
			if Password.objects.filter(code=code).count() == 0:
				valid_code = True
				break

		# Failed to generate unique code ID
		if not valid_code:
			raise ValidationError({
				'code': ValidationError(message="Failed to generate a unique password code", code="FAILED_TO_GENERATE_CODE")
			})

		# Generating cryptography
		salt = os.urandom(8)
		full_key = settings.MAIN_APP.PASSWORDS_HS256_MAIN_KEY + salt
		cipher = AES.new(full_key, AES.MODE_EAX)
		nonce = cipher.nonce

		ciphertext, tag = cipher.encrypt_and_digest(password.encode("utf-8"))
		signature = tag + nonce + salt

		# Preparing instance for Database
		instance = Password(
			title=title,
			description=description,
			code=code,
			owner_id=owner_id,
			signature=signature,
			created_by_id=created_by_id,
			updated_by_id=created_by_id
		)

		# Do not save the instance, if file creation will end up in a failure
		with transaction.atomic():
			instance.save()
			try:
				with open(os.path.join(Password.TARGET_DIRECTORY, code), "wb") as f:
					f.write(ciphertext)
			except Exception as e:
				raise Password.FailedToCreatePasswordFileError()
		
		return instance

		

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

	def clean(self, *args, **kwargs):
		super().clean(*args, **kwargs)

		if self.password.owner_id == self.user_id:
			raise ValidationError({
				'user_id': ValidationError("User is password owner", code="PASSWORD_OWNER_REASSIGNMENT")
			})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

	class Meta:
		unique_together = ("user", "password")