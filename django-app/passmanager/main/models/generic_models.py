from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import uuid
import os
from Crypto.Cipher import AES

from .abstract_models import AuditModel

class GenericPassword(AuditModel):
	title = models.CharField(max_length=50, null=False, blank=False, verbose_name=_("Title"))
	description = models.CharField(max_length=1000, null=True, blank=True, verbose_name=_("Description"))
	url = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("URL"))
	username = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Username"))
	code=models.CharField(max_length=36, null=False, blank=False, unique=True, verbose_name=_("Password_code")) 
	signature=models.BinaryField(max_length=40, null=False, blank=False, verbose_name=_("Password_signature"))

	class Meta:
		indexes = (
			models.Index(fields=["title"], name="generic_password_title_idx"),
		)


	@staticmethod
	def create(
		password:str, title:str, 
		description:str=None, url:str=None,
		username:str=None,
		commit:bool=True
	):
		if len(password) > 128:
			raise GenericPassword.PasswordTooLongError("Max password length is 128 characters")

		# Verification with DB required to ensure the code is unique
		# Mostly will succeed after 1st attempt
		valid_code = False
		for i in range(5):
			code = str(uuid.uuid4())
			if not GenericPassword.objects.filter(code=code).exists():
				valid_code = True
				break

		# This is very unlikely, but possible
		if not valid_code:
			raise GenericPassword.FailedToGenerateUniqueIdentifierError("System failed to generate unique identifier for the password")

		# Cryptography
		salt = os.urandom(8) # os.urandom is suitable for cryptographic use
		full_key = settings.PASSWORDS_HS256_MAIN_KEY + salt
		cipher = AES.new(full_key, AES.MODE_EAX)
		nonce = cipher.nonce

		ciphertext, tag = cipher.encrypt_and_digest(password.encode('utf-8'))
		signature = tag + nonce + salt # 16 bytes, 16 bytes, 8 bytes

		obj = GenericPassword(
			title=title,
			description=description,
			code=code,
			signature=signature,
			url=url,
			username=username
		)

		target_file = os.path.join(settings.PASSWORDS_TARGET_DIRECTORY, code)
		try:
			with open(target_file, 'wb') as f:
				f.write(ciphertext)

		except Exception as e:
			raise GenericPassword.FailedToCreatePasswordFileError(inner_exception=e)

		if commit:
			try:
				obj.save()
			except Exception as e:
				os.remove(target_file)
				raise e

		return obj, target_file

	@staticmethod
	def _read(password):
		target_file = os.path.join(settings.PASSWORDS_TARGET_DIRECTORY, password.code)

		try:
			with open(target_file, "rb") as f:
				ciphertext = f.read()
		except Exception as e:
			raise GenericPassword.PasswordFileNotFoundError(target_file=target_file)

		tag_nonce_salt = password.signature
		
		try:
			tag = tag_nonce_salt[0:16]
			nonce = tag_nonce_salt[16:32]
			salt = tag_nonce_salt[32:40]
		except Exception as e:
			raise GenericPassword.IntegrityError("Database password configuration invalid")

		full_key = settings.PASSWORDS_HS256_MAIN_KEY + salt
		cipher = AES.new(full_key, AES.MODE_EAX, nonce=nonce)

		try:
			plaintext = cipher.decrypt_and_verify(ciphertext, tag)
		except ValueError:
			raise GenericPassword.IntegrityError("Password file and database configuration mismatch")

		try:
			pass_value = plaintext.decode("utf-8")
		except Exception:
			raise GenericPassword.IntegrityError("Invalid encoding for password file (despite successful decryption)")

		return pass_value

	
	def read(self):
		return GenericPassword._read(self)


	class IntegrityError(Exception):
		'''
		Data in the database matched with data stored in files might mismatch
		In this case, the IntegrityError is raised
		'''
		pass

	class PasswordTooLongError(Exception):
		pass

	class FailedToGenerateUniqueIdentifierError(Exception):
		pass

	class FailedToCreatePasswordFileError(Exception):

		def __init__(self, *args, inner_exception:Exception=None, **kwargs):
			super(*args, **kwargs)

			self.inner_exception = inner_exception

	class PasswordFileNotFoundError(Exception):
		def __init__(self, *args, target_file:str=None, **kwargs):
			super(*args, **kwargs)
			self.target_file = target_file
	

	def __str__(self):
		return "(" + str(self.id) + ") " + self.title