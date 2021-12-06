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

class UserPasswordResponseWithOwnerSerializer(serializers.ModelSerializer):
    class _UserPasswordResponseWithOwnerGenericPasswordSerializer(serializers.ModelSerializer):
        class Meta:
            model = GenericPassword
            fields=(
                "title",
                "description",
                "url",
                "username",
                "code"
            )

    class _UserPasswordResponseWithOwnerOwnerSerializer(serializers.ModelSerializer):
        class Meta:
            model=User
            fields = (
                "id",
                "username",
                "first_name",
                "last_name",
                "email"
            )

    password = _UserPasswordResponseWithOwnerGenericPasswordSerializer()
    user = _UserPasswordResponseWithOwnerOwnerSerializer()

    class Meta:
        model = UserPassword
        fields = (
            "password",
            "user"
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



class UserPasswordsTabsResponseSerializer(serializers.ModelSerializer):

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

class UserPasswordsAPIGetResponseSerializer(serializers.Serializer):

    tabs = UserPasswordsTabsResponseSerializer(many=True)
    shared = UserPasswordResponseWithOwnerSerializer(many=True)


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


class UserPasswordShareResponseSerializer(serializers.ModelSerializer):

    class _UserPasswordShareResponseUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                "id",
                "username",
                "first_name",
                "last_name",
                "email"
            )

    class _UserPasswordShareResponseUserPasswordSerializer(serializers.ModelSerializer):

        class _UserPasswordShareResponseGenericPasswordSerializer(serializers.ModelSerializer):
            class Meta:
                model = GenericPassword
                fields = (
                    "title",
                    "description",
                    "url",
                    "username",
                    "code"
                )

        password = _UserPasswordShareResponseGenericPasswordSerializer()
        
        class Meta:
            model = UserPassword
            fields = (
                "password",
            )

    user = _UserPasswordShareResponseUserSerializer()
    user_password = _UserPasswordShareResponseUserPasswordSerializer()
    
    class Meta:
        model = UserPasswordShare
        fields = (
            "id",
            "user",
            "user_password"
        )

class UserPasswordShareResponseWithOwnerSerializer(serializers.ModelSerializer):

    class _UserPasswordShareResponseWithOwnerUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                "id",
                "username",
                "first_name",
                "last_name",
                "email"
            )

    class _UserPasswordShareResponseWithOwnerUserPasswordSerializer(serializers.ModelSerializer):

        class _UserPasswordShareResponseWithOwnerGenericPasswordSerializer(serializers.ModelSerializer):
            class Meta:
                model = GenericPassword
                fields = (
                    "title",
                    "description",
                    "url",
                    "username",
                    "code"
                )

        class _UserPasswordShareResponseWithOwnerOwnerSerializer(serializers.ModelSerializer):
            class Meta:
                model = User
                fields = (
                    "id",
                    "username",
                    "first_name",
                    "last_name",
                    "email"
                )

        password = _UserPasswordShareResponseWithOwnerGenericPasswordSerializer()
        user = _UserPasswordShareResponseWithOwnerOwnerSerializer()
        class Meta:
            model = UserPassword
            fields = (
                "password",
                "user"
            )

    user = _UserPasswordShareResponseWithOwnerUserSerializer()
    user_password = _UserPasswordShareResponseWithOwnerUserPasswordSerializer()
    
    class Meta:
        model = UserPasswordShare
        fields = (
            "id",
            "user",
            "user_password"
        )



