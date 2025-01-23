from django.shortcuts import render
import json
from rest_framework.parsers import JSONParser
from django.utils.translation import gettext_lazy as _
from django.core import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from backend.LdapServer.serializers import ADServerSerializer
from backend.LdapServer.models import ADServer
import ldap
from rest_framework.response import Response
from .list_Remote_servers import get_list_ad_servers,update_Ldapserver_DB
from drf_yasg.utils import swagger_auto_schema
from . import views
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Constants
CONSTANT_LDAP_SERVER = _('Directory Server')
CONSTANT_LDAP_UNREACHABLE= _('Directory Server unreachable, verify IP address or port')
CONSTANT_LDAP_AUTH = _("Authentication failed")
CONSTANT_LDAP_SEARCH_BASE = _("Please provide a valid Search Base")
CONSTANT_INVALID_REQUEST = _("Invalid request method")
CONSTANT_LDAP_UNVALID_CREDENTIENLS= _('Invalid Server Credentials')

# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")

# Error messages
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


################################### API GET ALL LDAP SERVERS ##################################################


@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve all servers connections details.",
    responses={
        200: openapi.Response(
            description=(
                "Details of server connections retrieved successfully. "
                "Each server connection includes the following attributes:\n"
                "- **server_name**: The name of the server (e.g., 'hhhh').\n"
                "- **server_url**: The server's URL or IP address (e.g., '54.38.218.21').\n"
                "- **port**: The port number used for the connection (e.g., 389).\n"
                "- **search_base**: The base DN for directory searches (e.g., 'dc=testing,dc=ad').\n"
                "- **bind_user_dn**: The distinguished name of the user for binding (e.g., 'hela.touzi@testing.ad').\n"
                "- **bind_user_password**: The hashed password of the bind user (e.g., 'pbkdf2_sha256$870000...').\n"
                "- **ssl_tls_activation**: Boolean indicating if SSL/TLS is activated (e.g., `false`).\n"
                "- **server_type**: The type of server (e.g., 'ad').\n"
                "- **id**: The unique identifier of the server entry."
            ),
        )
    }
      
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getALLServers(request):
    """
    This function retrieves a list of servers from the database.

    Parameters:
    request (HttpRequest): The incoming request object containing the HTTP method and any relevant data.

    Returns:
    JsonResponse: A JSON response containing the list of servers. If the request method is not 'GET', the response will contain an error message.
    """
    if (request.method == 'GET'):
        list_servers = get_list_ad_servers()
        return JsonResponse(list_servers, safe=False,status=200)

################################### API GET LDAP SERVER BY ID ############################################


@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve server connection by id details.",
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
            description=(
                "Details of server connection retrieved successfully. "
                "This server connection includes the following attributes:\n"
                "- **server_name**: The name of the server (e.g., 'hhhh').\n"
                "- **server_url**: The server's URL or IP address (e.g., '54.38.218.21').\n"
                "- **port**: The port number used for the connection (e.g., 389).\n"
                "- **search_base**: The base DN for directory searches (e.g., 'dc=testing,dc=ad').\n"
                "- **bind_user_dn**: The distinguished name of the user for binding (e.g., 'hela.touzi@testing.ad').\n"
                "- **bind_user_password**: The hashed password of the bind user (e.g., 'pbkdf2_sha256$870000...').\n"
                "- **ssl_tls_activation**: Boolean indicating if SSL/TLS is activated (e.g., `false`).\n"
                "- **server_type**: The type of server (e.g., 'ad').\n"
                "- **id**: The unique identifier of the server entry."
            ),
           
        ),
        404: openapi.Response(description=f"{CONSTANT_LDAP_SERVER}{ERROR_MESSAGES_INEXISTANT}"),
    }
)



@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getServerById(request, id):
    """
    This function retrieves a specific server from the database.

    Parameters:
    request (HttpRequest): The incoming request object containing the HTTP method and any relevant data.

    Returns:
    JsonResponse: A JSON response containing the list of servers. 
    If the request method is not 'GET', the response will contain an error message.
    """
    if request.method == 'GET':
        try:
            ldap_server = ADServer.objects.get(id=id)
            ldap_server_data = serializers.serialize("json", [ldap_server])
            res = json.loads(ldap_server_data)
            list_servers=[]
            for i in range(0, len(res)):
                res[i].pop('model')
                id = res[i]['pk']
                res[i].pop('pk')
                res[i]['fields']['id'] = id
                list_servers.append(res[i]['fields'])
            return JsonResponse({ f"{CONSTANT_LDAP_SERVER}": list_servers})
        except ADServer.DoesNotExist:
            return JsonResponse({"error":f"{CONSTANT_LDAP_SERVER}{ERROR_MESSAGES_INEXISTANT}"}, status=404)     




