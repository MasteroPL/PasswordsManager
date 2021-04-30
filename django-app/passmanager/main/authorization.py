from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def user_login(request, username:str, password:str):
    '''
    Logs user in if credentials are valid and account configuration are valid for login

    :throws AccountInactive: thrown if account is inactive
    :throws InvalidCredentialsError: thrown the credentials provided were invalid
    '''
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)

        else:
            raise AccountInactive()
    
    raise InvalidCredentialsError()


def user_logout(user:User):
    logout(user)



class LoginError(Exception):
    pass

class InvalidCredentialsError(LoginError):
    pass

class AccountInactive(LoginError):
    pass