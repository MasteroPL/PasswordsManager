from django.contrib.auth.models import User

from django.db.models import Q, Value
from django.db import IntegrityError
from django.http import Http404, HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework import generics

from main.generic_serializers import FullPasswordSerializer, FullUserPasswordAssignmentSerializer, UserSerializer
from main.models import Password, UserPasswordAssignment
from main.api.serializers import (
	UserPasswordAssignmentSerializer, 
	UserPasswordsRequestSerializer,
	SharePasswordForUserAPIGetRequestSerializer,
	SharePasswordForUserAPIPostRequestSerializer,
	UserPasswordCreateRequestSerializer
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
		ids2 = passwordsAssigned.filter(owner=True).values_list("password_id", flat=True)
		# Case 2: User originally shared this password
		tmp_ids = passwordsAssigned.filter(owner=False).values_list("password_id", flat=True)
		ids3 = UserPasswordAssignment.objects.filter(password_id__in=tmp_ids, created_by_id=user.id).values_list("id", flat=True)

		# Case 1 query
		otherAssignments1 = UserPasswordAssignment.objects.filter(
			Q(password_id__in=ids1)|Q(password_id__in=ids2)
		).exclude(user_id=user.id).prefetch_related(
			"password",
			"password__created_by",
			"password__updated_by",
			"password__owner"
		)
		# Case 2 query
		otherAssignments2 = UserPasswordAssignment.objects.filter(
			id__in=ids3
		)

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

		for passwordAssignment in passwordsAssigned:
			result_tmp[passwordAssignment.password_id] = FullPasswordSerializer(passwordAssignment.password).data
			result_tmp[passwordAssignment.password_id]["assigned_users"] = []
			result_tmp[passwordAssignment.password_id]["read"] = passwordAssignment.read
			result_tmp[passwordAssignment.password_id]["share"] = passwordAssignment.share
			result_tmp[passwordAssignment.password_id]["update"] = passwordAssignment.update
			result_tmp[passwordAssignment.password_id]["is_owner"] = passwordAssignment.owner

		# Mapping other assignments to their passwords
		for assignment in otherAssignments1:
			result_tmp[assignment.password.id]["assigned_users"].append(
				UserPasswordAssignmentSerializer(assignment).data
			)
		for assignment in otherAssignments2:
			result_tmp[assignment.password.id]["assigned_users"].append(
				UserPasswordAssignmentSerializer(assignment).data
			)

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
				created_by_id = request.user.id,
				updated_by_id = request.user.id
			)
			try:
				assignment.save()
			except ValidationError as e:
				return Response(e.error_dict, status=status.HTTP_400_BAD_REQUEST)
			
			return Response(FullUserPasswordAssignmentSerializer(assignment).data, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