############################################# API CREATE AND CONNECT TO LDAP SERVER ############################################
@swagger_auto_schema(
    method='POST',
    operation_summary="API to establish server connection.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "server_type": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The type of the server.",
                enum=["openldap", "ad"],
                default="openldap"
            ),
            "server_name": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The name of the server.",
                example="ADServer"
            ),
            "server_url": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The URL or IP address of the server.",
                example="10.1.12.54"
            ),
            "port": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="The port used for server connection.",
                example=389
            ),
            "search_base": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The base DN for directory searches.",
                example="dc=testing,dc=local"
            ),
            "bind_user_dn": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The distinguished name of the user for binding.",
                example="administrator@testing.local"
            ),
            "bind_user_password": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The password of the bind user.",
                example="root123e.g"
            ),
            "ssl_tls_activation": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Indicates if SSL/TLS is activated.",
                example=False
            ),
        },
        required=["server_type", "server_name", "server_url", "port", "search_base", "bind_user_dn", "bind_user_password"],
    ),
    responses={
        200: openapi.Response(
            description=f"{CONSTANT_LDAP_SERVER} {SUCCESS_MESSAGES_CREATING}"
        ),
        400: openapi.Response(
            description="Invalid input or missing required fields.",
            examples={
                "application/json": {
                    "error": "Invalid input data."
                }
            }
        ),
    }
)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def connect_to_ad(request):
    """
    Establishes a connection to a remote LDAP/Active Directory server and saves the server details.

    This function attempts to connect to the specified LDAP server using the provided credentials,
    performs a test search, and if successful, saves the server details to the database.

    Parameters:
    request (HttpRequest): The HTTP request object .

    Returns:
    JsonResponse: A JSON response with a status code and a message.
        - If successful: {'msg': 'Directory Server is created'}, status 200
        - If failed: {'msg': <error_message>}, status 400

    Raises:
    JsonResponse: With appropriate error messages for various failure scenarios.
    """
    if request.method == 'POST':
        try:
            # Get data from the request
            data = request.data
            server_name = data['server_name'],
            server_url = data['server_url']
            port = data['port']
            bind_user_dn = data['bind_user_dn']
            search_base = data['search_base']
            password_ldap=data['bind_user_password']
            bind_user_password = make_password(data['bind_user_password'])
            ssl_tls_activation = data['ssl_tls_activation']
            server_type = data['server_type']

            # Connect to AD server
            ldap_uri = f"{'ldaps' if ssl_tls_activation else 'ldap'}://{server_url}:{port}"
            ldap_conn = ldap.initialize(ldap_uri)
            ldap_conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 5)
            if ssl_tls_activation:
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)  # Enforce certificate verification
                ldap.set_option(ldap.OPT_X_TLS_CACERTDIR, '/etc/ssl/certs/')  # Path to trusted CA certificates directory
            try:
                ldap_conn.simple_bind_s(bind_user_dn,password_ldap)

                result = ldap_conn.search_s(search_base, ldap.SCOPE_SUBTREE, "(objectClass=user)", ['userPrincipalName'])
                user_principal_names = [
                    entry[1].get('userPrincipalName', [])[0].decode('utf-8')
                    for entry in result
                    if 'userPrincipalName' in entry[1]
                ]

                # Save updated server details in the database
                data['bind_user_password']=bind_user_password
                serializer = ADServerSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    error_message = next(iter(serializer.errors.values()))[0]
                    return JsonResponse({'msg': error_message},status=400)    

                # Close LDAP connection
                ldap_conn.unbind()

                return JsonResponse({ 'msg':f"{CONSTANT_LDAP_SERVER} {SUCCESS_MESSAGES_CREATING}"},status=200)
            
            except ldap.INVALID_CREDENTIALS:
                return JsonResponse({'msg': f"{CONSTANT_LDAP_UNVALID_CREDENTIENLS}"},status=400)
            
            except ldap.SERVER_DOWN:
                # LDAP authentication failed
                return JsonResponse({'msg': f"{CONSTANT_LDAP_UNREACHABLE}"},status=400)
            except ldap.LDAPError as e:
                # LDAP authentication failed
                return JsonResponse({'msg': f"{CONSTANT_LDAP_SEARCH_BASE}"},status=400)

        
        except Exception as e:
            return JsonResponse({ 'msg': str(e)},status=400)

    return JsonResponse({'msg': f"{CONSTANT_INVALID_REQUEST}"},status=400)



