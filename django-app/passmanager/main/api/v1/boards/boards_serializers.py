from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail
from main.models import Board, BoardTab, BoardUserAssignment
from main.models.board_passwords_models import BoardPassword
from main.models.generic_models import GenericPassword

class BoardPasswordAPIResponseSerializer(serializers.Serializer):
    class _BoardPasswordAPIResponsePasswordSerializer(serializers.ModelSerializer):
        class Meta:
            model=GenericPassword
            fields=(
                "title",
                "description",
                "url",
                "username",
                "code"
            )

    password = _BoardPasswordAPIResponsePasswordSerializer()

    class Meta:
        model=BoardPassword
        fields=(
            "password",
            "board_tab"
        )

# ---------
# BoardsAPI
# ---------

class BoardsAPIGetRequestSerializer(serializers.Serializer):
    
    per_page = serializers.IntegerField(default=-1, label="Items per page", help_text="Defines number of items returned per page. -1 means all items will be returned")
    page = serializers.IntegerField(default=1, label="Page to return", help_text="Defines page to return")
    search_text = serializers.CharField(default=None, allow_null=True, allow_blank=True, label="Standard search filter", help_text="Searches by board title and description")

    # Filters might be added here later


    def validate(self, data):
        data = super().validate(data)

        if data["per_page"] < 1 and data["per_page"] != -1:
            raise serializers.ValidationError({
                "per_page": ErrorDetail(
                    "Invalid value. Has to be number greater than 0 or value -1",
                    code="invalid_value"
                )
            })

        if data["page"] < 1 and data["per_page"] != -1:
            raise serializers.ValidationError({
                "page": ErrorDetail(
                    "Invalid value. Has to be number greater than 0",
                    code="invalid_value"
                )
            })

        if data["search_text"] != None and len(data["search_text"]) > 100:
            raise serializers.ValidationError({
                "search_text": ErrorDetail(
                    "Text too long. Search text cannot be longer than 100 characters",
                    code="too_long"
                )
            })

        return data


class BoardsAPIGetResponseSerializer(serializers.Serializer):

    class _BoardsAPIGetResponseBoardSerializer(serializers.ModelSerializer):

        is_owner = serializers.BooleanField()
        is_admin = serializers.BooleanField()

        class Meta:
            model=Board
            fields=(
                "id",
                "name",
                "description",
                "is_owner",
                "is_admin"
            )

    per_page = serializers.IntegerField()
    page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    items = _BoardsAPIGetResponseBoardSerializer(many=True)
    

class BoardsAPIPostRequestSerializer(serializers.ModelSerializer):

    default_tab_name=serializers.CharField(max_length=30, allow_null=True, default=None)

    class Meta:
        model=Board
        fields=(
            "name",
            "description",
            "default_tab_name"
        )


class BoardsAPIPostResponseSerializer(serializers.ModelSerializer):

    default_tab_name=serializers.CharField()

    class Meta:
        model=Board
        fields=(
            "id",
            "name",
            "description",
            "default_tab_name"
        )



# --------
# BoardAPI
# --------

class BoardAPIGetRequestSerializer(serializers.Serializer):
    include_tabs = serializers.BooleanField(default=True)
    include_users = serializers.BooleanField(default=False)
    include_owner = serializers.BooleanField(default=False)


