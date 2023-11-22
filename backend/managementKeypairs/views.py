from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication
from django.core import serializers
from django.db.models.deletion import ProtectedError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from backend.managementKeypairs.key_pairs import create_private_key, delete_private_key_in_system
from backend.managementKeypairs.list_key_pairs import get_all_private_key, get_all_public_key, get_private_key, get_public_key
from backend.managementKeypairs.models import PrivateKey, PublicKey
from backend.managementKeypairs.serializers import PrivateKeySerializer

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
    if (request.method == 'GET'):
        list_private_key = get_all_private_key()
        return JsonResponse(list_private_key, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A PRIVATE KEY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getPrivateKey(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        private_key = get_private_key(id)
        return JsonResponse(private_key, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE A PRIVATE KEY",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['name', 'encryption_algorithm', 'key_size'],
                                                 properties={'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'encryption_algorithm': openapi.Schema(type=openapi.TYPE_STRING, enum='RSA', 
                                                                                                    description="Always is RSA"),
                                                             'key_size': openapi.Schema(type=openapi.TYPE_STRING, enum=['2048', '4096', '8192'])
                                                             }
                                                             ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createPrivateKey(request):
    """Creating a new Private Key in system and adding it to the database"""
    if request.method == 'POST':
        try:
            data = request.data

            # parse the incoming information
            data = request.data

            name = data.get('name', '')
            encryption_algorithm = data.get('encryption_algorithm', '')
            key_size = data.get('key_size', '')
            private_key_data = {"name": name,
                                "encryption_algorithm": encryption_algorithm,
                                "key_size": key_size,
                                }
            # Creating Private Key
            serializer_private_key = PrivateKeySerializer(data=private_key_data)
            if serializer_private_key.is_valid():
                # Install the private key in system
                create_private_key(name, key_size)
                
                private_key_data["private_key_path"] = f'/etc/ipsec.d/private/{name}.key'
                serializer_private_key = PrivateKeySerializer(data=private_key_data)
                if serializer_private_key.is_valid():
                    # Add the server to the database
                    serializer_private_key.save()
                    return JsonResponse({"msg": f"Private key {name} is created"}, status=201)
                
                else:
                    return JsonResponse({"error": list(serializer_private_key.errors.values())[0][0]}, status=400)
                
            else:
                return JsonResponse({"error": list(serializer_private_key.errors.values())[0][0]}, status=400)

        except CommandExecutionError:
            return JsonResponse({"error": "Error in creating Private Key"}, status=400)
        except ValueError as error:
            return JsonResponse({"error": error.__str__()}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A PRIVATE KEY",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deletePrivateKey(request, id):
    """Deleting a Private Key from system and then from database"""
    try:
        if (request.method == 'DELETE'):
            private_key = PrivateKey.objects.get(id=id)
            # delete from system
            delete_private_key_in_system(private_key.name)
            # delete from database
            private_key.delete()
            return JsonResponse({"msg": f"delete private key {private_key.name} succesfully"})
    except ProtectedError:
        return JsonResponse({"error": "You have to delete Public Key created by this Private Key"}, status=400)
    except PrivateKey.DoesNotExist:
        return JsonResponse({"error": "This Private Key does not exist"}, status=400)


##################################################
############# Public Key #############
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL PUBLIC KEYS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllPublicKey(request):
    """Getting all Private Keys from database"""
    if (request.method == 'GET'):
        list_public_key = get_all_public_key()
        return JsonResponse(list_public_key, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A PUBLIC KEY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getPublicKey(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        public_key = get_public_key(id)
        return JsonResponse(public_key, safe=False)
