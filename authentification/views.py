from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import  AllowAny
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .serializers import *
import json
from django.http import JsonResponse
from .models import *
# Create your views here.

User = get_user_model()
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
                settings.USERNAME = username
                settings.PASSWORD = password
                userObject = User.objects.get(username=username)
                userDict = userObject.__dict__
                CurrentUser = {"username":userDict['username'],"email":userDict['email']}
                settings.CurrentUserId = userDict['id']
                return JsonResponse({'message': ' Success Authentification',"current user":CurrentUser}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'message': 'Invalid credentiels'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return JsonResponse({'message': 'Invalid username or password'})


@api_view(['GET'])
@permission_classes([AllowAny])
#@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def logout_view(request):
    return JsonResponse({"msg": 'User Logged out successfully'})