class BoardAPIGetResponseSerializer(serializers.ModelSerializer):

    def __init__(self, *args, fields:list=None, **kwargs):
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop excluded fields
            allowed = set(fields)
            existing = set(self.fields.keys())

            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class _BoardAPiGetResponseOwnerSerializer(serializers.ModelSerializer):
        class Meta:
            model=User
            fields=(
                "id",
                "username",
                "first_name",
                "last_name"
            )

    class _BoardAPIGetResponseUsersSerializer(serializers.ModelSerializer):

        class _BoardAPIGetResponseUsersUserSerializer(serializers.ModelSerializer):
            class Meta:
                model=User
                fields=(
                    "id",
                    "username",
                    "first_name",
                    "last_name"
                )

        user = _BoardAPIGetResponseUsersUserSerializer()

        class Meta:
            model=BoardUserAssignment
            fields=(
                "id",
                "user",
                "perm_admin",
                "perm_create",
                "perm_read",
                "perm_update",
                "perm_delete"
            )

    class _BoardAPIGetResponseTabsSerializer(serializers.ModelSerializer):
        is_default = serializers.SerializerMethodField()

        def get_is_default(self, obj):
            if obj.is_default:
                return True
            else:
                return False

        tab_passwords = BoardPasswordAPIResponseSerializer(many=True)

        class Meta:
            model=BoardTab
            fields=(
                "id",
                "name",
                "is_default",
                "tab_passwords"
            )

    class _BoardAPIGetResponsePermissionsSerializer(serializers.Serializer):
        admin = serializers.BooleanField()
        create = serializers.BooleanField()
        read = serializers.BooleanField()
        update = serializers.BooleanField()
        delete = serializers.BooleanField()

    owner = _BoardAPiGetResponseOwnerSerializer()
    users = serializers.SerializerMethodField()
    tabs = serializers.SerializerMethodField()
    permissions = _BoardAPIGetResponsePermissionsSerializer()

    def get_users(self, obj):
        qs = obj.user_assignments
        return self._BoardAPIGetResponseUsersSerializer(instance=qs, many=True).data

    def get_tabs(self, obj):
        qs = obj.board_tabs
        return self._BoardAPIGetResponseTabsSerializer(instance=qs, many=True).data

    class Meta:
        model=Board
        fields=(
            "id",
            "name",
            "description",
            "tabs",
            "owner",
            "users",
            "permissions"
        )


class BoardAPIPatchRequestSerializer(serializers.ModelSerializer):

    def __init__(self, board_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board_id = board_id

    # owner_id = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all(),
    #     allow_null=False,
    #     required=False
    # )
    owner_id = serializers.IntegerField(required=False, allow_null=False)

    def validate(self, data):
        data = super().validate(data)

        if data.__contains__("owner_id"):
            tmp_qs = BoardUserAssignment.objects.filter(
                board_id = self.board_id
            ).values_list("user_id", flat=True)

            try:
                new_owner = User.objects.filter(
                    pk__in=tmp_qs
                ).get(pk=data["owner_id"])
                data["owner"] = new_owner
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "owner_id": ErrorDetail(
                        "User not found",
                        code="not_found"
                    )
                })

        return data

    class Meta:
        model=Board
        fields=(
            "owner_id",
            "name",
            "description"
        )

class BoardAPIPatchResponseSerializer(serializers.ModelSerializer):
    
    class _BoardAPIPatchResponseOwnerSerializer(serializers.ModelSerializer):
        class Meta:
            model=User
            fields=(
                "id",
                "username",
                "first_name",
                "last_name"
            )

    owner = _BoardAPIPatchResponseOwnerSerializer()

    class Meta:
        model=Board
        fields=(
            "owner",
            "name",
            "description"
        )


class BoardAssignmentsAPIGetRequestSerializer(serializers.Serializer):
    per_page = serializers.IntegerField(default=-1, label="Items per page", help_text="Defines number of items returned per page. -1 means all items will be returned")
    page = serializers.IntegerField(default=1, label="Page to return", help_text="Defines page to return")
    search_text = serializers.CharField(default=None, allow_null=True, allow_blank=True, label="Standard search filter", help_text="Searches by username")

    # Filters might be added here later


    def validate(self, data):
        data = super().validate(data)

        if data["per_page"] < 1 and data["per_page"] != -1:
            raise serializers.ValidationError({
                "per_page": ErrorDetail(
                    "Invalid value. Has to be number greater than 0 or value -1",
                    code="invalid_value"
                )
            })

        if data["page"] < 1 and data["per_page"] != -1:
            raise serializers.ValidationError({
                "page": ErrorDetail(
                    "Invalid value. Has to be number greater than 0",
                    code="invalid_value"
                )
            })

        if data["search_text"] != None and len(data["search_text"]) > 100:
            raise serializers.ValidationError({
                "search_text": ErrorDetail(
                    "Text too long. Search text cannot be longer than 100 characters",
                    code="too_long"
                )
            })

        return data



