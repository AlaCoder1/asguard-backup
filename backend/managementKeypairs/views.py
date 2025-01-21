from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from django.db.models.deletion import ProtectedError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from backend.managementKeypairs.key_pairs import create_private_key_in_system, create_public_key_in_system, delete_private_key_in_system, delete_public_key_in_system, import_public_key
from backend.managementKeypairs.list_key_pairs import get_list_all_private_key, get_list_all_public_key, get_one_private_key, get_one_public_key
from backend.managementKeypairs.models import PrivateKey, PublicKey
from backend.managementKeypairs.serializers import PrivateKeySerializer, PublicKeySerializer
from utils.errors_utils import CommandExecutionError


# Constants
CONSTANT_PRIVATE_KEY = _("Private Key")
CONSTANT_PUBLIC_KEY = _("Public Key")
CONSTANT_USED_ITEM = _("it's used in")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_DELETING_USED_ITEM = _("Unable to delete")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


##################################################
############# Private Key #############
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL PRIVATE KEYS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_private_key(request):
    """Getting all Private Keys from database"""
    if (request.method == 'GET'):
        list_private_key = get_list_all_private_key()
        return JsonResponse(list_private_key, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A PRIVATE KEY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_private_key(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        private_key = get_one_private_key(id)
        return JsonResponse(private_key, safe=False)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE A PRIVATE KEY",
    request_body=Schema(
        type=TYPE_OBJECT, required=['name', 'encryption_algorithm', 'key_size'],
        properties={'name': Schema(type=TYPE_STRING, example="private_key"),
                    'encryption_algorithm': Schema(type=TYPE_STRING, enum=['RSA'], description="Always is RSA"),
                    'key_size': Schema(type=TYPE_STRING, enum=['2048', '4096', '8192'])}))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_private_key(request):
    """Creating a new Private Key in system and adding it to the database"""
    try:
        # parse the incoming information
        data = request.data

        # Creating Private Key
        serializer_private_key = PrivateKeySerializer(data=data)
        if serializer_private_key.is_valid():
            # Install the private key in system
            create_private_key_in_system(data["name"], data["key_size"])
            
            # Add the server to the database
            serializer_private_key.save()
            return JsonResponse({"msg": f"""{data["name"]} {SUCCESS_MESSAGES_CREATING}"""}, status=201)
        
        return JsonResponse({"error": list(serializer_private_key.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_PRIVATE_KEY}"}, status=400)
    except ValueError as error:
        return JsonResponse({"error": error.__str__()}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A PRIVATE KEY",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_private_key(request, id):
    """Deleting a Private Key from system and then from database"""
    try:
        private_key = PrivateKey.objects.get(id=id)
        # delete from system
        delete_private_key_in_system(private_key.name)
        # delete from database
        private_key.delete()
        return JsonResponse({"msg": f"{private_key.name} {SUCCESS_MESSAGES_DELETING}"}, status=201)
    
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_PRIVATE_KEY}"}, status=400)
    except ProtectedError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_PRIVATE_KEY}, {CONSTANT_USED_ITEM} {CONSTANT_PUBLIC_KEY}"}, status=400)
    except PrivateKey.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_PRIVATE_KEY} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


##################################################
############# Public Key #############
##################################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL PUBLIC KEYS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_public_key(request):
    """Getting all Private Keys from database"""
    if (request.method == 'GET'):
        list_public_key = get_list_all_public_key()
        return JsonResponse(list_public_key, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A PUBLIC KEY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_public_key(request, id):
    """Getting a Certificates Authority by id from database"""
    if (request.method == 'GET'):
        public_key = get_one_public_key(id)
        return JsonResponse(public_key, safe=False)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE A PUBLIC KEY",
    request_body=Schema(
        type=TYPE_OBJECT, required=['name', 'method'], 
        properties={
            'name': Schema(type=TYPE_STRING, example="public_key"),
            'method': Schema(type=TYPE_OBJECT, required=['method_name'], properties={
                'method_name': Schema(type=TYPE_STRING, enum=['create', 'import']),
                'private_key': Schema(type=TYPE_INTEGER, example=1, description="ID of the selected private key"),
                'encryption_algorithm': Schema(type=TYPE_STRING, enum=['RSA'], description="Always is RSA"),
                'public_key_value': Schema(type=TYPE_STRING, example="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAi1fcisJwGXHZ4/A9VC85\nr6fY7eV4l52FxP6wQOxGrTpIU8GH+ud9hxd3xWt3xXgNpxcVys7jLJ4qc3iRjiUU\nt/cqI+kZmdHUkyLJqFk9vhs/oymYuESDn5XN7AM2dgPKkYsXIhMVQ0d35WCKwADX\neWgV9d9ziPxQNNHr8GyASiqiwYcsf2fHlxOSB+jX62JI8eqHESU+cJl55KpmSY+9\nkbLnc7JQDU/g+hhvvwqwxgyMPORnNkS9cyXMMogSDzYMBiS/vHyuq5XolYCJkqOk\nZznx2nLXJPTc6CcNSfXDSkEt7QX5l8wlDdUUA76q+OxBtBxn61sl48Ni85tfxImM\n9wIDAQAB\n-----END PUBLIC KEY-----", description="Value of the imported public key when using import method"),})}))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_public_key(request):
    """Creating a new Public Key in system and adding it to the database"""
    try:
        # parse the incoming information
        data = request.data

        public_key_data = {"name": data["name"]}

        if data["method"]["method_name"] == "create":
            private_key_id = data["method"].get('private_key', '')
            private_key = PrivateKey.objects.get(id=private_key_id)
            public_key_data["private_key"] = data["method"]["private_key"]
            public_key_data["encryption_algorithm"] = data["method"]["encryption_algorithm"]
            public_key_data["key_size"] = private_key.key_size
            # Creating Private Key
            serializer_public_key = PublicKeySerializer(data=public_key_data)
            if serializer_public_key.is_valid():
                # Install the public key in system
                create_public_key_in_system(private_key.name, data["name"])
                
                # Add the server to the database
                serializer_public_key.save()
                return JsonResponse({"msg":  f"""{data["name"]} {SUCCESS_MESSAGES_CREATING}"""}, status=201)
                
                
            return JsonResponse({"error": list(serializer_public_key.errors.values())[0][0]}, status=400)
            
        else: # Import method
            public_key_value = data["method"]["public_key_value"]
            public_key_data["encryption_algorithm"] = "RSA"
            serializer_public_key = PublicKeySerializer(data=public_key_data)
            if serializer_public_key.is_valid():
                public_key_length = import_public_key(data["name"], public_key_value)
                public_key_data["key_size"] = public_key_length
                serializer_public_key = PublicKeySerializer(data=public_key_data)
                if serializer_public_key.is_valid():
                    # Add the server to the database
                    serializer_public_key.save()
                    return JsonResponse({"msg":  f"""{data["name"]} {SUCCESS_MESSAGES_CREATING}"""}, status=201)
                                
            return JsonResponse({"error": list(serializer_public_key.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_PUBLIC_KEY}"}, status=400)
    except ValueError as error:
        return JsonResponse({"error": error.__str__()}, status=400)
    except PrivateKey.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_PRIVATE_KEY} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A PUBLIC KEY",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_public_key(request, id):
    """Deleting a Public Key from system and then from database"""
    try:
        public_key = PublicKey.objects.get(id=id)
        # delete from system
        delete_public_key_in_system(public_key.name)
        # delete from database
        public_key.delete()
        return JsonResponse({"msg": f"{public_key.name} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_PUBLIC_KEY}"}, status=400)
    except PublicKey.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_PUBLIC_KEY} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
