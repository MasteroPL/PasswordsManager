from django.contrib.auth.models import User

from django.db.models import Q, Value
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework import generics
from main.commons import serialization_errors_to_response

from main.generic_serializers import MinimalPasswordSerializer, FullPasswordSerializer, FullUserPasswordAssignmentSerializer, UserPasswordAssignmentSerializer, UserSerializer
from main.models import Password, UserPasswordAssignment
from main.api.serializers import (
	ChangePasswordOwnerAPIGetRequestSerializer,
	ChangePasswordOwnerAPIPatchRequestSerializer,
	ChangePasswordOwnerAPIPatchResponseSerializer,
	DeleteUserPasswordAssignmentDeleteRequestSerializer,
	SharePasswordForUserAPIPatchRequestSerializer,
	UserPasswordAssignmentSerializer as UserPasswordAssignmentSerializerNoPasswordDetails, 
	UserPasswordsRequestSerializer,
	SharePasswordForUserAPIGetRequestSerializer,
	SharePasswordForUserAPIPostRequestSerializer,
	UserPasswordCreateRequestSerializer,
	EditPasswordRequestSerializer
)
from django.db.models.functions import Concat
from django.core.exceptions import ValidationError

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.conf import settings

class UserPasswordsListAPI(generics.ListAPIView):

	serializer_class = UserPasswordsRequestSerializer

	@staticmethod
	def arr_key(obj):
		return obj["title"]

	def get_queryset(self, asc=True, search=None):
		user = self.request.user

		if search is None or search == "":
			passwordsOwn = Password.objects.filter(
				owner_id=user.id
			).prefetch_related("created_by", "updated_by", "owner")
			passwordsAssigned = UserPasswordAssignment.objects.filter(
				user_id=user.id
			).prefetch_related(
				"user", 
				"password", 
				"password__created_by", 
				"password__updated_by", 
				"password__owner"
			)
		else:
			passwordsOwn = Password.objects.filter(
				Q(title__icontains=search)|Q(description__icontains=search),
				owner_id=user.id
			).prefetch_related("created_by", "updated_by", "owner")
			passwordsAssigned = UserPasswordAssignment.objects.filter(
				Q(password__title__icontains=search)|Q(password__description__icontains=search),
				user_id=user.id
			).prefetch_related(
				"user", 
				"password", 
				"password__created_by", 
				"password__updated_by", 
				"password__owner"
			)

		# Case 1: User is password owner
		ids1 = passwordsOwn.values_list("id", flat=True)
		ids2 = passwordsAssigned.values_list("password_id", flat=True)
		# # Case 2: User originally shared this password
		# tmp_ids = passwordsAssigned.filter(owner=False).values_list("password_id", flat=True)
		# ids3 = UserPasswordAssignment.objects.filter(password_id__in=tmp_ids, created_by_id=user.id).values_list("id", flat=True)

		# Case 1 query
		otherAssignments1 = UserPasswordAssignment.objects.filter(
			Q(password_id__in=ids1)|Q(password_id__in=ids2)
		).exclude(user_id=user.id).prefetch_related(
			"password",
			"password__created_by",
			"password__updated_by",
			"password__owner"
		)
		# # Case 2 query
		# otherAssignments2 = UserPasswordAssignment.objects.filter(
		# 	id__in=ids3
		# )

		# Creating temporary result (for faster mapping), later it will be remapped into a list
		# Database prevents any collisions in password IDS here
		result_tmp = {}
		for password in passwordsOwn:
			result_tmp[password.id] = FullPasswordSerializer(password).data
			result_tmp[password.id]["assigned_users"] = []
			result_tmp[password.id]["read"] = True
			result_tmp[password.id]["share"] = True
			result_tmp[password.id]["update"] = True
			result_tmp[password.id]["is_owner"] = True
			result_tmp[password.id]["tmp_assignment"] = None

		for passwordAssignment in passwordsAssigned:
			result_tmp[passwordAssignment.password_id] = FullPasswordSerializer(passwordAssignment.password).data
			result_tmp[passwordAssignment.password_id]["assigned_users"] = []
			result_tmp[passwordAssignment.password_id]["read"] = passwordAssignment.read
			result_tmp[passwordAssignment.password_id]["share"] = passwordAssignment.share
			result_tmp[passwordAssignment.password_id]["update"] = passwordAssignment.update
			result_tmp[passwordAssignment.password_id]["is_owner"] = passwordAssignment.owner
			result_tmp[passwordAssignment.password_id]["tmp_assignment"] = passwordAssignment

		# Mapping other assignments to their passwords
		for assignment in otherAssignments1:
			assignment_data = UserPasswordAssignmentSerializerNoPasswordDetails(assignment).data
			if assignment.password.owner_id == self.request.user.id:
				assignment_data["editable"] = True
			elif assignment.user_assignment_can_edit(result_tmp[assignment.password.id]["tmp_assignment"]):
				assignment_data["editable"] = True
			else:
				assignment_data["editable"] = False

			result_tmp[assignment.password.id]["assigned_users"].append(
				assignment_data
			)

		for r in result_tmp:
			result_tmp[r].pop("tmp_assignment")
		# for assignment in otherAssignments2:
		# 	result_tmp[assignment.password.id]["assigned_users"].append(
		# 		UserPasswordAssignmentSerializerNoPasswordDetails(assignment).data
		# 	)

		# Finally mapping entire dictionary to an array
		result = list(result_tmp.values())
		result.sort(key=UserPasswordsListAPI.arr_key, reverse=(not asc))
		return result

	def paginate(self, queryset, page=1, per_page=10):
		if per_page < 1:
			per_page = 1
		elif per_page > 500:
			per_page = 500

		total = len(queryset)
		num_pages = int(total / per_page)
		if total % per_page != 0:
			num_pages += 1

		if page < 1:
			page = 1
		elif page > num_pages:
			page = num_pages
			if page == 0:
				page = 1

		index_start = (page - 1) * per_page
		index_finish = index_start + 10
		if index_finish > total:
			index_finish = total

		return {
			"page": page,
			"total": total,
			"per_page": per_page,
			"num_pages": num_pages,
			"offset": index_start,
			"items": queryset[index_start:index_finish]
		}

	def list(self, request):
		serializer = UserPasswordsRequestSerializer(data=request.query_params)
		if serializer.is_valid():
			items = self.get_queryset(
				asc=serializer.data["order_asc"], 
				search=serializer.data["search"]
			)

			items = self.paginate(items, page=serializer.data["page"], per_page=serializer.data["per_page"])
			items["asc"] = serializer.data["order_asc"]
			
			return Response(data=items, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordCreateAPI(APIView):
	def get_serializer_class(self):
		return UserPasswordCreateRequestSerializer

	def post(self, request, format=None):
		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.data)

		if serializer.is_valid():
			try:
				password = Password.create(
					serializer.data["password"],
					serializer.data["title"],
					serializer.data["description"],
					owner_id=request.user.id,
					created_by_id=request.user.id
				)
			except ValidationError as e:
				return Response(e.error_dict, status=status.HTTP_400_BAD_REQUEST)
			except IntegrityError as e:
				raise e
				return Response(data={
					"__all__": "Could not create the requested password due to an internal server error"
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			response = FullPasswordSerializer(password).data
			return Response(response, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordDecryptAPI(APIView):
	
	def post(self, request, password_code:str, format=None):
		'''
		Used to obtain a decrypted password via password_code
		'''

		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		has_permission, is_assigned = password.user_has_access(request.user.id)
		if not has_permission:
			if not is_assigned:
				raise Http404()

			return Response(status=status.HTTP_403_FORBIDDEN)

		try:
			pass_value = password.read()
		except Password.IntegrityError:
			return Response(data={
				"error_code": "PASSWORD_INTEGRITY_ERROR",
				"error_message": "The password has not been properly stored server side. Please contact the administrator for more infromation."
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return Response(data={
			"password": pass_value
		}, status=status.HTTP_200_OK)



class SharePasswordForUserAPI(APIView):

	def get_serializer_class(self):
		if self.request.method == "GET":
			return SharePasswordForUserAPIGetRequestSerializer
		elif self.request.method == "POST":
			return SharePasswordForUserAPIPostRequestSerializer

	def get_users_queryset(self, password_code:str, search:str="", limit:int=10):
		exclude1 = Password.objects.filter(
			code=password_code
		).values_list("owner_id", flat=True)
		exclude2 = UserPasswordAssignment.objects.filter(
			password__code=password_code
		).values_list("user_id", flat=True)

		if search is not None and search != "":
			users_qs = User.objects.annotate(
				full_search=Concat(
					'email', Value(' '), 
					'username', Value(' '), 
					'first_name', Value(' '), 
					'last_name', Value(' '), 
					'first_name'
				)
			).filter(
				full_search__icontains=search
			).exclude(
				Q(id__in=exclude1)|Q(id__in=exclude2)
			).order_by('username')[:limit]
		else:
			users_qs = User.objects.all(
			).exclude(
				Q(id__in=exclude1)|Q(id__in=exclude2)
			).order_by('username')[:limit]

		return users_qs

	def get(self, request, password_code:str, format=None):
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		if password.owner_id != request.user.id:
			try:
				assignment = UserPasswordAssignment.objects.get(password__code=password_code, user_id=request.user.id)
			except UserPasswordAssignment.DoesNotExist:
				raise Http404()

			if not assignment.share:
				return HttpResponseForbidden()

		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.query_params)
		if serializer.is_valid():
			users_qs = self.get_users_queryset(password_code, serializer.data["search"], serializer.data["limit"])

			return Response(data=UserSerializer(users_qs, many=True).data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	
	def post(self, request, password_code:str, format=None):
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		qs = UserPasswordAssignment.objects.filter(password__code=password_code, user_id=request.user.id)
		if qs.count() != 0:
			assignment = qs[0]

			if not assignment.share:
				return HttpResponseForbidden()
		else:
			assignment = None
			if password.owner_id != request.user.id:
				# This user is not assigned to the password, as far as they're concerned, it doesn't exist
				raise Http404()

		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.data)

		if serializer.is_valid():
			# Permission check
			if password.owner_id != request.user.id:
				if serializer.data["permission_owner"]:
					return HttpResponseForbidden()
				elif serializer.data["permission_update"] or serializer.data["permission_share"]:
					if not assignment.owner:
						return HttpResponseForbidden()

			# Assignment creation
			assignment = UserPasswordAssignment(
				user_id = serializer.data["user_id"],
				password_id = password.id,

				read = serializer.data["permission_read"],
				share = serializer.data["permission_share"],
				update = serializer.data["permission_update"],
				owner = serializer.data["permission_owner"],

				assignment_owner_id = request.user.id,
				created_by_id = request.user.id,
				updated_by_id = request.user.id
			)
			try:
				assignment.save()
			except ValidationError as e:
				return Response(e.error_dict, status=status.HTTP_400_BAD_REQUEST)
			
			return Response(FullUserPasswordAssignmentSerializer(assignment).data, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordAssignmentAPI(APIView):
	def get_serializer_class(self):
		if self.request.method == "PATCH":
			return SharePasswordForUserAPIPatchRequestSerializer
		elif self.request.method == "DELETE":
			return None

	def patch(self, request, password_code:str, user_id:int, format=None):
		# Checking permissions
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		qs = UserPasswordAssignment.objects.filter(password__code=password_code, user_id=request.user.id)
		assignment = UserPasswordAssignment.objects.filter(password__code=password_code, user_id=user_id)
		my_assignment = None

		if assignment.count() == 0:
			raise Http404()
		assignment = assignment[0]

		if qs.count() != 0:
			my_assignment = qs[0]

			if not assignment.user_assignment_can_edit(my_assignment):
				return Response(status=status.HTTP_403_FORBIDDEN)
		else:
			if password.owner_id != request.user.id:
				# This user is not assigned to the password, as far as they're concerned, it doesn't exist
				raise Http404()

		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.data)

		if serializer.is_valid():
			# 3 cases to consider

			# Case 1. Attempting to assign owner permissions
			if serializer.data["permission_owner"]:
				# Requires user to be the passwords main owner
				if password.owner_id != request.user.id:
					return Response(status=status.HTTP_403_FORBIDDEN)

			# Case 2. Attempting to assign permissions other than readonly
			elif serializer.data["permission_share"] or serializer.data["permission_update"]:
				# Requires at least owner permission
				if password.owner_id != request.user.id and not my_assignment.owner:
					return Response(status=status.HTTP_403_FORBIDDEN)

			# Case 3. Attempting to assign readonly permissions
			else:
				if password.owner_id != request.user.id and not my_assignment.share:
					return Response(status=status.HTTP_403_FORBIDDEN)


			# Permissions validated, updating assignment
			try:
				if not serializer.data["permission_owner"]:
					assignment.read = serializer.data["permission_read"]
					assignment.share = serializer.data["permission_share"]
					assignment.update = serializer.data["permission_update"]
					assignment.owner = False
				else:
					assignment.read = True
					assignment.share = True
					assignment.update = True
					assignment.owner = True
				assignment.assignment_owner_id = request.user.id
				assignment.updated_by_id = request.user.id

				assignment.save()
			except:
				return Response(data={
					"message": "An internal server error occured when attempting to save changes"
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			response = UserPasswordAssignmentSerializerNoPasswordDetails(instance=assignment)
			return Response(response.data, status=status.HTTP_200_OK)

		# Processing errors
		errors = serialization_errors_to_response(serializer.errors)
		return Response(errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, password_code:str, user_id:int, format=None):
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		assignment = UserPasswordAssignment.objects.filter(password_id = password.id, user_id = user_id)

		if assignment.count() == 0:
			return Http404()

		assignment = assignment[0]

		if password.owner_id != request.user.id:
			# The long way of verifying permission
			my_assignment = UserPasswordAssignment.objects.filter(
				password_id = password.id,
				user_id = request.user.id
			)
			if my_assignment.count() == 0:
				raise Http404()

			my_assignment = my_assignment[0]

			if not my_assignment.share and not my_assignment.owner:
				return Response(status=status.HTTP_403_FORBIDDEN)	
		
		if user_id == password.owner_id:
			return Response(status=status.HTTP_403_FORBIDDEN)

		try:
			# User has to be either the main password owner or have specified permissions
			if password.owner_id != request.user.id and not assignment.user_assignment_can_edit(my_assignment):
				return Response(status=status.HTTP_403_FORBIDDEN)

			assignment.delete()
		except:
			return Response(data={
				"message": "An internal server error occured when attempting to save changes"
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return Response(status=status.HTTP_200_OK)


class EditPasswordAPI(APIView):

	def get_serializer_class(self):
		if self.request.method == "PATCH":
			return EditPasswordRequestSerializer

	def patch(self, request, password_code:str, format=None):
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		access, permission = password.user_has_access(request.user.id, read=False, update=True)
		if not access:
			raise Http404()

		if not permission:
			return Response(status=status.HTTP_403_FORBIDDEN)

		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.data)

		if serializer.is_valid():
			password.update_password(request.user.id, serializer.data["new_password"], serializer.data["title"], serializer.data["description"])

			response = MinimalPasswordSerializer(password)

			return Response(data=response.data, status=status.HTTP_200_OK)

		# Processing errors
		errors = serialization_errors_to_response(serializer.errors)

		return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordOwnerAPI(APIView):

	def get_serializer_class(self):
		if self.request.method == "GET":
			return ChangePasswordOwnerAPIGetRequestSerializer
		elif self.request.method == "PATCH":
			return ChangePasswordOwnerAPIPatchRequestSerializer

	def get_users_queryset(self, search:str="", limit:int=10):
		if search is not None and search != "":
			users_qs = User.objects.annotate(
				full_search=Concat(
					'email', Value(' '), 
					'username', Value(' '), 
					'first_name', Value(' '), 
					'last_name', Value(' '), 
					'first_name'
				)
			).filter(
				full_search__icontains=search
			).exclude(
				id = self.request.user.id
			).order_by('username')[:limit]
		else:
			users_qs = User.objects.all(
			).exclude(
				id = self.request.user.id
			).order_by('username')[:limit]

		return users_qs

	def get(self, request, password_code:str, format=None):
		'''
		Used for querying which users can be assigned as new password owners
		'''

		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		access, permission = password.user_has_access(request.user.id, read=False)
		if not access:
			raise Http404()

		if password.owner_id != request.user.id:
			# Only password owner can access this method
			return Response(status=status.HTTP_403_FORBIDDEN)
		
		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.query_params)
		if serializer.is_valid():
			users_qs = self.get_users_queryset(serializer.data["search"], serializer.data["limit"])

			return Response(data=UserSerializer(users_qs, many=True).data, status=status.HTTP_200_OK)

		errors = serialization_errors_to_response(serializer.errors)
		return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

	def patch(self, request, password_code:str, format=None):
		'''
		Actually assigns a new password owner 
		'''
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		access, permission = password.user_has_access(request.user.id, read=False)
		if not access:
			raise Http404()

		if password.owner_id != request.user.id:
			# Only password owner can access this method
			return Response(status=status.HTTP_403_FORBIDDEN)

		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.data)
		if serializer.is_valid():
			# Case of attempting to reassign self
			if serializer.data["user_id"] == password.owner_id:
				return Response(data={
					"user_id": [
						{
							"string": "This user is already the main password owner",
							"code": "USER_ALREADY_MAIN_OWNER"
						}
					]
				}, status=status.HTTP_400_BAD_REQUEST)

			try:
				with transaction.atomic():
					UserPasswordAssignment.objects.filter(
						user_id = serializer.data["user_id"],
						password_id = password.id
					).delete()

					new_assignment = UserPasswordAssignment(
						user_id = request.user.id,
						password = password,
						read = True,
						share = True,
						update = True,
						owner = True,
						created_by_id = request.user.id,
						updated_by_id = request.user.id
					)
					password.owner_id = serializer.data["user_id"]
					password.save()
					new_assignment.save()
					new_assignment.password = password
			except Exception as e:
				return Response(data={
					"message": "An internal server error occured when attempting to save changes"
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			response = ChangePasswordOwnerAPIPatchResponseSerializer(new_assignment)
			return Response(data=response.data, status=status.HTTP_200_OK)


		errors = serialization_errors_to_response(serializer.errors)
		return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class DeletePasswordAPI(APIView):
	
	def get_serializer_class(self):
		if self.request.method == "DELETE":
			return None

	def delete(self, request, password_code:str, format=None):
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		access, permission = password.user_has_access(request.user.id, read=False)
		if not access:
			raise Http404()

		if password.owner_id != request.user.id:
			# Only password owner can access this method
			return Response(status=status.HTTP_403_FORBIDDEN)

		try:
			# Overriden to take care of password files alongside deleting the password from the database
			password.delete()
		except:
			return Response(data={
				"message": "An internal server error occured when attempting to save changes"
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return Response(status=status.HTTP_200_OK)

class RemoveMyPasswordAssignmentAPI(APIView):
	def get_serializer_class(self):
		if self.request.method == "DELETE":
			return None

	def delete(self, request, password_code:str, format=None):
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		access, permission = password.user_has_access(request.user.id, read=False)
		if not access:
			raise Http404()

		if password.owner_id == request.user.id:
			# Only password owner can access this method
			return Response(data={
				"message": "As password main owner you cannot remove your own assignment to the password. Either delete the password entirely, or pass the ownership to another user before reattempting the request."
			}, status=status.HTTP_403_FORBIDDEN)

		try:
			UserPasswordAssignment.objects.filter(password_id = password.id, user_id = request.user.id).delete()
		except:
			return Response(data={
				"message": "An internal server error occured when attempting to save changes"
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return Response(status=status.HTTP_200_OK)


class DeleteUserPasswordAssignmentAPI(APIView):
	def get_serializer_class(self):
		if self.request.method == "DELETE":
			return DeleteUserPasswordAssignmentDeleteRequestSerializer

	def delete(self, request, password_code:str, format=None):
		try:
			password = Password.objects.get(code=password_code)
		except Password.DoesNotExist:
			raise Http404()

		if password.owner_id != request.user.id:
			# The long way of verifying permission
			my_assignment = UserPasswordAssignment.objects.filter(
				password_id = password.id,
				user_id = request.user.id
			)
			if my_assignment.count() == 0:
				raise Http404()

			my_assignment = my_assignment[0]

			if not my_assignment.share and not my_assignment.owner:
				return Response(status=status.HTTP_403_FORBIDDEN)

		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.data)		
		
		if serializer.is_valid():
			if serializer.data["user_id"] == password.owner_id:
				return Response(status=status.HTTP_403_FORBIDDEN)

			try:
				assignment = UserPasswordAssignment.objects.filter(password_id = password.id, user_id = serializer.data["user_id"])

				if assignment.count() == 0:
					return Response(data={
						"user_id": {
							"string": "User not assigned to the password",
							"code": "USER_NOT_ASSIGNED"
						}
					})

				assignment = assignment[0]

				# User has to be either the main password owner or have specified permissions
				if password.owner_id != request.user.id and not assignment.user_assignment_can_edit(my_assignment):
					return Response(status=status.HTTP_403_FORBIDDEN)

				assignment.delete()
			except:
				return Response(data={
					"message": "An internal server error occured when attempting to save changes"
				}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

			return Response(status=status.HTTP_200_OK)

		errors = serialization_errors_to_response(serializer.errors)
		return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
			
