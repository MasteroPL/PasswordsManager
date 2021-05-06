from rest_framework import serializers
from django.contrib.auth.models import User
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