class BoardAssignmentsAPIGetResponseSerializer(serializers.Serializer):

    class _BoardAssignmentsAPIGetResponseAssignmentSerializer(serializers.ModelSerializer):

        class _BoardAssignmentsAPIGetResponseUserSerializer(serializers.ModelSerializer):
            class Meta:
                model=User
                fields=(
                    "id",
                    "username",
                    "first_name",
                    "last_name"
                )

        user = _BoardAssignmentsAPIGetResponseUserSerializer()

        class Meta:
            model=BoardUserAssignment
            fields=(
                "id",
                "user",
                "perm_admin",
                "perm_create",
                "perm_read",
                "perm_update",
                "perm_delete"
            )

    per_page = serializers.IntegerField()
    page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    items = _BoardAssignmentsAPIGetResponseAssignmentSerializer(many=True)



class BoardAssignmentsAPIPostRequestSerializer(serializers.ModelSerializer):

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=False,
        required=True
    )

    class Meta:
        model=BoardUserAssignment
        fields=(
            "user_id",
            "perm_admin",
            "perm_create",
            "perm_read",
            "perm_update",
            "perm_delete"
        )

    def validate(self, data):
        data = super().validate(data)

        data["user"] = data["user_id"]
        data.pop("user_id")

        return data


class BoardAssignmentsAPIPostResponseSerializer(serializers.ModelSerializer):

    class _BoardAssignmentsAPIPostResponseUserSerializer(serializers.ModelSerializer):
        class Meta:
            model=User
            fields=(
                "id",
                "username",
                "first_name",
                "last_name"
            )

    user = _BoardAssignmentsAPIPostResponseUserSerializer()

    class Meta:
        model=BoardUserAssignment
        fields=(
            "id",
            "user",
            "perm_admin",
            "perm_create",
            "perm_read",
            "perm_update",
            "perm_delete"
        )



class BoardAssignmentAPIGetResponseSerializer(serializers.ModelSerializer):

    class _BoardAssignmentAPIGetResponseUserSerializer(serializers.ModelSerializer):
        class Meta:
            model=User
            fields=(
                "id",
                "username",
                "first_name",
                "last_name"
            )

    user = _BoardAssignmentAPIGetResponseUserSerializer()

    class Meta:
        model=BoardUserAssignment
        fields=(
            "id",
            "user",
            "perm_admin",
            "perm_create",
            "perm_read",
            "perm_update",
            "perm_delete"
        )


class BoardAssignmentAPIPatchRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model=BoardUserAssignment
        fields=(
            "perm_admin",
            "perm_create",
            "perm_read",
            "perm_update",
            "perm_delete"
        )


class BoardAssignmentAPIPatchResponseSerializer(serializers.ModelSerializer):
    
    user_id = serializers.SerializerMethodField()
    def get_user_id(self, obj):
        return obj.user_id
    
    class Meta:
        model=BoardUserAssignment
        fields=(
            "id",
            "user_id",
            "perm_admin",
            "perm_create",
            "perm_read",
            "perm_update",
            "perm_delete"
        )


class BoardAssignmentsUsersSearchAPIGetRequestSerializer(serializers.Serializer):
    search_text = serializers.CharField(max_length=256, allow_blank=True)

class BoardAssignmentsUsersSearchAPIGetResponseSerializer(serializers.ModelSerializer):

    search_value = serializers.CharField()

    # def get_search_value(self, obj):
    #     username = obj.username
    #     first_name = obj.first_name if obj.first_name is not None else ""
    #     last_name = obj.last_name if obj.last_name is not None else ""

    #     return username + " (" + last_name + " " + first_name + ")" 

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "search_value"
        )


# -------------
# BoardTabs API 
# -------------

