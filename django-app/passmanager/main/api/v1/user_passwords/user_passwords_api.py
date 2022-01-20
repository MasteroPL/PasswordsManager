from os import read
from django.contrib.auth.models import User
from django.db.models.expressions import Case, Value, When
from django.db.models.query import Prefetch
from django.db.models.query_utils import Q
from django.http.response import Http404
from main.models import Board
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import serializers, status
from main.commons import serialization_errors_to_response
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError as CoreValidationError
from django.db import transaction


from main.models import (
    UserPassword,
    UserPasswordShare,
    UserTab
)
from main.utils.board_tabs_builder import CannotDeleteDefaultTabError
from .user_passwords_serializers import (
    UserPasswordResponseSerializer,
    UserPasswordResponseWithOwnerSerializer,
    UserPasswordsAPIPostRequestSerializer,
    UserPasswordsAPIGetResponseSerializer,
    UserPasswordAPIPatchRequestSerializer,
    UserPasswordShareResponseSerializer,
    UserPasswordShareResponseWithOwnerSerializer,
    UserPasswordSharesPostRequestSerializer,
    UserPasswordDuplicateAPIPostRequestSerializer,
    UserTabsAPIPostRequestSerializer,
    UserTabsAPIGetResponseSerializer,
    UserTabAPIPatchRequestSerializer,
    UserTabAPIDeleteRequestSerializer,
    UserPasswordShareSearchUserRequestSerializer,
    UserPasswordShareSearchUserResponseSerializer
)

from main.utils.user_tabs_builder import UserTabsBuilder, UserTabNotFoundError


class UserPasswordsAPI(GenericAPIView):
    def post(self, request, format=None):

        serializer = UserPasswordsAPIPostRequestSerializer(request.user.id, data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            user_password = UserPassword.create(
                request.user.id,
                data["user_tab_id"],
                data["password"],
                data["title"],
                description=data["description"],
                url=data["url"],
                username=data["username"],
                commit=True
            )

            response = UserPasswordResponseSerializer(instance=user_password)
            return Response(data=response.data, status=status.HTTP_201_CREATED)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):

        tabs = UserTab.objects.filter(user_id=request.user.id).order_by('order').prefetch_related(
            Prefetch(
                "tab_passwords", to_attr="passwords",
                queryset=UserPassword.objects.prefetch_related(
                    Prefetch(
                        "password_shares",
                        queryset=UserPasswordShare.objects.prefetch_related("user").order_by("user__username")
                    )
                ).order_by("password__title")
            ),
            "passwords__password"
        )

        shared_passwords = UserPassword.objects.filter(
            password_shares__user_id=request.user.id
        ).distinct().prefetch_related(
            "password",
            "user"
        ).order_by("password__title")

        response = UserPasswordsAPIGetResponseSerializer(instance={
            "tabs": tabs,
            "shared": shared_passwords
        })
        return Response(data=response.data, status=status.HTTP_200_OK)



class UserPasswordAPI(GenericAPIView):

    def get_object(self, user_id:int, password_code:str):
        share_exist = UserPasswordShare.objects.filter(
            user_id=user_id,
            user_password__password__code=password_code
        ).exists()

        obj = UserPassword.objects.select_related("password").prefetch_related(
            Prefetch(
                "password_shares",
                queryset=UserPasswordShare.objects.prefetch_related("user").order_by("user__username")
            )
        ).get(
            password__code=password_code
        )

        if obj.user_id != user_id and not share_exist:
            raise UserPassword.DoesNotExist()

        return obj, share_exist



    def get(self, request, password_code:str, format=None):
        try:
            obj, share_exists = self.get_object(request.user.id, password_code)
        except UserPassword.DoesNotExist:
            raise Http404()

        response = UserPasswordResponseSerializer(instance=obj)
        return Response(data=response.data, status=status.HTTP_200_OK)

    def patch(self, request, password_code:str, format=None):
        try:
            obj, share_exists = self.get_object(request.user.id, password_code)
        except UserPassword.DoesNotExist:
            raise Http404()

        if obj.user_id != request.user.id:
            if not share_exists:
                raise Http404()
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = UserPasswordAPIPatchRequestSerializer(user_id=request.user.id, data=request.data, partial=True)

        if serializer.is_valid():
            data = serializer.validated_data
            if len(data) == 0:
                return Response(data={
                    "detail": "Nothing to update",
                    "code": "empty_request"
                }, status=status.HTTP_400_BAD_REQUEST)

            new_password_request = False
            if data.__contains__("password"):
                new_password_request = True
                new_password = data.pop("password")

            new_user_tab_requested = False
            if data.__contains__("user_tab_id"):
                new_user_tab_requested = True
                new_user_tab_id = data.pop("user_tab_id")

            with transaction.atomic():
                for key, value in data.items():
                    setattr(obj.password, key, value)

                if new_password_request:
                    obj.password.change_password(new_password, commit=False)

                if new_user_tab_requested:
                    obj.user_tab_id = new_user_tab_id

                obj.password.save()
                obj.save()

                response = UserPasswordResponseSerializer(instance=obj)
                return Response(data=response.data, status=status.HTTP_200_OK)


        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, password_code:str, format=None):
        try:
            obj, share_exists = self.get_object(request.user.id, password_code)
        except UserPassword.DoesNotExist:
            raise Http404()

        if obj.user_id != request.user.id:
            if not share_exists:
                raise Http404()
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        obj.remove()

        return Response(status=status.HTTP_204_NO_CONTENT)

        

