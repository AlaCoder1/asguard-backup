from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.deletion import ProtectedError
import json
from rest_framework.authentication import SessionAuthentication
from django.core import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from backend.managementKeypairs.models import PrivateKey

from backend.openvpn.manage_errors import CommandExecutionError

# Create your views here.

##################################################
############# Private Key #############
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL PRIVATE KEYS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllPrivateKey(request):
    """Getting all Private Keys from database"""
    list_private_key = []
    if (request.method == 'GET'):
        private_key = PrivateKey.objects.all()
        caDict = serializers.serialize("json", private_key)
        res = json.loads(caDict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_private_key.append(res[i]['fields'])
        return JsonResponse(list_private_key, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A PRIVATE KEY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getPrivateKey(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        private_key = PrivateKey.objects.filter(pk=id)
        private_keyDict = serializers.serialize("json", private_key)
        res = json.loads(private_keyDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        return JsonResponse(res[0]['fields'], safe=False)
