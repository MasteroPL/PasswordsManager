from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from main.models import Password, UserPasswordAssignment
from main.generic_serializers import UserSerializer

class UserPasswordAssignmentSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	created_by = UserSerializer()
	updated_by = UserSerializer()

	class Meta:
		model = UserPasswordAssignment
		fields = fields = ["user", "read", "share", "update", "owner", "created_by", "created_at", "updated_by", "updated_at"]


class UserPasswordsRequestSerializer(serializers.Serializer):
	page = serializers.IntegerField(required=False, default=1)
	per_page = serializers.IntegerField(required=False, default=10)
	order_asc = serializers.BooleanField(required=False, default=True)
	search = serializers.CharField(required=False, default="")


class SharePasswordForUserAPIGetRequestSerializer(serializers.Serializer):
	search = serializers.CharField(required=False, default="")
	limit = serializers.IntegerField(required=False, default=10)

	def validate(self, data):
		data = super().validate(data)

		s = data["search"]
		if len(s) > 100:
			raise serializers.ValidationError({"search": "Search string has exceeded the maximum length (100 characters)"})

		l = data["limit"]
		if l < 1 or l > 50:
			raise serializers.ValidationError({"limit": "Limit has to be within range: <1, 50>"})

		return data


class EditPasswordRequestSerializer(serializers.Serializer):
	new_password = serializers.CharField(required=False, default=None)
	title = serializers.CharField(required=False, default=None)
	description = serializers.CharField(required=False, default=None)

	def validate(self, data):
		data = super().validate(data)

		if data["new_password"] is None and data["title"] is None and data["description"] is None:
			raise serializers.ValidationError(detail="No changes detected", code="NO_CHANGES")

		if data["new_password"] is not None and len(data["new_password"]) > 100:
			raise serializers.ValidationError({"new_password": ErrorDetail(
				"Password too long. Can be at most 100 characters.",
				code="PASSWORD_TOO_LONG"
			)})

		if data["title"] is not None and len(data["title"]) > 50:
			raise serializers.ValidationError({"title": ErrorDetail(
				"Title too long. Can be at most 50 characters.",
				code="TITLE_TOO_LONG"
			)})

		if data["description"] is not None and len(data["description"]) > 500:
			raise serializers.ValidationError({"description": ErrorDetail(
				"Description too long. Can be at most 100 characters.",
				code="DESCRIPTION_TOO_LONG"
			)})

		return data

class UserPasswordCreateRequestSerializer(serializers.Serializer):
	password = serializers.CharField(required=True)
	title = serializers.CharField(required=True)
	description = serializers.CharField(required=False, default="")

	def validate(self, data):
		data = super().validate(data)
		return data


class SharePasswordForUserAPIPostRequestSerializer(serializers.Serializer):
	user_id = serializers.IntegerField(required=True)
	permission_read = serializers.BooleanField(required=False, default=False)
	permission_share = serializers.BooleanField(required=False, default=False)
	permission_update = serializers.BooleanField(required=False, default=False)
	permission_owner = serializers.BooleanField(required=False, default=False)

	def validate(self, data):
		data = super().validate(data)

		user_id = data["user_id"]
		permission_read = data["permission_read"]
		permission_share = data["permission_share"]
		permission_update = data["permission_update"]
		permission_owner = data["permission_owner"]

		if not permission_read and not permission_share and not permission_update and not permission_owner:
			raise serializers.ValidationError({"__global__": "No permission selected"})

		if permission_owner:
			data["permission_read"] = True
			data["permission_share"] = True
			data["permission_update"] = True

		return data

class ChangePasswordOwnerAPIGetRequestSerializer(serializers.Serializer):
	search = serializers.CharField(required=False, default=None)
	limit = serializers.IntegerField(required=False, default=10)

	def validate(self, data):
		data = super().validate(data)

		s = data["search"]
		if s is not None and len(s) > 100:
			raise serializers.ValidationError({"search": ErrorDetail(
				"Search string has exceeded the maximum length (100 characters)",
				code="SEARCH_TOO_LONG"
			)})

		l = data["limit"]
		if l < 1 or l > 50:
			raise serializers.ValidationError({"limit": ErrorDetail(
				"Limit has to be within range: <1, 50>",
				code="LIMIT_OUT_OF_RANGE"
			)})

		return data

class ChangePasswordOwnerAPIPatchRequestSerializer(serializers.Serializer):
	user_id = serializers.IntegerField(required=True)

	def validate(self, data):
		data = super().validate(data)

		try:
			user = User.objects.get(id = data["user_id"])
		except User.DoesNotExist:
			raise serializers.ValidationError({"user_id": ErrorDetail(
				"Requested user does not exist",
				code="USER_DOES_NOT_EXIST"
			)})

		return data

class DeleteUserPasswordAssignmentDeleteRequestSerializer(serializers.Serializer):
	user_id = serializers.IntegerField(required=True)

	def validate(self, data):
		data = super().validate(data)

		return data