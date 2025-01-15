from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from .models import Server, Type
from .serializers import ServerSerializerPost
import json
from backend.managementUsers.models import User
from django.core import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.hashers import check_password
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Constants
CONSTANT_USER = _('User')
CONSTANT_SERVER = _('Server')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_PASSWORD = _("Invalid password")

@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve all servers details.",
    responses={
        200: openapi.Response(
            description="Details of server connection retrieved successfully. "
                        "Each server connection includes the following attributes:\n"
                        "- **name_server**: The name of the server (e.g., 'MyServer').\n"
                        "- **hostname**: The hostname of the server (e.g., 'server.local').\n"
                        "- **transport**: The transport type used for communication (e.g., 'TCP').\n"
                        "- **protocol_version**: The protocol version of the server (e.g., 'IPv4').\n"
                        "- **scope**: The scope of the server (e.g., 'Global').\n"
                        "- **domaine_name**: The domain name of the server (e.g., 'example.com').\n"
                        "- **type**: The type of the server as referenced .",
        )
    }
      
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_servers(request):
    """
    This function retrieves a list of servers from the database.

    Parameters:
    request (HttpRequest): The incoming request object containing the HTTP method and any relevant data.

    Returns:
    JsonResponse: A JSON response containing the list of servers. If the request method is not 'GET', the response will contain an error message.
    """
    list_servers = []
    if (request.method == 'GET'):
        servers = Server.objects.all()
        server_dict = serializers.serialize("json", servers)
        res = json.loads(server_dict)
        for i in range(0, len(res)):
            res[i].pop('model')
            server_id = res[i]['pk']
            res[i].pop('pk')
            server_type = Type.objects.get(id=res[i]['fields']['type'])
            res[i]['fields']['id'] = server_id
            res[i]['fields']['type_name'] = server_type.type_name
            list_servers.append(res[i]['fields'])
        return JsonResponse(list_servers, safe=False)
    
@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve server by id details.",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of AD server to get info",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            description="Details of server connection retrieved successfully. "
                        "This server connection includes the following attributes:\n"
                        "- **name_server**: The name of the server (e.g., 'MyServer').\n"
                        "- **hostname**: The hostname of the server (e.g., 'server.local').\n"
                        "- **transport**: The transport type used for communication (e.g., 'TCP').\n"
                        "- **protocol_version**: The protocol version of the server (e.g., 'IPv4').\n"
                        "- **scope**: The scope of the server (e.g., 'Global').\n"
                        "- **domaine_name**: The domain name of the server (e.g., 'example.com').\n"
                        "- **type**: The type of the server as referenced .",
           
        ),
        
    }
)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_server(request, id):
    """
    This function retrieves a specific server from the database.

    Parameters:
    request (HttpRequest): The incoming request object containing the HTTP method and any relevant data.

    Returns:
    JsonResponse: A JSON response containing the list of servers. 
    If the request method is not 'GET', the response will contain an error message.
    """
    if (request.method == 'GET'):
        server = Server.objects.filter(id=id)
        server_dict = serializers.serialize("json", server)
        res = json.loads(server_dict)
        res[0].pop('model')
        server_id = res[0]['pk']
        res[0].pop('pk')
        server_type = Type.objects.get(id=res[0]['fields']['type'])
        res[0]['fields']['id'] = server_id
        res[0]['fields']['type_name'] = server_type.type_name
        server_json = res[0]['fields']
        # return a no content response.
        return JsonResponse(server_json)
