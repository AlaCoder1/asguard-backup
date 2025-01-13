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

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF SERVERS",
                     operation_description="API TO GET LIST OF SERVERS",)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getALLServers(request):
    """Getting list of servers from database"""
    if (request.method == 'GET'):
        list_servers = get_list_ad_servers()
        return JsonResponse(list_servers, safe=False)

################################### API GET LDAP SERVER BY ID ############################################




@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF SERVERS",
                     operation_description="API TO GET LIST OF SERVERS",)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getServerById(request, id):
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
    request_body=ADServerSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API Connect to Remote server ",
    operation_description="API Connect to Remote server",
)  
# Create new Connection to Active Directory Server  
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def connect_to_ad(request):
    """Connect to Remote LDAP Server"""
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
    request_body=ADServerSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE directory Server",
    operation_description="This API help us to update parametres in directory server added ",
)
@api_view(['PUT'])
@permission_classes([])
def updateLdapServer(request,id):
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
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API DELETE Ldap Server",
    operation_description="This API delete directory server ",
)
@api_view(['DELETE'])
@permission_classes([])
def deleteldap_server(request,id):
    
    if (request.method == 'DELETE'):
        if (ADServer.objects.filter(id=id).exists()):
            ldap_servers = ADServer.objects.get(id=id)
            ldap_servers.delete()
            msg=f"{CONSTANT_LDAP_SERVER} {SUCCESS_MESSAGES_DELETING}"
    return JsonResponse({"msg": msg}, status=200)