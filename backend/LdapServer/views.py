from django.shortcuts import render
import json
from rest_framework.parsers import JSONParser
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
from backend.LdapServer.config_ldaps import update_ldap_conf
from rest_framework.response import Response




# Create new Connection to Active Directory Server  

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def connect_to_ad(request):
    if request.method == 'POST':
        try:
            # Get data from the request
            data = request.data
            serializer = ADServerSerializer(data=data)
            if serializer.is_valid():
                # Check if the server name already exists in the database
                server_name = serializer.validated_data['server_name']
                try:
                    ad_server = ADServer.objects.get(server_name=server_name)
                except ADServer.DoesNotExist:
                    # Create a new server if it doesn't exist
                    ad_server = serializer.save()

                # Update existing server details
                ad_server.server_url = serializer.validated_data['server_url']
                ad_server.port = serializer.validated_data['port']
                ad_server.bind_user_dn = serializer.validated_data['bind_user_dn']
                ad_server.search_base = serializer.validated_data['search_base']
                ad_server.bind_user_password = serializer.validated_data['bind_user_password']
                ad_server.ssl_tls_activation = serializer.validated_data['ssl_tls_activation']
                ad_server.save()

                # Connect to AD server
                ldap_uri = f"{'ldaps' if ad_server.ssl_tls_activation else 'ldap'}://{ad_server.server_url}:{ad_server.port}"
                #ldap_uri = f"ldap://{ad_server.server_url}:{ad_server.port}"
                ldap_conn = ldap.initialize(ldap_uri)
                ldap_conn.simple_bind_s(ad_server.bind_user_dn, ad_server.bind_user_password)

                # Update ldap.conf based on SSL/TLS activation
                ldap_conf_path = '/etc/openldap/ldap.conf'
                update_ldap_conf(ldap_conf_path, ad_server.ssl_tls_activation)

                # Retrieve user details from AD (you can modify this part based on your needs)
                result = ldap_conn.search_s(ad_server.search_base, ldap.SCOPE_SUBTREE, "(objectClass=user)")
                print(result)
                users = [
                    entry[1].get('sAMAccountName', [])[0].decode('utf-8') 
                    for entry in result 
                    if 'sAMAccountName' in entry[1]
                ]

                # Close LDAP connection
                ldap_conn.unbind()

                return Response({'success': True, 'users': users})
            else:
                return Response({'success': False, 'error': serializer.errors})
        except Exception as e:
            return Response({'success': False, 'error': str(e)})

    return Response({'success': False, 'error': 'Invalid request method'})