@swagger_auto_schema(
        method='POST',
        operation_summary="API to create new server.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name_server": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The name of the server.",
                    example="ser1"
                ),
                "hostname": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The hostname of the server.",
                    example="hostname"
                ),
                "transport": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The transport type of the server.",
                    example="transport"
                ),
                "protocol_version": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The protocol version used.",
                    example=2
                ),
                "scope": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The scope of the server connection.",
                    example="scope"
                ),
                "domaine_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The domain name of the server.",
                    example="domaine_name"
                ),
                "type": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The type of connection.",
                    example=1
                ),
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The username for authentication.",
                    example="haninee"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The password for authentication.",
                    example="heni"
                ),
            },
            required=["name_server", "hostname", "transport", "protocol_version", "scope", "domaine_name", "type", "username", "password"],
        ),
        responses={
            201: f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_CREATING}",
            404:f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}",
            400: openapi.Response(
                description="Invalid input or missing required fields or password incorrect.",
                examples={
                    "application/json": {
                        "error": "Invalid input data."
                    },
                    
                }
            ),
        }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def create_server(request):
    """
    API to add a SERVER to the database.
    Parameters:
        request (HttpRequest): The incoming request object containing the POST data.
    Returns:
        JsonResponse: A JSON response containing a message indicating the success or failure of the operation.
    """
    if (request.method == 'POST'):
        
        # parse the incoming information
        data = request.data
        user_search = User.objects.filter(username=data["username"])
        if (len(user_search) != 0):
            user = User.objects.get(username=data["username"])
            server_dict = serializers.serialize("json", user_search)
            res = json.loads(server_dict)
            if check_password(data['password'], user.__dict__['password']):
                # instanciate with the serializer
                serializer_server = ServerSerializerPost(data=data)
                # check if the sent information is okay
                if (serializer_server.is_valid()):
                    # if okay, save it on the database
                    serializer_server.save()
                    # provide a Json Response with the data that was saved
                    return JsonResponse({"msg": f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_CREATING}"}, 
                                        status=201)
                # provide a Json Response with the necessary error information
                return JsonResponse(serializer_server.errors, status=400)
            return JsonResponse({"msg": ERROR_MESSAGES_INVALID_PASSWORD}, status=400)
        return JsonResponse({"msg": f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)

@swagger_auto_schema(
    method='DELETE',
     manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of server to delete",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={200:f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_DELETING}",
               404: f"{CONSTANT_SERVER} {ERROR_MESSAGES_INEXISTANT}"},
    operation_summary="API DELETE SERVER",
)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_server(request, id):
    """
    Deletes a server from the database based on the provided ID.

    Parameters:
    request (HttpRequest): The incoming request object containing the HTTP method and any relevant data.
    id (int): The ID of the server to be deleted.

    Returns:
    JsonResponse: A JSON response indicating the success or failure of the operation.
    If the server with the given ID exists, it is deleted from the database and a success message is returned.
    If the server with the given ID does not exist, a not found message is returned.
    """
    if (request.method == 'DELETE'):
        if Server.objects.filter(id=id).exists():
            server = Server.objects.get(id=id)
            server.delete()
            return JsonResponse({"msg": f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_DELETING}"},status=200)
        else:
            return JsonResponse({"msg": f"{CONSTANT_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)

@swagger_auto_schema(
        method='PUT',
        operation_summary="API to update server.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of server to update",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name_server": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The name of the server.",
                    example="ser1"
                ),
                "hostname": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The hostname of the server.",
                    example="hostname"
                ),
                "transport": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The transport type of the server.",
                    example="transport"
                ),
                "protocol_version": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The protocol version used.",
                    example=2
                ),
                "scope": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The scope of the server connection.",
                    example="scope"
                ),
                "domaine_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The domain name of the server.",
                    example="domaine_name"
                ),
                "type": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The type of connection.",
                    example=1
                ),
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The username for authentication.",
                    example="haninee"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The password for authentication.",
                    example="heni"
                ),
            },
            required=["name_server", "hostname", "transport", "protocol_version", "scope", "domaine_name", "type", "username", "password"],
        ),
        responses={
            200: f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_UPDATING}",
            404:f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}",
            400: f"{ERROR_MESSAGES_INVALID_PASSWORD}"
        }
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def modify_server(request, id):
    """
    API to update SERVER in the system and database.
    Parameters:
        request (HttpRequest): An instance of HttpRequest containing the incoming request data.
        id (int): The ID of the SERVER to be updated.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.
    """
    if (request.method == 'PUT'):
        server_by_id = Server.objects.filter(id=id)
        server_dict = serializers.serialize("json", server_by_id)
        res = json.loads(server_dict)
        res[0].pop('model')
        server_id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = server_id
        server_json = res[0]['fields']
        data = request.data
        server_object = Server.objects.get(id=server_id)
        server = server_object.__dict__
        type = Type.objects.get(id=data['type'])
        user_search = User.objects.filter(username=data["username"])
        if (len(user_search) != 0):
            user = User.objects.get(username=data["username"])
            server_dict = serializers.serialize("json", user_search)
            res = json.loads(server_dict)
            if check_password(data['password'], user.__dict__['password']):
                server_object.name_server = data['name_server']
                server_object.hostname = data['hostname']
                server_object.transport = data['transport']
                server_object.protocol_version = data['protocol_version']
                server_object.scope = data['scope']
                server_object.domaine_name = data['domaine_name']
                server_object.type = type
                server_object.save()
                return JsonResponse({"msg": f"{CONSTANT_SERVER} {SUCCESS_MESSAGES_UPDATING}"},status=200)
            return JsonResponse({"msg": ERROR_MESSAGES_INVALID_PASSWORD}, status=400)
        return JsonResponse({"msg": f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