class BoardTabsAPIGetResponseSerializer(serializers.ModelSerializer):

    is_default = serializers.SerializerMethodField()
    def get_is_default(self, obj):
        if obj.is_default is not None:
            return True
        return False

    tab_passwords = BoardPasswordAPIResponseSerializer(many=True)
    class Meta:
        model=BoardTab
        fields=(
            "id",
            "name",
            "is_default",
            "tab_passwords"
        )

class BoardTabsAPIPostRequestSerializer(serializers.ModelSerializer):

    def __init__(self, board_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board_id = board_id

    add_after = serializers.IntegerField(default=None, allow_null=True)

    class Meta:
        model=BoardTab
        fields=(
            "name",
            "add_after"
        )

    def validate(self, data):
        data = super().validate(data)

        if data["add_after"] is not None and not BoardTab.objects.filter(board_id=self.board_id, id=data["add_after"]).exists():
            raise serializers.ValidationError({
                "add_after": ErrorDetail(
                    "Requested tab id has not been found",
                    code="tab_not_found"
                )
            })

        return data



class BoardTabAPIPatchRequestSerializer(serializers.ModelSerializer):

    def __init__(self, board_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board_id = board_id

    put_after = serializers.IntegerField(allow_null=True)

    class Meta:
        model=BoardTab
        fields=(
            "name",
            "put_after"
        )


    def validate(self, data):
        data = super().validate(data)

        if data.__contains__("put_after") and data["put_after"] is not None and not BoardTab.objects.filter(board_id=self.board_id, id=data["put_after"]).exists():
            raise serializers.ValidationError({
                "put_after": ErrorDetail(
                    "Requested tab id has not been found",
                    code="tab_not_found"
                )
            })

        return data

class BoardTabAPIDeleteRequestSerializer(serializers.Serializer):
    
    def __init__(self, board_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board_id = board_id

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
                data["move_passwords_to_tab"] = BoardTab.objects.get(
                    board_id=self.board_id,
                    id=data["move_passwords_to_tab_id"]
                )
            except BoardTab.DoesNotExist:
                raise serializers.ValidationError({
                    "move_passwords_to_tab_id": ErrorDetail(
                        "Tab not found",
                        code="not_found"
                    )
                })

        return data



class BoardPasswordsAPIPostRequestSerializer(serializers.Serializer):

    def __init__(self, board_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board_id = board_id

    password=serializers.CharField(max_length=128, required=True)
    title=serializers.CharField(max_length=50, required=True)
    description=serializers.CharField(max_length=1000, required=False, allow_null=True, default=None)
    url=serializers.CharField(max_length=100, required=False, allow_null=True, default=None)
    username=serializers.CharField(max_length=100, required=False, allow_null=True, default=None)

    board_tab_id=serializers.IntegerField(required=True)

    def validate(self, data):
        data = super().validate(data)

        try:
            obj = BoardTab.objects.get(
                board_id=self.board_id,
                id=data["board_tab_id"]
            )
        except BoardTab.DoesNotExist:
            raise serializers.ValidationError({
                "board_tab_id": ErrorDetail(
                    "Board tab has not been found",
                    code="not_found"
                )
            })

        data["board_tab"] = obj

        return data



class BoardPasswordsAPIPatchRequestSerializer(serializers.Serializer):

    def __init__(self, board_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board_id = board_id

    password=serializers.CharField(max_length=128)
    title=serializers.CharField(max_length=50)
    description=serializers.CharField(max_length=1000, allow_null=True)
    url=serializers.CharField(max_length=100, allow_null=True)
    username=serializers.CharField(max_length=100, allow_null=True)

    board_tab_id=serializers.IntegerField(allow_null=True)

    def validate(self, data):
        data = super().validate(data)

        if data.__contains__("board_tab_id"):
            try:
                obj = BoardTab.objects.get(
                    board_id=self.board_id,
                    id=data["board_tab_id"]
                )
            except BoardTab.DoesNotExist:
                raise serializers.ValidationError({
                    "board_tab_id": ErrorDetail(
                        "Board tab has not been found",
                        code="not_found"
                    )
                })

            data["board_tab"] = obj

        return data