################################################ API TO UPDATE THE PARAMERTERS OF Ldap server #####################


@swagger_auto_schema(
    method='PUT',
    operation_summary="API to update server connection.",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of AD server to update",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "server_type": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The type of the server.",
                enum=["openldap", "ad"],
                default="openldap"
            ),
            "server_name": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The name of the server.",
                example="ADServer"
            ),
            "server_url": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The URL or IP address of the server.",
                example="10.1.12.54"
            ),
            "port": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="The port used for server connection.",
                example=389
            ),
            "search_base": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The base DN for directory searches.",
                example="dc=testing,dc=local"
            ),
            "bind_user_dn": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The distinguished name of the user for binding.",
                example="administrator@testing.local"
            ),
            "bind_user_password": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The password of the bind user.",
                example="root123e.g"
            ),
            "ssl_tls_activation": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Indicates if SSL/TLS is activated.",
                example=False
            ),
        },
        required=["server_type", "server_name", "server_url", "port", "search_base", "bind_user_dn", "bind_user_password"],
    ),
    responses={
        201: openapi.Response(
            description=f"{CONSTANT_LDAP_SERVER} {SUCCESS_MESSAGES_UPDATING}"
        ),
        400: openapi.Response(
            description="Invalid input or missing required fields.",
            examples={
                "application/json": {
                    "error": "Invalid input data."
                }
            }
        ),
    }
)
@api_view(['PUT'])
@permission_classes([])
def updateLdapServer(request, id):
    """
    Update the parameters of an existing LDAP server.

    This function handles the PUT request to update the details of a specific LDAP server
    identified by its ID. It checks if the server exists, parses the request data,
    and attempts to update the server's information in the database.

    Parameters:
    request (HttpRequest): The HTTP request object containing the updated server data.
    id (int): The ID of the LDAP server to be updated.

    Returns:
    JsonResponse: A JSON response containing a message indicating the result of the update operation.
                  If successful, returns a success message with a 200 status code.
                  If unsuccessful, returns an error message with a 400 status code.
    """
    if (request.method == 'PUT'):
        msg=f"{ERROR_MESSAGES_UPDATING}"
        if (ADServer.objects.filter(id=id).exists()):
            data = JSONParser().parse(request)
            result = update_Ldapserver_DB(data, id)
            if result is True:
                msg = f"{CONSTANT_LDAP_SERVER} {SUCCESS_MESSAGES_UPDATING}"
                status_code= 200
            elif 'msg' in result:
                msg = result['msg'] 
                status_code= 400
    return JsonResponse({"msg":msg},status=status_code)




@swagger_auto_schema(
    method='DELETE',
     manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of AD server to delete",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={200:f"{CONSTANT_LDAP_SERVER} {SUCCESS_MESSAGES_DELETING}",
               404: f"{CONSTANT_LDAP_SERVER} {ERROR_MESSAGES_INEXISTANT}"},
    operation_summary="API DELETE ldap server",
)
@api_view(['DELETE'])
@permission_classes([])
def deleteldap_server(request,id):
    """
    Delete LDAP server from the database.
    This function removes LDAP server configuration from both the system and the database.
    Parameters:
        request (HttpRequest): The incoming request object containing the DELETE data.#+
        id (int): The ID of the LDAP server to be deleted.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        The response includes a message and a status code. The status can be "success" or "error".
        If the LDAP server is found and deleted, the response message will indicate successful deletion.
        If the LDAP server is not found, the response will indicate an error.
    """
    if (request.method == 'DELETE'):
        if (ADServer.objects.filter(id=id).exists()):
            ldap_servers = ADServer.objects.get(id=id)
            ldap_servers.delete()
            msg=f"{CONSTANT_LDAP_SERVER} {SUCCESS_MESSAGES_DELETING}"
            status=200
        else:
            msg=f"{CONSTANT_LDAP_SERVER} {ERROR_MESSAGES_INEXISTANT}"
            status=404
    return JsonResponse({"msg": msg}, status=status)