class UserPasswordCopyAPI(GenericAPIView):

    def post(self, request, password_code:str, format=None):
        share_exist = UserPasswordShare.objects.filter(
            user_id=request.user.id,
            user_password__password__code=password_code
        ).exists()

        try:
            obj = UserPassword.objects.select_related("password").get(
                password__code=password_code
            )
        except UserPassword.DoesNotExist:
            raise Http404()

        if obj.user_id != request.user.id and not share_exist:
            raise Http404()

        password = obj.password.read()

        return Response(data=password, status=status.HTTP_200_OK)


class UserPasswordSharesAPI(GenericAPIView):
    
    def get_object(self, password_code:str, user_id:int):
        qs = UserPassword.objects.filter(
            Q(user_id=user_id)
            |Q(password_shares__user_id=user_id)
        ).distinct()

        return qs.select_related("password").get(
            password__code=password_code
        )

    def post(self, request, password_code:str, format=None):
        try:
            obj = self.get_object(password_code, request.user.id)
        except UserPassword.DoesNotExist:
            raise Http404()

        if obj.user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = UserPasswordSharesPostRequestSerializer(password_code, data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            new_share = UserPasswordShare(
                user=data["user"],
                user_password=obj
            )

            new_share.save()

            response = UserPasswordShareResponseSerializer(instance=new_share)
            return Response(data=response.data, status=status.HTTP_201_CREATED)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
        

    def get(self, request, password_code:str, format=None):
        try:
            obj = self.get_object(password_code, request.user.id)
        except UserPassword.DoesNotExist:
            raise Http404()

        if obj.user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)

        qs = UserPasswordShare.objects.filter(
            user_password__password__code=password_code
        ).prefetch_related("user", "user_password", "user_password__password", "user_password__user")

        response = UserPasswordResponseSerializer(instance=qs, many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)


class UserPasswordShareAPI(GenericAPIView):

    def get_object(self, password_code:str, share_id:int, user_id:int, select_related:tuple=None):
        if select_related is None:
            tmp = (
                "user",
                "user_password",
                "user_password__password",
                "user_password__user"
            )
        else:
            tmp = select_related

        obj = UserPasswordShare.objects.filter(
            Q(user_password__user_id=user_id)
            |Q(user_password__password_shares__user_id=user_id),
            user_password__password__code=password_code
        ).distinct().select_related(
            *tmp
        ).get(id=share_id)

        return obj

    def get(self, request, password_code:str, share_id:int, format=None):
        try:
            obj = self.get_object(password_code, share_id, request.user.id)
        except UserPasswordShare.DoesNotExist:
            raise Http404()

        response = UserPasswordShareResponseWithOwnerSerializer(instance = obj)
        return Response(data=response.data, status=status.HTTP_200_OK)


    def delete(self, request, password_code:str, share_id:int, format=None):
        try:
            obj = self.get_object(password_code, share_id, request.user.id, select_related=(
                "user_password",
                "user_password__user"
            ))
        except UserPasswordShare.DoesNotExist:
            raise Http404()

        if obj.user_password.user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)

        obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPasswordMySharesAPI(GenericAPIView):

    def get(self, request, format=None):
        qs = UserPassword.objects.filter(
            password_shares__user_id=request.user.id
        ).prefetch_related("user", "password").distinct()

        response = UserPasswordResponseWithOwnerSerializer(instance=qs, many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)

