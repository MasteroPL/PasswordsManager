from django.contrib.auth.models import User

from django.db.models import Q, Value
from django.http import Http404
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
	SharePasswordForUserAPIGetRequestSerializer
)
from django.db.models.functions import Concat

class UserPasswordsList(generics.ListAPIView):

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
		ids3 = passwordsAssigned.filter(created_by_id=user.id).values_list("password_id", flat=True)

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
			password_id__in=ids3
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
			result_tmp[passwordsAssignment.password_id] = FullPasswordSerializer(passwordAssignment.password)
			result_tmp[passwordsAssignment.password_id]["assigned_users"] = []
			result_tmp[password.id]["read"] = passwordAssignment.read
			result_tmp[password.id]["share"] = passwordAssignment.share
			result_tmp[password.id]["update"] = passwordAssignment.update
			result_tmp[password.id]["is_owner"] = passwordAssignment.owner

		# Mapping other assignments to their passwords
		for assignment in otherAssignments1:
			result_tmp[assignment.password.id]["assigned_users"].append(
				UserPasswordAssignmentSerializer(assignment).data
			)

		# Finally mapping entire dictionary to an array
		result = list(result_tmp.values())
		result.sort(key=UserPasswordsList.arr_key, reverse=(not asc))
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

		

class SharePasswordForUserAPI(APIView):

	def get_serializer_class(self):
		if self.request.method == "GET":
			return SharePasswordForUserAPIGetRequestSerializer

	def get_users_queryset(self, password_id:int, search:str="", limit:int=10):
		exclude1 = Password.objects.filter(
			id=password_id
		).values_list("owner_id", flat=True)
		exclude2 = UserPasswordAssignment.objects.filter(
			password_id=password_id
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

	def get(self, request, password_id, format=None):
		serializer_cls = self.get_serializer_class()
		serializer = serializer_cls(data=request.query_params)
		if serializer.is_valid():
			users_qs = self.get_users_queryset(password_id, serializer.data["search"], serializer.data["limit"])

			return Response(data=UserSerializer(users_qs, many=True).data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
