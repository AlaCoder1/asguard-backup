from django.contrib.auth import get_user_model
from rest_framework import status
from .authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
from django.conf import settings
from .serializers import *
import json
from django.http import JsonResponse
import paramiko
from .models import *
# Create your views here.


User = get_user_model()
ssh = paramiko.SSHClient()
from django.shortcuts import redirect
from django.conf import settings
@api_view(['POST'])
@permission_classes([AllowAny])
def authentification(request):
    if (request.method == "POST"):
        User = get_user_model()
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        serializer = ObtainTokenSerializer(data=data)
        if (serializer.is_valid()):
            user = authenticate(request, username=username, password=password)
            if (user is not None):
                login(request, user)
                # automatically add host key when connecting to a new host
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # connect to SSH server
                ssh.connect(settings.SSH_HOST, username=username,
                            password=password, port=settings.SSH_PORT)
                # def getUserCredentials():
                #     settings.USERNAME = username
                #     settings.PASSWORD = username
                #     return username,password
                # getUserCredentials()
                settings.USERNAME = username
                settings.PASSWORD = password
                ## add this code so that logout work with jwt and timeleft
                
                # jwt_token = str(JWTAuthentication.create_jwt(user))
                # userObject = User.objects.get(username=username)
                # userObject.token_last_expired = datetime.now(
                # )+timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])
                # userObject.save()
                
                ## end code
                # userDict = userObject.__dict__
                # del userDict['_state']
                # del userDict['password']
                # del userDict['last_login']
                # del userDict['token_last_expired']
                userObject = User.objects.get(username=username)
                userDict = userObject.__dict__
                settings.CurrentUserId = userDict['id']
                # def getCurrentUserId():
                #     userObject = User.objects.get(username=username)
                #     userDict = userObject.__dict__
                #     settings.CurrentUserId = userDict['id']
                #     return userDict['id']
                # getCurrentUserId()
                ## add this code so that logout work with jwt and timeleft
                
                # return JsonResponse({'message': ' Success Authentification','jwt':jwt_token}, status=status.HTTP_200_OK)
                ## end code
                return JsonResponse({'message': ' Success Authentification'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'message': 'Invalid credentiels'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return JsonResponse({'message': 'Invalid username or password'})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def logout_view(request):
    logout()
    if logout(request) is None:
        # close the SSH connection
        ssh.close()
  
    return JsonResponse({"msg": 'User Logged out successfully'})
