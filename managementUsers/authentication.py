# managementUsers/authentication.py

from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError
import pytz


User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
   
    def authenticate( self,request):
        # Extract the JWT from the Authorization header
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if jwt_token is None:
            return None

        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)  # clean the token
        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise ParseError()
           
        # Get the user from the database
        id = payload.get('user_identifier')
        if id is None:
            raise AuthenticationFailed('User identifier not found in JWT')
            # return None
        user = User.objects.filter(id=id).first()
        if user is None:
            raise AuthenticationFailed('User not found')
           
        # Return the user and token payload
        
        return user, payload
        

    def authenticate_header(self, request):
        return 'Bearer'

    @classmethod
    def create_jwt(cls, user):
        # Create the JWT payload
        timezone=pytz.timezone("Africa/Tunis")
        # print("timmmmme",str((datetime.now(timezone) + timedelta(hours=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']))).split(".")[0])
        
        payload = {
            'user_identifier': user.id,
            'exp': int((datetime.now(timezone) + timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])).timestamp()),
            # set the expiration time for 5 hour from now
            'iat': datetime.now().timestamp(),
            'username': user.username,
            
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        print(payload['exp'])
        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')  # clean the token
        return token
