from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import Permission, User
from django.db.models.fields import related
from django.utils.translation import gettext as _
from django_mysql import models as mysql_models
from django.core.exceptions import ValidationError
from Crypto.Cipher import AES
import os
import uuid
from django.conf import settings
from shutil import copyfile
from .generic_models import GenericPassword
from .abstract_models import AuditModel


class UserTab(models.Model):

	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User_tab"), related_name="user_tabs")

	name = models.CharField(max_length=30, null=False, blank=False, verbose_name=_("Tab_name"))
	order = models.IntegerField(verbose_name=_("Order_of_the_tab"))
	is_default = models.BooleanField(null=True, blank=True, default=None,
		choices=(
			(None, "False"),
			(True, "True")
		)
	)

	class Meta:
		unique_together = (
			("user", "is_default")
		)


class UserPassword(AuditModel):

	password = models.OneToOneField(GenericPassword, on_delete=models.CASCADE, primary_key=True, null=False, blank=False, verbose_name=_("Generic_password"), related_name="user_password")
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User"), related_name="user_passwords")

	user_tab = models.ForeignKey(UserTab, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User_tab"), related_name="tab_passwords")

	@staticmethod
	def create(
		user_id:int, user_tab_id:int,
		password:str, title:str,
		description:str=None, url:str=None,
		username:str=None,
		commit:bool=True
	):
		target_file = None
		try:
			with transaction.atomic():
				generic_password, target_file = GenericPassword.create(
					password,
					title,
					description=description,
					url=url,
					username=username,
					commit=False
				)

				user_password = UserPassword(
					password=generic_password,
					user_id=user_id,
					user_tab_id=user_tab_id
				)

				if commit:
					generic_password.save()
					user_password.save()

				return user_password

		except Exception as e:
			if target_file is not None:
				os.remove(target_file)

			raise e

	def remove(self):
		with transaction.atomic():
			password = self.password

			self.delete()
			password.remove()


class UserPasswordShare(AuditModel):

	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User"), related_name="shared_passwords")

	user_password = models.ForeignKey(UserPassword, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User_password"), related_name="password_shares")

	class Meta:
		unique_together = (
			("user", "user_password")
		)



#
# LEGACY
#

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

	def _create_backup_file(self):
		'''
		Method for password file backup purposes
		'''
		pass_file_dest = os.path.join(Password.TARGET_DIRECTORY, self.code)
		tmp_file_dest = os.path.join(Password.TARGET_DIRECTORY, "_" + self.code)

		if not os.path.isfile(pass_file_dest):
			raise IntegrityError("Password file does not exist")

		if os.path.isfile(tmp_file_dest):
			os.remove(tmp_file_dest)

		# Creating a backup file in case changing the password fails
		copyfile(pass_file_dest, tmp_file_dest)

	def _restore_from_backup_file(self):
		'''
		Reverting to previous password file (if backup available)
		'''
		pass_file_dest = os.path.join(Password.TARGET_DIRECTORY, self.code)
		tmp_file_dest = os.path.join(Password.TARGET_DIRECTORY, "_" + self.code)

		if not os.path.isfile(tmp_file_dest):
			raise IntegrityError("Missing backup file")

		if os.path.isfile(pass_file_dest):
			os.remove(pass_file_dest)

		copyfile(tmp_file_dest, pass_file_dest)

	def _remove_backup_file(self, raise_exception=False):
		tmp_file_dest = os.path.join(Password.TARGET_DIRECTORY, "_" + self.code)
		if os.path.isfile(tmp_file_dest):
			os.remove(tmp_file_dest)
		elif raise_exception:
			raise IntegrityError("Missing backup file")


	def _change_password(self, new_password:str):
		if new_password is None or len(new_password) > 100:
			raise ValueError("new_password can't be none or exceed 100 characters")

		# Defining new password coding
		salt = os.urandom(8)
		full_key = settings.MAIN_APP.PASSWORDS_HS256_MAIN_KEY + salt
		cipher = AES.new(full_key, AES.MODE_EAX)
		nonce = cipher.nonce

		ciphertext, tag = cipher.encrypt_and_digest(new_password.encode("utf-8"))
		signature = tag + nonce + salt

		# backup
		old_signature = self.signature
		old_updated_by_id = self.updated_by_id
		self.signature = signature

		backup_created = False
		with transaction.atomic():
			self.save()
			
			try:
				self._create_backup_file()
				backup_created = True
				with open(os.path.join(Password.TARGET_DIRECTORY, self.code), "wb") as f:
					f.write(ciphertext)
			except:
				# Ensuring data integrity
				self.signature = old_signature
				if backup_created:
					try:
						self._restore_from_backup_file()
						self._remove_backup_file()
					except:
						pass
				
				# Raising exception to cancel changes in database
				raise Password.FailedToCreatePasswordFileError()

		# Backup file will no longer be needed
		self._remove_backup_file()


	@staticmethod
	def _read(password):
		with open(os.path.join(Password.TARGET_DIRECTORY, password.code), "rb") as f:
			ciphertext = f.read()

		tag_nonce_salt = password.signature
		tag = tag_nonce_salt[0:16]
		nonce = tag_nonce_salt[16:32]
		salt = tag_nonce_salt[32:40]

		full_key = settings.MAIN_APP.PASSWORDS_HS256_MAIN_KEY + salt
		cipher = AES.new(full_key, AES.MODE_EAX, nonce=nonce)
		
		try:
			plaintext = cipher.decrypt_and_verify(ciphertext, tag)
		except ValueError:
			raise Password.IntegrityError("Password file and DB entry mismatch")

		try:
			pass_value = plaintext.decode("utf-8")
		except Exception:
			raise Password.IntegrityError("Invalid encoding for password file (despite successful decryption)")

		return pass_value

	def read(self):
		return Password._read(self)

	@staticmethod
	def read_by_code(pass_code:str):
		password = Password.objects.get(code=pass_code)
		return Password._read(password)

	@staticmethod
	def read_by_id(pass_id:int):
		password = Password.objects.get(id=pass_id)
		return Password._read(password)

	@staticmethod
	def user_has_access_to_password(user_id:int, password, read=True, share=False, update=False, owner=False):
		'''
		Determines whether specified user has specified access to given password

		Access validation is only matched againast permission arguments specfied as "True", meaning for arguments:
		- read=True
		- share=True
		- update=False
		- owner=False

		The access will be verified for permissions read and share

		:returns: Returns 2 bools. First determines whether user has access to the password, second whether the user is at least assigned to the password
		'''
		if password.owner_id == user_id:
			return True, True

		assignment = UserPasswordAssignment.objects.filter(password_id=password.id, user_id=user_id)
		if assignment.count() == 0:
			return False, False
		
		assignment = assignment[0]
		if read and not assignment.read and not assignment.owner:
			return False, True
		if share and not assignment.share and not assignment.owner:
			return False, True
		if update and not assignment.update and not assignment.owner:
			return False, True
		if owner and not assignment.owner:
			return False, True

		return True, True

	def user_has_access(self, user_id:int, read=True, share=False, update=False, owner=False):
		'''
		Determines whether specified user has specified access to this password

		Access validation is only matched againast permission arguments specfied as "True", meaning for arguments:
		- read=True
		- share=True
		- update=False
		- owner=False

		The access will be verified for permissions read and share

		:returns: Returns 2 bools. First determines whether user has access to the password, second whether the user is at least assigned to the password
		'''
		return Password.user_has_access_to_password(user_id, self, read=read, share=share, update=update, owner=owner)

	def update_password(self, updated_by_id:int, new_password:str=None, new_title:str=None, new_description:str=None):
		if new_password is None and new_title is None and new_description is None:
			# No changes
			return

		self.updated_by_id = updated_by_id

		if new_title is not None:
			self.title = new_title
		if new_description is not None:
			self.description = new_description

		if new_password is not None:
			# Saving will be performed as part of below method
			self._change_password(new_password)
		else:
			self.save()

	def delete(self, *args, **kwargs):
		password_file = os.path.join(Password.TARGET_DIRECTORY, self.code)
		backup_file = os.path.join(Password.TARGET_DIRECTORY, "_" + self.code)

		with transaction.atomic():
			UserPasswordAssignment.objects.filter(password_id=self.id).delete()
			super().delete(*args, **kwargs)

			if os.path.isfile(backup_file):
				os.remove(backup_file)

			if os.path.isfile(password_file):
				os.remove(password_file)


	class Meta:
		indexes = (
			models.Index(fields=["title"], name="title_idx"),
		)

	class IntegrityError(Exception):
		'''
		Data in the database matched with data stored in files might mismatch
		In this case, the IntegrityError is raised
		'''
		pass

	def __str__(self):
		return "(" + str(self.id) + ") " + self.title

class UserPasswordAssignment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("User"))
	password = models.ForeignKey(Password, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("Password"))

	read = models.BooleanField(default=True, verbose_name=_("Can_read"))
	share = models.BooleanField(default=False, verbose_name=_("Can_share"))
	update = models.BooleanField(default=False, verbose_name=_("Can_update"))
	owner = models.BooleanField(default=False, verbose_name=_("Is_owner"))

	assignment_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name=_("Assignment_owner"), related_name="userpasswordassignment_assignment_owner")

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

	def user_can_edit(self, user_id:int):
		assignment = UserPasswordAssignment.objects.filter(
			password = self.password,
			user_id = user_id
		)

		# Case 1: assignment gives owner permission
		# Only main owner can remove the assignment regardless of the assignment owner
		if self.owner:
			return self.password.owner_id == user_id

		# For the remaining 2 cases, user requires a valid assignment to password
		if assignment.count() == 0:
			return False
		assignment = assignment[0]

		# Case 2: user has admin permissions to assignment
		if assignment.owner:
			return True

		# Case 3: user is assignment owner, and the assignment is read only
		return self.assignment_owner_id == user_id and not self.share and not self.update and not self.owner

	def user_assignment_can_edit(self, assignment):
		if self.owner:
			return self.password.owner_id == assignment.user_id

		if assignment.owner:
			return True

		return self.assignment_owner_id == assignment.user_id and not self.share and not self.update and not self.owner


	class Meta:
		unique_together = ("user", "password")