class UserPasswordDuplicateAPI(GenericAPIView):

    def get_object(self, password_code:str, user_id:int):
        obj = UserPassword.objects.select_related("password").get(
            Q(user_id=user_id)
            |Q(password_shares__user_id=user_id),
            password__code=password_code
        )
        return obj

    def post(self, request, password_code:str, format=None):
        try:
            obj = self.get_object(password_code, request.user.id)
        except UserPassword.DoesNotExist:
            raise Http404()

        serializer = UserPasswordDuplicateAPIPostRequestSerializer(request.user.id, data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            duplicated_password = obj.duplicate(
                owner_id=request.user.id,
                tab_id=data["tab_id"]
            )

            response = UserPasswordResponseSerializer(instance=duplicated_password)
            return Response(data=response.data, status=status.HTTP_201_CREATED)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

        


class UserTabsAPI(GenericAPIView):

    def post(self, request, format=None):
        
        serializer = UserTabsAPIPostRequestSerializer(request.user.id, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            builder = UserTabsBuilder(request.user.id)
            if data["add_after"] is not None:
                try:
                    builder.insert_tab_after_id(data["name"], data["add_after"])
                except UserTabNotFoundError:
                    return Response(data={
                        "add_after": {
                            "string": "Tab ID not found",
                            "code": "not_found"
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)

            else:
                builder.prepend_tab(data["name"])

            builder.save()

            objects = UserTab.objects.filter(user_id=request.user.id).prefetch_related(
                Prefetch(
                    "tab_passwords", to_attr="passwords",
                    queryset=UserPassword.objects.select_related("password").order_by("password__title")
                ),
            ).order_by("order")

            response = UserTabsAPIGetResponseSerializer(instance = objects, many=True)
            return Response(data=response.data, status=status.HTTP_201_CREATED)


        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        objects = UserTab.objects.filter(user_id=request.user.id).prefetch_related(
            Prefetch(
                "tab_passwords", to_attr="passwords",
                queryset=UserPassword.objects.select_related("password").order_by("password__title")
            ),
        ).order_by("order")

        response = UserTabsAPIGetResponseSerializer(instance = objects, many=True)
        return Response(data=response.data, status=status.HTTP_201_CREATED)


class UserTabAPI(GenericAPIView):

    def get(self, request, tab_id:int, format=None):
        try:
            obj = UserTab.objects.get(
                id=tab_id,
                user_id=request.user.id
            ).prefetch_related(
                Prefetch(
                    "tab_passwords",
                    queryset=UserPassword.objects.order_by("password__title")
                ),
                "tab_passwords__password"
            )
        except UserTab.DoesNotExist:
            raise Http404()

        response = UserTabsAPIGetResponseSerializer(instance=obj)
        return Response(data=response.data, status=status.HTTP_200_OK)


    def patch(self, request, tab_id:int, format=None):
        try:
            obj = UserTab.objects.get(
                id=tab_id,
                user_id=request.user.id
            )
        except UserTab.DoesNotExist:
            raise Http404()

        serializer = UserTabAPIPatchRequestSerializer(request.user.id, data=request.data)
        if serializer.is_valid():
            builder = UserTabsBuilder(request.user.id)
            data = serializer.validated_data

            if data.__contains__("name"):
                obj.name = data["name"]
            if data.__contains__("put_after"):
                try:
                    builder.change_tab_order(tab_id, data["put_after"])
                except UserTabNotFoundError:
                    return Response(data={
                        "put_after": {
                            "string": "Tab not found",
                            "code": "not_found"
                        }
                    })

            builder.save()

            objects = UserTab.objects.filter(user_id=request.user.id).prefetch_related(
                Prefetch(
                    "tab_passwords", to_attr="passwords",
                    queryset=UserPassword.objects.select_related("password").order_by("password__title")
                ),
            ).order_by("order")

            response = UserTabsAPIGetResponseSerializer(instance = objects, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, tab_id:int, format=None):
        try:
            obj = UserTab.objects.get(
                id=tab_id,
                user_id=request.user.id
            )
        except UserTab.DoesNotExist:
            raise Http404()

        serializer = UserTabAPIDeleteRequestSerializer(request.user.id, data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            builder = UserTabsBuilder(request.user.id)
            try:
                builder.delete_tab(
                    tab_id, 
                    delete_passwords=data["remove_passwords"],
                    move_to_tab=data["move_passwords_to_tab_id"]
                )
            except CannotDeleteDefaultTabError:
                return Response({
                    "detail": "Cannot delete default tab",
                    "code": "cannot_delete_default"
                })

            builder.save()

            objects = UserTab.objects.filter(user_id=request.user.id).prefetch_related(
                Prefetch(
                    "tab_passwords", to_attr="passwords",
                    queryset=UserPassword.objects.select_related("password").order_by("password__title")
                ),
            ).order_by("order")

            response = UserTabsAPIGetResponseSerializer(instance = objects, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordShareSearchUserAPI(GenericAPIView):
    def get(self, request, password_code:str, format=None):
        try:
            obj = UserPassword.objects.get(
                password__code=password_code,
                user=request.user
            )
        except UserPassword.DoesNotExist:
            raise Http404()

        serializer = UserPasswordShareSearchUserRequestSerializer(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            
            exclude_ids = UserPasswordShare.objects.filter(
                user_password=obj
            ).values_list("user_id", flat=True)

            users_annotate = User.objects.annotate(
                search_value=Concat(
                    "username",
                    V(" ("),
                    "last_name",
                    V(" "),
                    "first_name",
                    V(")")
                )
            )

            if data["search_text"] is None or data["search_text"] == "":
                users_qs = users_annotate.all(
                ).exclude(
                    Q(id__in=exclude_ids)|Q(id=obj.user_id)
                )[:10]
            else:
                users_qs = users_annotate.filter(
                    search_value__icontains=data["search_text"]
                ).exclude(
                    Q(id__in=exclude_ids)|Q(id=obj.user_id)
                )[:10]

            response = UserPasswordShareSearchUserResponseSerializer(instance=users_qs, many=True)

            return Response(data=response.data, status=status.HTTP_200_OK)

        errors = serialization_errors_to_response(serializer.errors)
        return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
