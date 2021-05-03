from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.http import Http404
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from main.generic_serializers import FullUserSerializer
from django.core.serializers import serialize
from rest_framework import permissions as rest_permissions

def test_user_can_login(user:User):
    if not user.is_active:
        raise AccountInactive()

def user_login(request, username:str, password:str):
    '''
    Logs user in if credentials are valid and account configuration are valid for login

    :throws AccountInactive: thrown if account is inactive
    :throws InvalidCredentialsError: thrown the credentials provided were invalid
    '''
    user = authenticate(username=username, password=password)

    if user is not None:
        test_user_can_login(user)
        login(request, user)
    
    raise InvalidCredentialsError()


def user_logout(user:User):
    logout(user)


class LoginAPISerializer(serializers.Serializer):
    login = serializers.CharField(required=True, allow_blank=False, max_length=100)
    password = serializers.CharField(required=True, allow_blank=False, max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, data):
        data = super().validate(data)

        user = authenticate(username=data["login"], password=data["password"])
        if user is None:
            raise serializers.ValidationError({None: "Invalid username or password"})

        self.user = user

        return data

def get_user_payload(user:User):
    return FullUserSerializer(user).data


class LoginAPI(APIView):
    permission_classes = [
    ]

    serializer_class = LoginAPISerializer

    def post(self, request, format=None):
        serializer = LoginAPISerializer(data=request.POST)
        if serializer.is_valid():
            try:
                test_user_can_login(serializer.user)
            except AccountInactive:
                return Response({
                    "__gobal__": "Account is inactive"
                }, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({
                    "__gobal__": "Internal server error occured"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            refresh = RefreshToken.for_user(serializer.user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "payload": get_user_payload(serializer.user)
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginError(Exception):
    pass

class InvalidCredentialsError(LoginError):
    pass

class AccountInactive(LoginError):
    pass