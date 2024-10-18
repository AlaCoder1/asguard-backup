from .models import ADServer
import json
from django.utils.translation import gettext_lazy as _
from backend.authentification.views import ldap
from .serializers import ADServerSerializer
from django.core import serializers
from django.contrib.auth.hashers import make_password
 
# Constants
CONSTANT_LDAP_SERVER = _('Directory Server')
CONSTANT_LDAP_UNREACHABLE= _('Directory Server unreachable , Please Verify your ip address or port')
CONSTANT_LDAP_UNVALID_CREDENTIENLS= _('Invalid Credentials')
CONSTANT_LDAP_SEARCH_BASE = _("Provide correct Search Base")
 
 
################### Function to display list of Servers ###################
def get_list_ad_servers():
        """list of Remote servers"""
 
        servers_list = []
        # Get all Remote servers from database
        list_servers = ADServer.objects.all()
        servers = serializers.serialize("json", list_servers)
        res = json.loads(servers)
        print(res)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            servers_list.append(res[i]['fields'])
 
        # Return the list in json form
        return json.dumps(servers_list)
 

################### Function to update the ldap server credentiels ###################
def update_Ldapserver_DB(data, id):
    server = ADServer.objects.get(id=id)
    server_serializers = ADServerSerializer(server, data=data)
 
    ldap_uri = f"{'ldaps' if data['ssl_tls_activation'] else 'ldap'}://{data['server_url']}:{data['port']}"
    ldap_conn = ldap.initialize(ldap_uri)
    ldap_conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 5)
    try:
        ldap_conn.simple_bind_s(data['bind_user_dn'], data['bind_user_password'])
 
        # Check LDAP search result more explicitly
        result = ldap_conn.search_s(data['search_base'], ldap.SCOPE_SUBTREE, "(objectClass=user)", ['userPrincipalName'])
       
        if result !=-1:
            if server_serializers.is_valid():
                server_serializers.validated_data['bind_user_password'] = make_password(data['bind_user_password'])
                server_serializers.save()
                ldap_conn.unbind()
                return True
        return False
     
    except ldap.INVALID_CREDENTIALS:
        return {'msg': f'{CONSTANT_LDAP_UNVALID_CREDENTIENLS}'}
    except ldap.SERVER_DOWN:
        return {'msg': f"{CONSTANT_LDAP_UNREACHABLE}"}
    except ldap.LDAPError:
        return {'msg': f"{CONSTANT_LDAP_SEARCH_BASE}"}
