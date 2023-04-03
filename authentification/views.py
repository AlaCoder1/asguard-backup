from django.contrib.auth import get_user_model
from rest_framework import  status
from .authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
from django.conf import settings
from .serializers import *
import json
from django.http import JsonResponse
import paramiko
# Create your views here.


User=get_user_model()
ssh = paramiko.SSHClient()
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def authentification_JWT(request):
    if (request.method=="POST"):
        User = get_user_model()
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        serializer = ObtainTokenSerializer(data=data)
        if (serializer.is_valid()):
            # username = serializer.validated_data.get('username')
            # password = (serializer.validated_data.get('password'))
            user=authenticate(request, username=username, password=password)
            if (user is not None):
                login(request,user)
                # automatically add host key when connecting to a new host
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # connect to SSH server
                ssh.connect(settings.SSH_HOST, username=username, password=password,port=settings.SSH_PORT)
                # Run the whoami command and capture its output
                command = "whoami"
                # Execute the command on the remote machine
                stdin, stdout, stderr = ssh.exec_command((command))
                # Split the output into lines and extract the last line
                lines = stdout.read().decode('utf-8').split("\n")
                last_line = lines[-2] if lines[-1] == "" else lines[-1]
                print({"who i am":last_line})
                # jwt_token=str(JWTAuthentication.create_jwt(user).decode())
                jwt_token=str(JWTAuthentication.create_jwt(user))
                userObject = User.objects.get(username=username)
                userObject.token_last_expired=datetime.now()+timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])
                userObject.save()
                return JsonResponse({'token': jwt_token})
            else:
                return JsonResponse({'message': 'Invalid credentiels'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'message': 'Invalid username or password'})
            
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def logout_view(request):
    username=request.user.username
    print({"logout":logout(request)})
    if logout(request) is None:
        # close the SSH connection
        ssh.close()
    userObject = User.objects.get(username=username)
    userObject.token_last_expired=datetime.now()+timedelta(hours=0)
    userObject.save()
    return JsonResponse({"msg":'User Logged out successfully'})