class UserPasswordSharesPostRequestSerializer(serializers.Serializer):

    def __init__(self, password_code:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_code = password_code

    user_id = serializers.IntegerField()

    def validate(self, data):
        data = super().validate(data)

        if data.__contains__("user_id"):
            already_exists = UserPasswordShare.objects.filter(
                user_password__password__code=self.password_code,
                user_id=data["user_id"]
            ).exists()

            invalid_share = UserPassword.objects.filter(
                user_id=data["user_id"],
                password__code=self.password_code
            ).exists()

            try:
                data["user"] = User.objects.get(id=data["ser_id"])
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "user_id": ErrorDetail(
                        "User not found",
                        code="not_found"
                    )
                })

            if already_exists:
                raise serializers.ValidationError({
                    "user_id": ErrorDetail(
                        "User already assigned to password",
                        code="already_assigned"
                    )
                })

            if invalid_share:
                raise serializers.ValidationError({
                    "user_id": ErrorDetail(
                        "Cannot share password to yourself",
                        code="share_self"
                    )
                })

        return data


class UserPasswordDuplicateAPIPostRequestSerializer(serializers.Serializer):
    
    def __init__(self, user_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_id = user_id

    tab_id = serializers.IntegerField()

    def validate(self, data):
        data = super().validate(data)

        if data.__contains__("tab_id"):
            try:
                data["tab"] = UserTab.objects.get(
                    user_id=self.user_id,
                    id=data["tab_id"]
                )
            except UserTab.DoesNotExist:
                raise serializers.ValidationError({
                    "tab_id": ErrorDetail(
                        "Tab not found",
                        code="not_found"
                    )
                })

        return data


class UserTabsAPIGetResponseSerializer(serializers.ModelSerializer):

    is_default = serializers.SerializerMethodField()
    def get_is_default(self, obj):
        if obj.is_default is not None:
            return True
        return False

    tab_passwords = UserPasswordResponseSerializer(many=True)
    class Meta:
        model=UserTab
        fields=(
            "id",
            "name",
            "is_default",
            "tab_passwords"
        )

class UserTabsAPIPostRequestSerializer(serializers.ModelSerializer):

    def __init__(self, user_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_id = user_id

    add_after = serializers.IntegerField(default=None, allow_null=True)

    class Meta:
        model=UserTab
        fields=(
            "name",
            "add_after"
        )

    def validate(self, data):
        data = super().validate(data)

        if data["add_after"] is not None and not UserTab.objects.filter(user_id=self.user_id, id=data["add_after"]).exists():
            raise serializers.ValidationError({
                "add_after": ErrorDetail(
                    "Requested tab id has not been found",
                    code="not_found"
                )
            })

        return data



class UserTabAPIPatchRequestSerializer(serializers.ModelSerializer):

    def __init__(self, user_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_id = user_id

    put_after = serializers.IntegerField(allow_null=True)

    class Meta:
        model=UserTab
        fields=(
            "name",
            "put_after"
        )


    def validate(self, data):
        data = super().validate(data)

        if data.__contains__("put_after") and data["put_after"] is not None and not UserTab.objects.filter(board_id=self.user_id, id=data["put_after"]).exists():
            raise serializers.ValidationError({
                "put_after": ErrorDetail(
                    "Requested tab id has not been found",
                    code="not_found"
                )
            })

        return data

class UserTabAPIDeleteRequestSerializer(serializers.Serializer):
    
    def __init__(self, user_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_id = user_id

    remove_passwords = serializers.BooleanField(required=False, default=True)
    move_passwords_to_tab_id = serializers.IntegerField(required=False, default=None)

    def validate(self, data):
        data = super().validate(data)

        if not data["remove_passwords"]:
            if data["move_passwords_to_tab_id"] is None:
                raise serializers.ValidationError({
                    "move_passwords_to_tab_id": ErrorDetail(
                        "If remove_passwords is False, this field is required",
                        code="conditionally_required"
                    )
                })

            try:
                data["move_passwords_to_tab"] = UserTab.objects.get(
                    user_id=self.user_id,
                    id=data["move_passwords_to_tab_id"]
                )
            except UserTab.DoesNotExist:
                raise serializers.ValidationError({
                    "move_passwords_to_tab_id": ErrorDetail(
                        "Tab not found",
                        code="not_found"
                    )
                })

        return data