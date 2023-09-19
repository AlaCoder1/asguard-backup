from django.http import JsonResponse
import json
from rest_framework.authentication import SessionAuthentication

from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from network.models import IP4Config
from .service_openvpn import *
from .models import *
from .serializers import *
from .functions import CommandExecutionError, json_to_str_client, json_to_str_server
from .server_openvpn import install_server_openvpn, delete_server_openvpn, update_server_openvpn
from .client_openvpn import delete_client_openvpn, install_client_openvpn, update_client_openvpn
from django.core import serializers

# Create your views here.

################ Server ################
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getAllServerOpenvpn(request):
    """Getting all servers from database"""
    list_openvpn = []
    if (request.method == 'GET'):
        openvpn = ServerOpenvpn.objects.all()
        openvpnDict = serializers.serialize("json",openvpn)
        res = json.loads(openvpnDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_openvpn.append(res[i]['fields'])
        return JsonResponse(list_openvpn, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getServerOpenvpn(request, id):
    """Getting server by id from database"""
    if (request.method == 'GET'):
        server_openvpn = ServerOpenvpn.objects.filter(pk=id)
        server_openvpnDict = serializers.serialize("json", server_openvpn)
        res = json.loads(server_openvpnDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        return JsonResponse(res[0]['fields'], safe=False)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createServerOpenvpn(request):
    """Creating a new server in system and adding it to the database"""
    if request.method == 'POST':
        try:
            data = request.data

            server_name = data.get('name', '')
            description = data.get('description', '')
            proto = data.get('protocol', '')
            dev = data.get('device_mode', '')
            interface = data.get('interface', '')
            port = data.get('local_port', '')
            dh = data.get('dh_params_length', '')
            cipher = data.get('encryption_algorithm', '')
            auth = data.get('auth_digest_algorithm', '')
            hardware_crypto = data.get('hardware_crypto', '')
            ipv4_local_network = data.get('ipv4_local_network', '')
            ipv4_remote_network = data.get('ipv4_remote_network', '')
            gateway = data.get('gateway', '')
            compression = data.get('compression', '')
            type_of_service = data.get('type_of_service', '')
            duplicate_connections = data.get('duplicate_connections', '')
            ipv6 = data.get('ipv6', '')
            inter_clients = data.get('inter_clients', '')
            dynamic_ip = data.get('dynamic_ip', '')
            topology = data.get('topology', '')
            dns_default_domain = data.get('dns_default_domain', '')
            dns_default_domain_select = dns_default_domain.get('dns_default_domain_select', '')
            dns_default_domain_server = dns_default_domain.get('dns_default_domain_server', '')
            dns_servers = data.get('dns_servers', '')
            dns_servers_select = dns_servers.get('dns_servers_select', '')
            dns_server1 = dns_servers.get('dns_server1', '')
            dns_server2 = dns_servers.get('dns_server2', '')
            force_dns_cache_update = data.get('force_dns_cache_update', '')
            ntp_servers = data.get('ntp_servers', '')
            ntp_servers_select = ntp_servers.get('ntp_servers_select', '')
            ntp_server1 = ntp_servers.get('ntp_server1', '')
            ntp_server2 = ntp_servers.get('ntp_server2', '')
            verb = data.get('verbosity_level', '')
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = interface_address.ip_address
            server_conf = json_to_str_server(data)

            ca = ''
            cert = ''
            key = ''
            secret = ''
            cert_method = data.get('cert_method', '')
            if cert_method.get('method_name', '') == 'cert':
                ca_name = data.get('ca_name', '')
                server_cert_name = data.get('server_cert', '')
                ca = f'/etc/certificates_{ca_name}/ca.crt'
                cert = f'/etc/openvpn/certificates_{server_cert_name}/server.crt'
                key = f'/etc/openvpn/certificates_{server_cert_name}/server.key'
            else:
                secret = f'/etc/openvpn/server/static_{server_name}.key'
            server_data = {"name": server_name,
                           "description": description,
                           "proto": proto,
                           "dev": dev,
                           "interface": interface,
                           "port": port,
                           "ca": ca,
                           "cert": cert,
                           "key": key,
                           "secret": secret,
                           "dh": dh,
                           "cipher": cipher,
                           "auth": auth,
                           "hardware_crypto": hardware_crypto,
                           "ipv4_local_network": ipv4_local_network,
                           "ipv4_remote_network": ipv4_remote_network,
                           "gateway": gateway,
                           "compression": compression,
                           "type_of_service": type_of_service,
                           "duplicate_connections": duplicate_connections,
                           "ipv6": ipv6,
                           "inter_clients": inter_clients,
                           "dynamic_ip": dynamic_ip,
                           "topology": topology,
                           "dns_default_domain": dns_default_domain_server,
                           "dns_server1": dns_server1,
                           "dns_server2": dns_server2,
                           "force_dns_cache_update": force_dns_cache_update,
                           "ntp_server1": ntp_server1,
                           "ntp_server2": ntp_server2,
                           "verb": verb,
                           }
            serializer_server = ServerOpenvpnSerializer(data=server_data)
            if serializer_server.is_valid():

                # Install the server in system
                install_server_openvpn(server_name=data["name"], ca_name=ca_name, server_conf=server_conf, cert_method=cert_method,
                                       dh_length=dh)

                # Add the server to the database
                serializer_server.save()
                return JsonResponse({"msg": f"Server {server_name} Configuration is done"}, status=201)
            else:
                print(serializer_server.errors)
                return JsonResponse({"msg": "Error in server configuration"}, status=401)
        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating openvpn server"}, status=401)


@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def deleteServerOpenvpn(request, id):
    """Deleting a server from system and then from database"""
    if (request.method == 'DELETE'):
        server = ServerOpenvpn.objects.get(id=id)
        # delete from system
        delete_server_openvpn(server.name)
        # delete from database
        server.delete()
        return JsonResponse({"msg": f"delete {server.name} succesfully"})


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def updateServerOpenVPN(request, id):
    """Updating a server from system and database"""
    if (request.method == 'PUT'):
        server = ServerOpenvpn.objects.get(id=id)
        data = request.data

        server.name = data.get('name', '')
        server.description = data.get('description', '')
        server.proto = data.get('protocol', '')
        server.dev = data.get('device_mode', '')
        server.interface = Interface.objects.get(id=data.get('interface', ''))
        server.port = data.get('local_port', '')
        server.dh = data.get('dh_params_length', '')
        server.cipher = data.get('encryption_algorithm', '')
        server.auth = data.get('auth_digest_algorithm', '')
        server.hardware_crypto = data.get('hardware_crypto', '')
        server.ipv4_local_network = data.get('ipv4_local_network', '')
        server.ipv4_remote_network = data.get('ipv4_remote_network', '')
        server.gateway = data.get('gateway', '')
        server.compression = data.get('compression', '')
        server.type_of_service = data.get('type_of_service', '')
        server.duplicate_connections = data.get('duplicate_connections', '')
        server.ipv6 = data.get('ipv6', '')
        server.inter_clients = data.get('inter_clients', '')
        server.dynamic_ip = data.get('dynamic_ip', '')
        server.topology = data.get('topology', '')
        dns_default_domain = data.get('dns_default_domain', '')
        server.dns_default_domain = dns_default_domain.get('dns_default_domain_server', '')
        server.dns_server1 = data.get('dns_server1', '')
        server.dns_server2 = data.get('dns_server2', '')
        server.force_dns_cache_update = data.get('force_dns_cache_update', '')
        server.ntp_server1 = data.get('ntp_server1', '')
        server.ntp_server2 = data.get('ntp_server2', '')
        server.verb = data.get('verbosity_level', '')
        interface_address = IP4Config.objects.get(interface_id=server.interface)
        data["interface_address"] = interface_address.ip_address

        ca = ''
        cert = ''
        key = ''
        secret = ''
        cert_method = data.get('cert_method', '')
        if cert_method.get('method_name', '') == 'cert':
            ca_name = data.get('ca_name', '')
            server_cert_name = data.get('server_cert', '')
            ca = f'/etc/certificates_{ca_name}/ca.crt'
            cert = f'/etc/openvpn/certificates_{server_cert_name}/server.crt'
            key = f'/etc/openvpn/certificates_{server_cert_name}/server.key'
        else:
            secret = f'/etc/openvpn/server/static_{server.name}.key'

        server_conf = json_to_str_server(data)
        server.ca = ca
        server.cert = cert
        server.key = key
        data['ca'] = ca
        data['cert'] = cert
        data['key'] = key
        data['secret'] = secret
        data['dns_default_domain'] = dns_default_domain.get('dns_default_domain_server', '')
        server_serializer = ServerOpenvpnSerializer(server, data=data)
        if server_serializer.is_valid():
        
            #updating the server in system
            print('name= ', server.name)
            update_server_openvpn(server_name=server.name, server_conf=server_conf, cert_method=cert_method, dh_length=server.dh)

            #updating the server in database
            server_serializer.save()
            return JsonResponse({"msg": f"updating {server.name} succesfully"}, status=201)
        else:
            return JsonResponse({"msg": f"{server_serializer.errors}"}, status=401)


################ Client ################
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getAllClientOpenvpn(request):
    """Getting all clients from database"""
    list_openvpn = []
    if (request.method == 'GET'):
        openvpn = ClientOpenvpn.objects.all()
        openvpnDict = serializers.serialize("json",openvpn)
        res = json.loads(openvpnDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_openvpn.append(res[i]['fields'])
        return JsonResponse(list_openvpn, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getClientOpenvpn(request, id):
    """Getting client by id from database"""
    if (request.method == 'GET'):
        client_openvpn = ClientOpenvpn.objects.filter(pk=id)
        client_openvpn = serializers.serialize("json", client_openvpn)
        res = json.loads(client_openvpn)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        return JsonResponse(res[0]['fields'], safe=False)


@api_view(['POST'])
# @authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createClientOpenvpn(request):
    """Creating a new client in system and adding it to the database"""
    if request.method == 'POST':
        try:
            data = request.data
            client_conf = json_to_str_client(data)
            # parse the incoming information
            data = request.data

            server_name = data.get('server_name', '')
            server = ServerOpenvpn.objects.get(name=server_name)
            client_name = data.get('name', '')
            description = data.get('description', '')
            proto = data.get('protocol', '')
            dev = data.get('device_mode', '')
            interface = data.get('interface', '')
            resolv_retry = data.get('retry_dns', '')
            port = data.get('local_port', '')
            server_mode = data.get('server_mode', '')
            cert_method = data.get('cert_method', '')
            cipher = data.get('encryption_algorithm', '')
            auth = data.get('auth_digest_algorithm', '')
            hardware_crypto = data.get('hardware_crypto', '')
            ipv4_remote = data.get('ipv4_remote', '')
            compression = data.get('compression', '')
            type_of_service = data.get('type_of_service', '')
            ipv6 = data.get('ipv6', '')
            verb = data.get('verbosity_level', '')
            ca = ''
            cert = ''
            key = ''
            secret = ''
            if cert_method.get('method_name', '') == 'cert':
                ca_name = cert_method.get('ca_name', '')
                client_cert_name = cert_method.get('client_cert', '')
                ca = f'/etc/certificates_{ca_name}/ca.crt'
                cert = f'/etc/openvpn/client/certificates_{client_cert_name}/{client_cert_name}.crt'
                key = f'/etc/openvpn/client/certificates_{client_cert_name}/{client_cert_name}.key'

            client_data = {"server_openvpn": server.pk,
                           "name": client_name,
                           "description": description,
                           "proto": proto,
                           "dev": dev,
                           "interface": interface,
                           "resolv_retry": resolv_retry,
                           "port": port,
                           "ca": ca,
                           "cert": cert,
                           "key": key,
                           "cipher": cipher,
                           "auth": auth,
                           "hardware_crypto": hardware_crypto,
                           "ipv4_remote": ipv4_remote,
                           "compression": compression,
                           "type_of_service": type_of_service,
                           "ipv6": ipv6,
                           "verb": verb,
                           }
            client_serializer = ClientOpenvpnSerializer(data=client_data)
            if client_serializer.is_valid():
                # Install the client in system
                install_client_openvpn(client_name=data["name"], client_conf=client_conf)

                # Add the client to the database
                client_serializer.save()
                return JsonResponse({"msg": "Client Configuration is done"}, status=201)
            else:
                return JsonResponse({"msg": f"Error in client configuration\n{client_serializer.errors}"}, status=401)
        except CommandExecutionError:
            return JsonResponse({"msg": f"Error in creating client for openvpn server"}, status=401)


@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def deleteClientOpenvpn(request, id):
    """Deleting a client from system and then from database"""
    if (request.method == 'DELETE'):
        client = ClientOpenvpn.objects.get(id=id)

        # Delete the client from system
        delete_client_openvpn(client.name)

        # Delete the client from database
        client.delete()
        return JsonResponse({"msg": f"delete {client.name} succesfully"})


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def updateClientOpenvpn(request, id):
    """Updating a client from system and database"""
    if (request.method == 'PUT'):
        client = ClientOpenvpn.objects.get(id=id)
        data = request.data
        server_name = data.get('server_name', '')
        server = ServerOpenvpn.objects.get(server_name=server_name)
        client.name = data.get('client_name', '')
        client.port = data.get('local_port', '')
        client.proto = data.get('protocol', '')
        # explicit_exit_notify = models.CharField(max_length=100, default=None)
        # remote = models.CharField(max_length=100, default=None)
        client.dev = data.get('device_mode', '')
        # resolv_retry = models.CharField(max_length=100, default=None)
        # nobind = models.CharField(max_length=100, default=None)
        # persist_key = models.CharField(max_length=100, default=None)
        # persist_tun = models.CharField(max_length=100, default=None)
        # remote_cert_tls = models.CharField(max_length=100, default=None)
        # verify_x509_name = models.CharField(max_length=100, default=None)
        client.auth = data.get('auth_digest_algorithm', '')
        # auth_nocache = models.CharField(max_length=100, default=None)
        client.cipher = data.get('encryption_algorithm', '')
        # tls_client = models.CharField(max_length=100, default=None)
        # tls_version_min = models.CharField(max_length=100, default=None, null=True, blank=True)
        # tls_cipher = models.CharField(max_length=100, default=None)
        # ignore_unknown_option = models.CharField(max_length=100, default=None)
        # setenv = models.CharField(max_length=100, default=None)
        client.verb = data.get('verbosity_level', '')
        # ca_certificate = models.TextField(default=None, blank=True)
        # cert_certificate = models.TextField(default=None, blank=True)
        # private_key = models.TextField(default=None, blank=True)
        # tls_crypt = models.TextField(default=None, blank=True)
        client_conf = json_to_str_client(data)
        data['server_openvpn'] = server.pk
        client_serializer = ClientOpenvpnSerializer(client, data=data)
        if client_serializer.is_valid():
            # Updating the client in system
            update_client_openvpn(client_name=client.client_name, client_conf=client_conf)

            # Updating the client in database
            client_serializer.save()
            return JsonResponse({"msg": f"updating {server.server_name} succesfully"}, status=201)
        else:
            return JsonResponse({"msg": f"{client_serializer.error_messages}"}, status=401)
