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
from .user_passwords_serializers import (
    UserPasswordResponseSerializer,
    UserPasswordsAPIPostRequestSerializer,
    UserPasswordsAPIGetResponseSerializer,
    UserPasswordAPIPatchRequestSerializer
)


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
                queryset=UserPassword.objects.order_by("password__title")
            ),
            "passwords__password"
        )

        response = UserPasswordsAPIGetResponseSerializer(instance=tabs, many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)



class UserPasswordAPI(GenericAPIView):

    def get_object(self, user_id:int, password_code:str):
        share_exist = UserPasswordShare.objects.filter(
            user_id=user_id,
            user_password__password__code=password_code
        ).exists()

        obj = UserPassword.objects.select_related("password").get(
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


class UserPasswordShares(GenericAPIView):
    
    def post(self, request, password_code:str, format=None):
        pass


    def get(self, request, password_code:str, format=None):
        pass