from django.http import JsonResponse
import json
from rest_framework.authentication import SessionAuthentication

from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .service_openvpn import *
from .models import *
from .serializers import *
from .functions import CommandExecutionError, json_to_str_client, json_to_str_server
from .server_openvpn import install_server_openvpn, delete_server_openvpn, update_server_openvpn
from .client_openvpn import delete_client_openvpn, install_client_openvpn, update_client_openvpn
from django.core import serializers

from network.models import Interface

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
            server_conf = json_to_str_server(data)

            # parse the incoming information
            data = request.data
            server_name = data.get('server_name', '')
            description = data.get('description', '')
            port = data.get('local_port', '')
            proto = data.get('protocol', '')
            dev = data.get('device_mode', '')
            # user = data.get('user', '')
            # group = data.get('group', '')
            # persist_key = data.get('persist_key', '')
            # persist_tun = data.get('persist_tun', '')
            # keepalive = data.get('keepalive', '')
            topology = data.get('topology', '')
            compression = data.get('compression', '')
            # server = data.get('server', '')
            # ifconfig_pool_persist = data.get('ifconfig_pool_persist', '')
            # push_ipv4_option1 = data.get('push_ipv4_option1', '')
            # push_ipv4_option2 = data.get('push_ipv4_option2', '')
            # push_ipv4_option3 = data.get('push_ipv4_option3', '')
            # push_ipv4_option4 = data.get('push_ipv4_option3', '')
            # server_ipv6 = data.get('port', '')
            # tun_ipv6 = data.get('tun_ipv6', '')
            # push_ipv6_option1 = data.get('push_ipv6_option1', '')
            # push_ipv6_option2 = data.get('push_ipv6_option2', '')
            # push_ipv6_option3 = data.get('push_ipv6_option3', '')
            dh = data.get('dh_params_length', '')
            # ecdh_curve = data.get('ecdh_curve', '')
            # tls_crypt = data.get('tls_crypt', '')
            # crl_verify = data.get('crl_verify', '')
            # ca = data.get('ca', '')
            # cert = data.get('cert', '')
            # key = data.get('key', '')
            auth = data.get('auth_digest_algorithm', '')
            cipher = data.get('encryption_algorithm', '')
            # ncp_ciphers = data.get('ncp_ciphers', '')
            # tls_server = data.get('tls_server', '')
            # tls_version_min = data.get('tls_version_min', '')
            # tls_cipher = data.get('tls_cipher', '')
            # client_config_dir = data.get('port', '')
            # status = data.get('status', '')
            verb = data.get('verbosity_level', '')
            interface_name = data.get('interface', '')
            interface_object = Interface.objects.get(ifname=interface_name)
            server_data = {"server_name": server_name,
                        "description": description,
                        "port": port,
                        "proto": proto,
                        "dev": dev,
                        "topology": topology,
                        "compression": compression,
                        "dh": dh,
                        "auth": auth,
                        "cipher": cipher,
                        "verb": verb,
                        "interface": interface_object.pk,
                        }
            serializer_server = ServerOpenvpnSerializer(data=server_data)
            if serializer_server.is_valid():

                # Install the server in system
                install_server_openvpn(server_name=data["server_name"], server_conf=server_conf)

                # Add the server to the database
                serializer_server.save()
                return JsonResponse({"msg": "Server Configuration is done"}, status=201)
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
        delete_server_openvpn(server.server_name)
        # delete from database
        server.delete()
        return JsonResponse({"msg": f"delete {server.server_name} succesfully"})


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def updateServerOpenVPN(request, id):
    """Updating a server from system and database"""
    if (request.method == 'PUT'):
        server = ServerOpenvpn.objects.get(id=id)
        data = request.data
        server.server_name = data.get('server_name', '')
        server.description = data.get('description', '')
        server.port = data.get('local_port', '')
        server.proto = data.get('protocol', '')
        server.dev = data.get('device_mode', '')
        # user = data.get('user', '')
        # group = data.get('group', '')
        # persist_key = data.get('persist_key', '')
        # persist_tun = data.get('persist_tun', '')
        # keepalive = data.get('keepalive', '')
        server.topology = data.get('topology', '')
        server.compression = data.get('compression', '')
        # server = data.get('server', '')
        # ifconfig_pool_persist = data.get('ifconfig_pool_persist', '')
        # push_ipv4_option1 = data.get('push_ipv4_option1', '')
        # push_ipv4_option2 = data.get('push_ipv4_option2', '')
        # push_ipv4_option3 = data.get('push_ipv4_option3', '')
        # push_ipv4_option4 = data.get('push_ipv4_option3', '')
        # server_ipv6 = data.get('port', '')
        # tun_ipv6 = data.get('tun_ipv6', '')
        # push_ipv6_option1 = data.get('push_ipv6_option1', '')
        # push_ipv6_option2 = data.get('push_ipv6_option2', '')
        # push_ipv6_option3 = data.get('push_ipv6_option3', '')
        server.dh = data.get('dh_params_length', '')
        # ecdh_curve = data.get('ecdh_curve', '')
        # tls_crypt = data.get('tls_crypt', '')
        # crl_verify = data.get('crl_verify', '')
        # ca = data.get('ca', '')
        # cert = data.get('cert', '')
        # key = data.get('key', '')
        server.auth = data.get('auth_digest_algorithm', '')
        server.cipher = data.get('encryption_algorithm', '')
        # ncp_ciphers = data.get('ncp_ciphers', '')
        # tls_server = data.get('tls_server', '')
        # tls_version_min = data.get('tls_version_min', '')
        # tls_cipher = data.get('tls_cipher', '')
        # client_config_dir = data.get('port', '')
        # status = data.get('status', '')
        server.verb = data.get('verbosity_level', '')
        interface_name = data.get('interface', '')
        server_conf = json_to_str_server(data)
        interface_object = Interface.objects.get(ifname=interface_name)
        server.interface = interface_object
        data['interface'] = interface_object.pk
        server_serializer = ServerOpenvpnSerializer(server, data=data)
        if server_serializer.is_valid():
        
            #updating the server in system
            update_server_openvpn(server_name=server.server_name, server_conf=server_conf)

            #updating the server in database
            server_serializer.save()
            return JsonResponse({"msg": f"updating {server.server_name} succesfully"}, status=201)
        else:
            return JsonResponse({"msg": f"{server_serializer.error_messages}"}, status=401)


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
            server = ServerOpenvpn.objects.get(server_name=server_name)
            client_name = data.get('client_name', '')
            port = data.get('local_port', '')
            proto = data.get('protocol', '')
            # explicit_exit_notify = models.CharField(max_length=100, default=None)
            # remote = models.CharField(max_length=100, default=None)
            dev = data.get('device_mode', '')
            # resolv_retry = models.CharField(max_length=100, default=None)
            # nobind = models.CharField(max_length=100, default=None)
            # persist_key = models.CharField(max_length=100, default=None)
            # persist_tun = models.CharField(max_length=100, default=None)
            # remote_cert_tls = models.CharField(max_length=100, default=None)
            # verify_x509_name = models.CharField(max_length=100, default=None)
            auth = data.get('auth_digest_algorithm', '')
            # auth_nocache = models.CharField(max_length=100, default=None)
            cipher = data.get('encryption_algorithm', '')
            # tls_client = models.CharField(max_length=100, default=None)
            # tls_version_min = models.CharField(max_length=100, default=None, null=True, blank=True)
            # tls_cipher = models.CharField(max_length=100, default=None)
            # ignore_unknown_option = models.CharField(max_length=100, default=None)
            # setenv = models.CharField(max_length=100, default=None)
            verb = data.get('verbosity_level', '')
            # ca_certificate = models.TextField(default=None, blank=True)
            # cert_certificate = models.TextField(default=None, blank=True)
            # private_key = models.TextField(default=None, blank=True)
            # tls_crypt = models.TextField(default=None, blank=True)

            client_data = {"server_openvpn": server.pk,
                           "client_name": client_name,
                           "port": port,
                           "proto": proto,
                           "dev": dev,
                           "auth": auth,
                           "cipher": cipher,
                           "verb": verb,
                           }
            client_serializer = ClientOpenvpnSerializer(data=client_data)
            if client_serializer.is_valid():
                # Install the client in system
                install_client_openvpn(client_name=data["client_name"], client_conf=client_conf)

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
        delete_client_openvpn(client.client_name)

        # Delete the client from database
        client.delete()
        return JsonResponse({"msg": f"delete {client.client_name} succesfully"})


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
        client.client_name = data.get('client_name', '')
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
