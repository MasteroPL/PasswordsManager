from rest_framework import serializers
from django.contrib.auth.models import User
from main.models import Password, UserPasswordAssignment
from main.commons import bytes_to_uuid4str

class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]

# Currently no additional relations for FullUserSerializer, due to which it is identical to UserSerializer (that however might change in the future, when choosing one of the two, take into consideration how much data you want to receive)
class FullUserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]


class MinimalPasswordSerializer(serializers.ModelSerializer):
	class Meta:
		model = Password
		fields = [ "title", "description", "code", "owner", "created_by", "created_at", "updated_by", "updated_at"]

class FullPasswordSerializer(serializers.ModelSerializer):

	owner = UserSerializer()
	created_by = UserSerializer()
	updated_by = UserSerializer()

	class Meta:
		model = Password
		fields = [ "title", "description", "code", "owner", "created_by", "created_at", "updated_by", "updated_at"]


class FullUserPasswordAssignmentSerializer(serializers.ModelSerializer):

	user = UserSerializer()
	created_by = UserSerializer()
	updated_by = UserSerializer()
	password = FullPasswordSerializer()

	class Meta:
		model = UserPasswordAssignment
		fields = ["id", "user", "password", "read", "share", "update", "owner", "created_by", "created_at", "updated_by", "updated_at"]

class UserPasswordAssignmentSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	created_by = UserSerializer()
	updated_by = UserSerializer()
	password = MinimalPasswordSerializer()

	class Meta:
		model = UserPasswordAssignment
		fields = ["id", "user", "password", "read", "share", "update", "owner", "created_by", "created_at", "updated_by", "updated_at"]

