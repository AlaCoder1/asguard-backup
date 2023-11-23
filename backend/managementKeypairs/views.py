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
from backend.managementKeypairs.key_pairs import create_private_key, create_public_key, delete_private_key_in_system, delete_public_key_in_system, import_public_key
from backend.managementKeypairs.list_key_pairs import get_all_private_key, get_all_public_key, get_private_key, get_public_key
from backend.managementKeypairs.models import PrivateKey, PublicKey
from backend.managementKeypairs.serializers import PrivateKeySerializer, PublicKeySerializer

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
                                                             'encryption_algorithm': openapi.Schema(type=openapi.TYPE_STRING, enum=['RSA'], 
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


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE A PUBLIC KEY",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['name', 'method'],
                                                 properties={'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'method': openapi.Schema(type=openapi.TYPE_OBJECT, required=['method_name'],
                                                                                      properties={'method_name': openapi.Schema(type=openapi.TYPE_STRING, enum=['create', 'import']),
                                                                                                  'private_key': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the selected private key"),
                                                                                                  'encryption_algorithm': openapi.Schema(type=openapi.TYPE_STRING, enum=['RSA'], description="Always is RSA"),
                                                                                                  'public_key_value': openapi.Schema(type=openapi.TYPE_STRING, description="Value of the imported public key"),
                                                                                                  })
                                                                                                  }
                                                                                                  ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createPublicKey(request):
    """Creating a new Public Key in system and adding it to the database"""
    if request.method == 'POST':
        try:
            # parse the incoming information
            data = request.data

            name = data.get('name', '')
            method = data.get('method', '')
            public_key_data = {"name": name}

            if method.get('method_name', '') == "create":
                private_key_id = method.get('private_key', '')
                private_key = PrivateKey.objects.get(id=private_key_id)
                encryption_algorithm = data.get('encryption_algorithm', '')
                public_key_data["private_key"] = private_key_id
                public_key_data["encryption_algorithm"] = encryption_algorithm
                public_key_data["key_size"] = private_key.key_size
                # Creating Private Key
                serializer_public_key = PublicKeySerializer(data=public_key_data)
                if serializer_public_key.is_valid():
                    # Install the public key in system
                    create_public_key(private_key.name, name)
                    public_key_data["public_key_path"] = f'/etc/ipsec.d/certs/{name}.key'
                    # public_key_data["finger_print"] = finger_print
                    serializer_public_key = PublicKeySerializer(data=public_key_data)
                    if serializer_public_key.is_valid():
                        # Add the server to the database
                        serializer_public_key.save()
                        return JsonResponse({"msg": f"Public Key {name} is created"}, status=201)
                    
                    else:
                        return JsonResponse({"error": list(serializer_public_key.errors.values())[0][0]}, status=400)
                    
                else:
                    return JsonResponse({"error": list(serializer_public_key.errors.values())[0][0]}, status=400)
                
            else: # Import method
                public_key_value = method.get('public_key_value', '')
                public_key_data["encryption_algorithm"] = "RSA"
                serializer_public_key = PublicKeySerializer(data=public_key_data)
                if serializer_public_key.is_valid():
                    public_key_length = import_public_key(name, public_key_value)
                    print("public_key_length: ", public_key_length)
                    public_key_data["public_key_path"] = f'/etc/ipsec.d/certs/{name}.key'
                    # public_key_data["finger_print"] = finger_print
                    public_key_data["key_size"] = public_key_length
                    serializer_public_key = PublicKeySerializer(data=public_key_data)
                    if serializer_public_key.is_valid():
                        # Add the server to the database
                        serializer_public_key.save()
                        return JsonResponse({"msg": f"Public Key {name} is created"}, status=201)
                    
                    else:
                        return JsonResponse({"error": list(serializer_public_key.errors.values())[0][0]}, status=400)
                    
                else:
                    return JsonResponse({"error": list(serializer_public_key.errors.values())[0][0]}, status=400)

        except CommandExecutionError:
            return JsonResponse({"error": "Error in creating Public Key"}, status=400)
        except ValueError as error:
            return JsonResponse({"error": error.__str__()}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A PUBLIC KEY",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deletePublicKey(request, id):
    """Deleting a Public Key from system and then from database"""
    try:
        if (request.method == 'DELETE'):
            public_key = PublicKey.objects.get(id=id)
            # delete from system
            delete_public_key_in_system(public_key.name)
            # delete from database
            public_key.delete()
            return JsonResponse({"msg": f"delete public key {public_key.name} succesfully"})
        
    except PublicKey.DoesNotExist:
        return JsonResponse({"error": "This Public Key does not exist"}, status=400)
