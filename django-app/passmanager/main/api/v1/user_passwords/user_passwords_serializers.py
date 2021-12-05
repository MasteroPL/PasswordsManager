from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from main.models import (
    UserPassword,
    UserPasswordShare,
    UserTab
)

from main.models.generic_models import GenericPassword



class UserPasswordResponseSerializer(serializers.ModelSerializer):
    class _UserPasswordResponseGenericPasswordSerializer(serializers.ModelSerializer):
        class Meta:
            model = GenericPassword
            fields=(
                "title",
                "description",
                "url",
                "username",
                "code"
            )

    password = _UserPasswordResponseGenericPasswordSerializer()
    user_tab_id = serializers.SerializerMethodField()
    def get_user_tab_id(self, obj):
        return obj.user_tab_id

    class Meta:
        model = UserPassword
        fields = (
            "password",
            "user_tab_id"
        )



class UserPasswordsAPIPostRequestSerializer(serializers.Serializer):

    def __init__(self, user_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_id = user_id

    
    password = serializers.CharField(max_length=128, required=True)
    user_tab_id = serializers.IntegerField(required=True)
    title = serializers.CharField(max_length=50, required=True)
    description = serializers.CharField(max_length=1000, required=False, allow_null=True, default=None)
    url = serializers.CharField(max_length=100, required=False, allow_null=True, default=None)
    username = serializers.CharField(max_length=100, required=False, allow_null=True, default=None)
    
    def validate(self, data):
        data = super().validate(data)

        try:
            user_tab = UserTab.objects.get(
                user_id=self.user_id,
                id=data["user_tab_id"]
            )
        except UserTab.DoesNotExist:
            raise serializers.ValidationError({
                "user_tab_id": ErrorDetail(
                    "User tab was not found",
                    code="not_found"
                )
            })

        data["user_tab"] = user_tab

        return data



class UserPasswordsAPIGetResponseSerializer(serializers.ModelSerializer):

    class _UserPasswordsAPIGetResponseUserPasswordSerializer(serializers.ModelSerializer):
        class _UserPasswordsAPIGetResponseGenericPasswordSerializer(serializers.ModelSerializer):
            class Meta:
                model = GenericPassword
                fields=(
                    "title",
                    "description",
                    "url",
                    "username",
                    "code"
                )

        password = _UserPasswordsAPIGetResponseGenericPasswordSerializer()

        class Meta:
            model = UserPassword
            fields = (
                "password",
            )

    is_default = serializers.SerializerMethodField()
    def get_is_default(self, obj):
        return True if obj.is_default is not None else False

    passwords = _UserPasswordsAPIGetResponseUserPasswordSerializer(many=True)

    class Meta:
        model = UserTab
        fields = (
            'id',
            'name',
            'is_default',
            'passwords'
        )



class UserPasswordAPIPatchRequestSerializer(serializers.Serializer):

    def __init__(self, user_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_id = user_id

    
    password = serializers.CharField(max_length=128, required=False)
    user_tab_id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(max_length=1000, required=False, allow_null=True)
    url = serializers.CharField(max_length=100, required=False, allow_null=True)
    username = serializers.CharField(max_length=100, required=False, allow_null=True)
    
    def validate(self, data):
        data = super().validate(data)

        if data.__contains__("user_tab_id"):
            try:
                user_tab = UserTab.objects.get(
                    user_id=self.user_id,
                    id=data["user_tab_id"]
                )
            except UserTab.DoesNotExist:
                raise serializers.ValidationError({
                    "user_tab_id": ErrorDetail(
                        "User tab was not found",
                        code="not_found"
                    )
                })

            data["user_tab"] = user_tab

        return data