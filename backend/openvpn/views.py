from datetime import datetime
from django.http import JsonResponse
from django.core import serializers
from django.db.models.deletion import ProtectedError
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from backend.network.models import IP4Config, Interface
from backend.network.serializers import IP4ConfigSerializer, InterfaceSerializer
from backend.openvpn.manage_errors import CommandExecutionError
from .models import ServerOpenvpn, ClientOpenvpn
from .serializers import ServerOpenvpnSerializer, ClientOpenvpnSerializer
from .functions import change_status_server_openvpn, delete_openvpn_interface, json_to_str_client, json_to_str_server, openvpn_interfaces
from .server_openvpn import install_server_openvpn, delete_server_openvpn, update_server_openvpn
from .client_openvpn import delete_client_openvpn, install_client_openvpn

# Create your views here.

########################################
################ Server ################
########################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL OPENVPN SERVERS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
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
    

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN OPENVPN SERVER",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
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


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE AN OPENVPN SERVER",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['name', 'server_mode', 'protocol', 'device_mode', 'interface', 'local_port', 'tls_auth', 'ca_name', 'server_cert', 'dh_params_length', 'encryption_algorithm', 'auth_digest_algorithm', 'hardware_crypto', 'ipv4_tunnel_network', 'gateway', 'bridge', 'compression', 'type_of_service', 'duplicate_connections', 'ipv6', 'inter_clients', 'address_pool', 'dynamic_ip', 'topology', 'dns_default_domain', 'dns_servers', 'force_dns', 'ntp_servers', 'verbosity_level'],
                                                 properties={'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'description': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'server_mode': openapi.Schema(type=openapi.TYPE_OBJECT, required=['mode'], properties={'mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["remote_access", "peer_to_peer"])}),
                                                             'protocol': openapi.Schema(type=openapi.TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                             'device_mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["tun", "tap"]),
                                                             'interface': openapi.Schema(type=openapi.TYPE_STRING, description="Interface name like LAN or WAN or any"),
                                                             'local_port': openapi.Schema(type=openapi.TYPE_STRING, description="port number with 4 digits"),
                                                             'tls_auth': openapi.Schema(type=openapi.TYPE_OBJECT, description="importing tls key or generating it", 
                                                                                        required=['generate'], properties={'generate': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                           'tls_key': openapi.Schema(type=openapi.TYPE_STRING, description="tls_key only when generate is false")}),
                                                             'ca_name': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate authority name"),
                                                             'server_cert': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate name"),
                                                             'dh_params_length': openapi.Schema(type=openapi.TYPE_STRING, enum=["2048", "4096"]),
                                                             'encryption_algorithm': openapi.Schema(type=openapi.TYPE_STRING, description="example: AES-256-GCM"),
                                                             'auth_digest_algorithm': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                             'hardware_crypto': openapi.Schema(type=openapi.TYPE_STRING, enum=["No Hardware Crypto"]),
                                                             'ipv4_tunnel_network': openapi.Schema(type=openapi.TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                             'gateway': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                                             'bridge': openapi.Schema(type=openapi.TYPE_OBJECT, description="Bridge block only appears if the device mode is TAP",
                                                                                      required=['bridge_select'], properties={'bridge_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                              'bridge_interface': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the interface bridge, required when selecting bridge"),
                                                                                                                              'bridge_start_dhcp': openapi.Schema(type=openapi.TYPE_STRING, description="Address start of the interface bridge like 192.168.10.254, required when selecting bridge"),
                                                                                                                              'bridge_end_dhcp': openapi.Schema(type=openapi.TYPE_STRING, description="Address end of the interface bridge like 192.168.1.3, required when selecting bridge"),}),
                                                             'ipv4_local_network': openapi.Schema(type=openapi.TYPE_STRING, description="IPv4 local network address in format address/mask like 192.168.10.0/24"),
                                                             'ipv4_remote_network': openapi.Schema(type=openapi.TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                             'concurrent_connections': openapi.Schema(type=openapi.TYPE_STRING, description="Number of concurrent connections"),
                                                             'compression': openapi.Schema(type=openapi.TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                             'type_of_service': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'duplicate_connections': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'ipv6': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'inter_clients': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'address_pool': openapi.Schema(type=openapi.TYPE_OBJECT, description="Address pool block",
                                                                                            required=['address_pool_select'], properties={'address_pool_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                          'address_pool_start': openapi.Schema(type=openapi.TYPE_STRING, description="Address pool start like 10.8.0.2, required when selecting address pool"),
                                                                                                                                          'address_pool_end': openapi.Schema(type=openapi.TYPE_STRING, description="Address pool end like 10.8.0.250, required when selecting address pool"),}),
                                                             'dynamic_ip': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'topology': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                                                             'dns_default_domain': openapi.Schema(type=openapi.TYPE_OBJECT, description="DNS default domain block",
                                                                                                  required=['dns_default_domain_select'], properties={'dns_default_domain_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                                      'dns_default_domain_server': openapi.Schema(type=openapi.TYPE_STRING, description="Address default domain server like 8.8.8.8, required when selecting DNS default domain")}),
                                                             'dns_servers': openapi.Schema(type=openapi.TYPE_OBJECT, description="DNS servers block",
                                                                                      required=['dns_servers_select'], properties={'dns_servers_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                   'dns_server1': openapi.Schema(type=openapi.TYPE_STRING, description="Address of DNS server1 like 8.8.8.8, required when selecting DNS servers"),
                                                                                                                                   'dns_server2': openapi.Schema(type=openapi.TYPE_STRING, description="Address of DNS server2 like 8.8.4.4, Optionally you can set the second DNS server afer setting the first DNS server"),}),
                                                             'force_dns': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'ntp_servers': openapi.Schema(type=openapi.TYPE_OBJECT, description="NTP servers block",
                                                                                      required=['ntp_servers_select'], properties={'ntp_servers_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                   'ntp_server1': openapi.Schema(type=openapi.TYPE_STRING, description="Address of NTP server1 like 8.8.8.8, required when selecting NTP servers"),
                                                                                                                                   'ntp_server2': openapi.Schema(type=openapi.TYPE_STRING, description="Address of NTP server2 like 8.8.4.4, Optionally you can set the second NTP server afer setting the first NTP server"),}),
                                                             'verbosity_level': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                             
                                                                 }
                                                                 ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createServerOpenvpn(request):
    """Creating a new server in system and adding it to the database"""
    if request.method == 'POST':
        try:
            data = request.data

            name = data.get('name', '')
            description = data.get('description', '')
            server_mode = data.get('server_mode', '')
            server_mode = server_mode.get('mode', '')
            proto = data.get('protocol', '')
            dev = data.get('device_mode', '')
            interface_name = data.get('interface', '')
            port = data.get('local_port', '')
            tls_auth = data.get('tls_auth', '')
            ca_name = data.get('ca_name', '')
            server_cert_name = data.get('server_cert', '')
            dh = data.get('dh_params_length', '')
            cipher = data.get('encryption_algorithm', '')
            auth = data.get('auth_digest_algorithm', '')
            hardware_crypto = data.get('hardware_crypto', '')
            ipv4_tunnel_network = data.get('ipv4_tunnel_network', '')
            gateway = data.get('gateway', '')
            bridge = data.get('bridge', '')
            ipv4_local_network = data.get('ipv4_local_network', '')
            ipv4_remote_network = data.get('ipv4_remote_network', '')
            concurrent_connections = data.get('concurrent_connections', '')
            compression = data.get('compression', '')
            type_of_service = data.get('type_of_service', '')
            duplicate_connections = data.get('duplicate_connections', '')
            ipv6 = data.get('ipv6', '')
            inter_clients = data.get('inter_clients', '')
            dynamic_ip = data.get('dynamic_ip', '')
            address_pool = data.get('address_pool', '')
            topology = data.get('topology', '')
            dns_default_domain = data.get('dns_default_domain', '')
            dns_servers = data.get('dns_servers', '')
            force_dns_cache_update = data.get('force_dns_cache_update', '')
            ntp_servers = data.get('ntp_servers', '')
            verb = data.get('verbosity_level', '')
            interface = Interface.objects.get(name_interface=interface_name)
            interface = interface.pk
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = interface_address.ip_address
        
            ca = f'/etc/certificates_{ca_name}/ca.crt'
            cert = f'/etc/openvpn/certificates_{server_cert_name}/server.crt'
            key = f'/etc/openvpn/certificates_{server_cert_name}/server.key'
            tls = f'/etc/openvpn/server/static_{name}.key'
            server_data = {"name": name,
                           "description": description,
                           "server_mode": server_mode,
                           "proto": proto,
                           "dev": dev,
                           "interface": interface,
                           "port": port,
                           "tls": tls,
                           "ca": ca,
                           "cert": cert,
                           "key": key,
                           "dh": dh,
                           "cipher": cipher,
                           "auth": auth,
                           "hardware_crypto": hardware_crypto,
                           "ipv4_tunnel_network": ipv4_tunnel_network,
                           "gateway": gateway,
                           "ipv4_local_network": ipv4_local_network,
                           "ipv4_remote_network": ipv4_remote_network,
                           "concurrent_connections": concurrent_connections,
                           "compression": compression,
                           "type_of_service": type_of_service,
                           "duplicate_connections": duplicate_connections,
                           "ipv6": ipv6,
                           "inter_clients": inter_clients,
                           "dynamic_ip": dynamic_ip,
                           "topology": topology,
                           "force_dns_cache_update": force_dns_cache_update,
                           "verb": verb,
                           }

            if bridge.get('bridge_select', ''):
                bridge_interface = bridge.get('bridge_interface', '')
                bridge_start_dhcp = bridge.get('bridge_start_dhcp', '')
                bridge_end_dhcp = bridge.get('bridge_end_dhcp', '')
                bridge_interface_address = IP4Config.objects.get(interface_id=bridge_interface)
                data["bridge_interface_address"] = f'{bridge_interface_address.ip_address}/{bridge_interface_address.netmask}'
                server_data["bridge_interface"] = bridge_interface
                server_data["bridge_start_dhcp"] = bridge_start_dhcp
                server_data["bridge_end_dhcp"] = bridge_end_dhcp

            if address_pool.get('address_pool_select'):
                address_pool_start = address_pool.get('address_pool_start')
                address_pool_end = address_pool.get('address_pool_end')
                server_data["address_pool_start"] = address_pool_start
                server_data["address_pool_end"] = address_pool_end

            if dns_default_domain.get('dns_default_domain_select', ''):
                dns_default_domain_server = dns_default_domain.get('dns_default_domain_server', '')
                server_data["dns_default_domain_server"] = dns_default_domain_server

            if dns_servers.get('dns_servers_select', ''):
                dns_server1 = dns_servers.get('dns_server1', '')
                dns_server2 = dns_servers.get('dns_server2', '')
                server_data["dns_server1"] = dns_server1
                server_data["dns_server2"] = dns_server2
            
            if ntp_servers.get('ntp_servers_select', ''):
                ntp_server1 = ntp_servers.get('ntp_server1', '')
                ntp_server2 = ntp_servers.get('ntp_server2', '')
                server_data["ntp_server1"] = ntp_server1
                server_data["ntp_server2"] = ntp_server2

            serializer_server = ServerOpenvpnSerializer(data=server_data)
            if serializer_server.is_valid():
            
                # Update the server config
                server_conf = json_to_str_server(data)

                # Install the server in system
                install_server_openvpn(server_name=data["name"], ca_name=ca_name, dh_length=dh, tls_auth=tls_auth, server_conf=server_conf)

                # Add the server to the database
                serializer_server.save()
                return JsonResponse({"msg": f"Server {name} Configuration is done"}, status=201)
            else:
                print(serializer_server.errors)
                return JsonResponse({"msg": "Error in server configuration"}, status=400)
        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating openvpn server"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN OPENVPN SERVER",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteServerOpenvpn(request, id):
    """Deleting a server from system and then from database"""
    try:
        if (request.method == 'DELETE'):
            server = ServerOpenvpn.objects.get(id=id)
            # delete from system
            delete_server_openvpn(server.name)
            # delete from database
            server.delete()
            return JsonResponse({"msg": f"delete {server.name} succesfully"})
    except ProtectedError:
        return JsonResponse({"msg": "You have to delete Clients related to this server"})
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"msg": "This Server does not exist"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE AN OPENVPN SERVER (same as creation API)",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT,  required=['name', 'server_mode', 'protocol', 'device_mode', 'interface', 'local_port', 'tls_auth', 'ca_name', 'server_cert', 'dh_params_length', 'encryption_algorithm', 'auth_digest_algorithm', 'hardware_crypto', 'ipv4_tunnel_network', 'gateway', 'bridge', 'compression', 'type_of_service', 'duplicate_connections', 'ipv6', 'inter_clients', 'address_pool', 'dynamic_ip', 'topology', 'dns_default_domain', 'dns_servers', 'force_dns', 'ntp_servers', 'verbosity_level'],
                                                 properties={'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'description': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'server_mode': openapi.Schema(type=openapi.TYPE_OBJECT, required=['mode'], properties={'mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["remote_access", "peer_to_peer"])}),
                                                             'protocol': openapi.Schema(type=openapi.TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                             'device_mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["tun", "tap"]),
                                                             'interface': openapi.Schema(type=openapi.TYPE_STRING, description="Interface name like LAN or WAN or any"),
                                                             'local_port': openapi.Schema(type=openapi.TYPE_STRING, description="port number with 4 digits"),
                                                             'tls_auth': openapi.Schema(type=openapi.TYPE_OBJECT, description="importing tls key or generating it", 
                                                                                        required=['generate'], properties={'generate': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                           'tls_key': openapi.Schema(type=openapi.TYPE_STRING, description="tls_key only when generate is false")}),
                                                             'ca_name': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate authority name"),
                                                             'server_cert': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate name"),
                                                             'dh_params_length': openapi.Schema(type=openapi.TYPE_STRING, enum=["2048", "4096"]),
                                                             'encryption_algorithm': openapi.Schema(type=openapi.TYPE_STRING, description="example: AES-256-GCM"),
                                                             'auth_digest_algorithm': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                             'hardware_crypto': openapi.Schema(type=openapi.TYPE_STRING, enum=["No Hardware Crypto"]),
                                                             'ipv4_tunnel_network': openapi.Schema(type=openapi.TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                             'gateway': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                                             'bridge': openapi.Schema(type=openapi.TYPE_OBJECT, description="Bridge block only appears if the device mode is TAP",
                                                                                      required=['bridge_select'], properties={'bridge_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                              'bridge_interface': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the interface bridge, required when selecting bridge"),
                                                                                                                              'bridge_start_dhcp': openapi.Schema(type=openapi.TYPE_STRING, description="Address start of the interface bridge like 192.168.10.254, required when selecting bridge"),
                                                                                                                              'bridge_end_dhcp': openapi.Schema(type=openapi.TYPE_STRING, description="Address end of the interface bridge like 192.168.1.3, required when selecting bridge"),}),
                                                             'ipv4_local_network': openapi.Schema(type=openapi.TYPE_STRING, description="IPv4 local network address in format address/mask like 192.168.10.0/24"),
                                                             'ipv4_remote_network': openapi.Schema(type=openapi.TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                             'concurrent_connections': openapi.Schema(type=openapi.TYPE_STRING, description="Number of concurrent connections"),
                                                             'compression': openapi.Schema(type=openapi.TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                             'type_of_service': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'duplicate_connections': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'ipv6': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'inter_clients': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'address_pool': openapi.Schema(type=openapi.TYPE_OBJECT, description="Address pool block",
                                                                                            required=['address_pool_select'], properties={'address_pool_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                          'address_pool_start': openapi.Schema(type=openapi.TYPE_STRING, description="Address pool start like 10.8.0.2, required when selecting address pool"),
                                                                                                                                          'address_pool_end': openapi.Schema(type=openapi.TYPE_STRING, description="Address pool end like 10.8.0.250, required when selecting address pool"),}),
                                                             'dynamic_ip': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'topology': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                                                             'dns_default_domain': openapi.Schema(type=openapi.TYPE_OBJECT, description="DNS default domain block",
                                                                                                  required=['dns_default_domain_select'], properties={'dns_default_domain_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                                      'dns_default_domain_server': openapi.Schema(type=openapi.TYPE_STRING, description="Address default domain server like 8.8.8.8, required when selecting DNS default domain")}),
                                                             'dns_servers': openapi.Schema(type=openapi.TYPE_OBJECT, description="DNS servers block",
                                                                                      required=['dns_servers_select'], properties={'dns_servers_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                   'dns_server1': openapi.Schema(type=openapi.TYPE_STRING, description="Address of DNS server1 like 8.8.8.8, required when selecting DNS servers"),
                                                                                                                                   'dns_server2': openapi.Schema(type=openapi.TYPE_STRING, description="Address of DNS server2 like 8.8.4.4, Optionally you can set the second DNS server afer setting the first DNS server"),}),
                                                             'force_dns': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'ntp_servers': openapi.Schema(type=openapi.TYPE_OBJECT, description="NTP servers block",
                                                                                      required=['ntp_servers_select'], properties={'ntp_servers_select': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                                   'ntp_server1': openapi.Schema(type=openapi.TYPE_STRING, description="Address of NTP server1 like 8.8.8.8, required when selecting NTP servers"),
                                                                                                                                   'ntp_server2': openapi.Schema(type=openapi.TYPE_STRING, description="Address of NTP server2 like 8.8.4.4, Optionally you can set the second NTP server afer setting the first NTP server"),}),
                                                             'verbosity_level': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                             
                                                                 }
                                                                 ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def updateServerOpenVPN(request, id):
    """Updating a server from system and database"""
    if (request.method == 'PUT'):
        try:
            # parse the incoming information
            data = request.data
            server = ServerOpenvpn.objects.get(id=id)
            server.name = data.get('name', '')
            server.description = data.get('description', '')
            server_mode = data.get('server_mode', '')
            server.server_mode = server_mode.get('mode', '')
            server.proto = data.get('protocol', '')
            server.dev = data.get('device_mode', '')
            server.interface = Interface.objects.get(name_interface=data.get('interface', ''))
            server.port = data.get('local_port', '')
            tls_auth = data.get('tls_auth', '')
            server.tls = f'/etc/openvpn/server/static_{server.name}.key'
            ca_name = data.get('ca_name', '')
            server_cert_name = data.get('server_cert', '')
            server.ca = f'/etc/certificates_{ca_name}/ca.crt'
            server.cert = f'/etc/openvpn/certificates_{server_cert_name}/server.crt'
            server.key = f'/etc/openvpn/certificates_{server_cert_name}/server.key'
            dh = data.get('dh_params_length', '')
            if server.dh == dh:
                dh = False
            else:
                server.dh = dh
            server.cipher = data.get('encryption_algorithm', '')
            server.auth = data.get('auth_digest_algorithm', '')
            server.hardware_crypto = data.get('hardware_crypto', '')
            server.ipv4_tunnel_network = data.get('ipv4_tunnel_network', '')
            server.gateway = data.get('gateway', '')
            bridge = data.get('bridge', '')
            server.ipv4_local_network = data.get('ipv4_local_network', '')
            server.ipv4_remote_network = data.get('ipv4_remote_network', '')
            server.compression = data.get('compression', '')
            server.type_of_service = data.get('type_of_service', '')
            server.duplicate_connections = data.get('duplicate_connections', '')
            server.ipv6 = data.get('ipv6', '')
            server.inter_clients = data.get('inter_clients', '')
            address_pool = data.get('address_pool', '')
            server.dynamic_ip = data.get('dynamic_ip', '')
            server.topology = data.get('topology', '')
            dns_default_domain = data.get('dns_default_domain', '')
            server.force_dns_cache_update = data.get('force_dns_cache_update', '')
            dns_servers = data.get('dns_servers', '')
            ntp_servers = data.get('ntp_servers', '')
            server.verb = data.get('verbosity_level', '')
            interface_address = IP4Config.objects.get(interface_id=server.interface)
            data["interface_address"] = interface_address.ip_address

            if bridge.get('bridge_select', ''):
                server.bridge_interface = bridge.get('bridge_interface', '')
                server.bridge_start_dhcp = bridge.get('bridge_start_dhcp', '')
                server.bridge_end_dhcp = bridge.get('bridge_end_dhcp', '')
                bridge_interface_address = IP4Config.objects.get(interface_id=server.bridge_interface)
                data["bridge_interface_address"] = f'{bridge_interface_address.ip_address}/{bridge_interface_address.netmask}'

            if address_pool.get('address_pool_select'):
                server.address_pool_start = address_pool.get('address_pool_start')
                server.address_pool_end = address_pool.get('address_pool_end')

            if dns_default_domain.get('dns_default_domain_select', ''):
                server.dns_default_domain_server = dns_default_domain.get('dns_default_domain_server', '')

            if dns_servers.get('dns_servers_select', ''):
                server.dns_server1 = data.get('dns_server1', '')
                server.dns_server2 = data.get('dns_server2', '')

            if ntp_servers.get('ntp_servers_select', ''):
                server.ntp_server1 = data.get('ntp_server1', '')
                server.ntp_server2 = data.get('ntp_server2', '')

            data['server_mode'] = server.server_mode
            server_serializer = ServerOpenvpnSerializer(server, data=data)
            if server_serializer.is_valid():

                # Update the server config
                server_conf = json_to_str_server(data)
            
                #updating the server in system
                update_server_openvpn(server_name=server.name, dh_length=dh, tls_auth=tls_auth, server_conf=server_conf)

                #updating the server in database
                server_serializer.save()
                return JsonResponse({"msg": f"updating {server.name} succesfully"}, status=201)
            else:
                return JsonResponse({"msg": f"Error in updating server\n{server_serializer.errors}"}, status=400)
        except ServerOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO Start AN OPENVPN SERVER",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def startServerOpenvpn(request, id):
    """Starting a server and opening a tunnel. The system open a new interface and this interface is added to the database"""
    if request.method == 'POST':
        try:
            server = ServerOpenvpn.objects.get(id=id)
            change_status_server_openvpn(server_name=server.name, server_status='start')
            interfaces = openvpn_interfaces()
            for interface in interfaces:
                interface_serializer = InterfaceSerializer(data=interface)
                if interface_serializer.is_valid():
                    interface_instance  = interface_serializer.save()
                    ipv4_data = {"typeIP4": "DHCP",
                                 "ip_address": interface["ip_address"],
                                 "netmask": interface["netmask"],
                                 "interface": interface_instance.id
                                 }
                    ipv4_serializer = IP4ConfigSerializer(data=ipv4_data)
                    if ipv4_serializer.is_valid():
                        ipv4_serializer.save()
                        return JsonResponse({"msg": f"Server {server.name} is started"}, status=201)
                    else:
                        return JsonResponse({"msg": ipv4_serializer.errors}, status=400)
                else:
                    return JsonResponse({"msg": "Server was opened"}, status=400)
        
        except CommandExecutionError:
            return JsonResponse({"msg": "Error in starting openvpn server"}, status=400)
        except ServerOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO Restart AN OPENVPN SERVER",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def restartServerOpenvpn(request, id):
    """Retarting a server and reopening a tunnel."""
    if request.method == 'PUT':
        try:
            server = ServerOpenvpn.objects.get(id=id)
            interfaces_before = openvpn_interfaces()
            change_status_server_openvpn(server_name=server.name, server_status='stop')
            interfaces = openvpn_interfaces()
            interface_updated_name = delete_openvpn_interface(interfaces_before, interfaces)
            interface = Interface.objects.get(ifname=interface_updated_name)
            interface.updated_at = datetime.now()
            change_status_server_openvpn(server_name=server.name, server_status='start')
            interface.save()
            return JsonResponse({"msg": f"Server {server.name} is restarted"}, status=201)
        
        except CommandExecutionError:
            return JsonResponse({"msg": "Error in starting openvpn server"}, status=400)
        except ServerOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO STOP AN OPENVPN SERVER",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stopServerOpenvpn(request, id):
    """Stoping a server and closing a tunnel. The system delete an interface and this interface is deleted from the database"""
    if request.method == 'DELETE':
        try:
            server = ServerOpenvpn.objects.get(id=id)
            interfaces_before = openvpn_interfaces()
            interfaces = change_status_server_openvpn(server_name=server.name, server_status='stop')
            interfaces = openvpn_interfaces()
            interface_deleted_name = delete_openvpn_interface(interfaces_before, interfaces)
            if interface_deleted_name:
                interface = Interface.objects.get(ifname=interface_deleted_name)
                interface.delete()
                return JsonResponse({"msg": f"Server {server.name} is stoped"}, status=201)
            else:
                return JsonResponse({"msg": "Interface dosen't exist"}, status=404)
        
        except CommandExecutionError:
            return JsonResponse({"msg": "Error in stoping openvpn server"}, status=400)
        except ServerOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)


########################################
################ Client ################
########################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL OPENVPN CLIENTS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
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


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN OPENVPN CLIENT",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
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


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE AN OPENVPN Client",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['server_name', 'name', 'server_mode', 'protocol', 'device_mode', 'interface', 'resolv_retry', 'local_port', 'tls_auth', 'ca_name', 'client_cert', 'encryption_algorithm', 'auth_digest_algorithm', 'hardware_crypto', 'compression', 'type_of_service', 'ipv6', 'pull_routes', 'add_remove_routes', 'verbosity_level'],
                                                 properties={'server_name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the selected server"),
                                                             'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'description': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'server_mode': openapi.Schema(type=openapi.TYPE_OBJECT, required=['mode'], properties={'mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["peer_to_peer"])}),
                                                             'protocol': openapi.Schema(type=openapi.TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                             'device_mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["tun", "tap"]),
                                                             'interface': openapi.Schema(type=openapi.TYPE_INTEGER, description="Interface ID"),
                                                             'resolv_retry': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'proxy_host': openapi.Schema(type=openapi.TYPE_STRING, description="address of poxy like 10.1.12.249"),
                                                             'proxy_port': openapi.Schema(type=openapi.TYPE_STRING, pattern=r"\d\d\d\d", default="1194", desciption="port number of 4 digits"),
                                                             'proxy_authentication': openapi.Schema(type=openapi.TYPE_OBJECT, description="Additional options for proxy authentication", 
                                                                                        required=['option'], properties={'option': openapi.Schema(type=openapi.TYPE_STRING, default="none", enum=["none", "basic", "ntlm"]),
                                                                                                                         'username': openapi.Schema(type=openapi.TYPE_STRING, description="required when choosing basic in authentication method option"),
                                                                                                                         'password': openapi.Schema(type=openapi.TYPE_STRING, description="required when choosing basic in authentication method option"),}),
                                                             'local_port': openapi.Schema(type=openapi.TYPE_STRING, description="local port number with 4 digits"),
                                                             'username': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'password': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'renegotiate_time': openapi.Schema(type=openapi.TYPE_STRING, description="Number of seconds to renogotiate"),
                                                             'tls_auth': openapi.Schema(type=openapi.TYPE_OBJECT, description="importing tls key or generating it", 
                                                                                        required=['generate'], properties={'generate': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                           'tls_key': openapi.Schema(type=openapi.TYPE_STRING, description="tls_key only when generate is false")}),
                                                             'ca_name': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate authority name"),
                                                             'client_cert': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate name from Certificates list with type client"),
                                                             'dh_params_length': openapi.Schema(type=openapi.TYPE_STRING, enum=["2048", "4096"]),
                                                             'encryption_algorithm': openapi.Schema(type=openapi.TYPE_STRING, description="example: AES-256-GCM"),
                                                             'auth_digest_algorithm': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                             'hardware_crypto': openapi.Schema(type=openapi.TYPE_STRING, enum=["No Hardware Crypto"]),
                                                             'ipv4_tunnel_network': openapi.Schema(type=openapi.TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                             'ipv4_remote_network': openapi.Schema(type=openapi.TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                             'limit_outgoing_bandwidth': openapi.Schema(type=openapi.TYPE_STRING, description="Number of limit outgoing bandwith"),
                                                             'compression': openapi.Schema(type=openapi.TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                             'type_of_service': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'ipv6': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'pull_routes': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'add_remove_routes': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'verbosity_level': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                                 }
                                                                 ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createClientOpenvpn(request):
    """Creating a new client in system and adding it to the database"""
    if request.method == 'POST':
        try:
            # parse the incoming information
            data = request.data

            server_name = data.get('server_name', '')
            server = ServerOpenvpn.objects.get(name=server_name)
            server_host = IP4Config.objects.get(interface_id=server.interface).ip_address
            server_port = server.port
            # server_host = data.get('server_host', '')
            # server_port = data.get('server_port', '')
            name = data.get('name', '')
            description = data.get('description', '')
            server_mode = data.get('server_mode', '')
            server_mode = server_mode.get('mode', '')
            proto = data.get('protocol', '')
            dev = data.get('device_mode', '')
            interface = data.get('interface', '')
            resolv_retry = data.get('retry_dns', '')
            proxy_host = data.get('proxy_host', '')
            proxy_port = data.get('proxy_port', '')
            proxy_authentication = data.get('proxy_authentication', '')
            proxy_authentication_option = proxy_authentication.get('option', '')
            port = data.get('local_port', '')
            username = data.get('username', '')
            password = data.get('password', '')
            renegotiate_time = data.get('renegotiate_time', '')
            tls_auth = data.get('tls_auth', '')
            ca_name = data.get('ca_name', '')
            client_cert_name = data.get('client_cert', '')
            cipher = data.get('encryption_algorithm', '')
            auth = data.get('auth_digest_algorithm', '')
            hardware_crypto = data.get('hardware_crypto', '')
            ipv4_tunnel_network = data.get('ipv4_tunnel_network', '')
            ipv4_remote_network = data.get('ipv4_remote_network', '')
            limit_outgoing_bandwidth = data.get('limit_outgoing_bandwidth', '')
            compression = data.get('compression', '')
            type_of_service = data.get('type_of_service', '')
            ipv6 = data.get('ipv6', '')
            pull_routes = data.get('pull_routes', '')
            add_remove_routes = data.get('add_remove_routes', '')
            verb = data.get('verbosity_level', '')
            ca = f'/etc/certificates_{ca_name}/ca.crt'
            cert = f'/etc/openvpn/client/certificates_{client_cert_name}/{client_cert_name}.crt'
            key = f'/etc/openvpn/client/certificates_{client_cert_name}/{client_cert_name}.key'
            tls = f'/etc/openvpn/client/static_{name}.key'
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = interface_address.ip_address
            data["server_host"] = server_host
            data["server_port"] = server_port

            # client_conf = json_to_str_client(data)

            client_data = {"server_openvpn": server.pk,
                           "name": name,
                           "description": description,
                           "server_mode": server_mode,
                           "proto": proto,
                           "dev": dev,
                           "interface": interface,
                           "resolv_retry": resolv_retry,
                           "proxy_host": proxy_host,
                           "proxy_port": proxy_port,
                           "proxy_authentication_option": proxy_authentication_option,
                           "port": port,
                           "username": username,
                           "password": password,
                           "renegotiate_time": renegotiate_time,
                           "tls": tls,
                           "ca": ca,
                           "cert": cert,
                           "key": key,
                           "cipher": cipher,
                           "auth": auth,
                           "hardware_crypto": hardware_crypto,
                           "ipv4_tunnel_network": ipv4_tunnel_network,
                           "ipv4_remote_network": ipv4_remote_network,
                           "limit_outgoing_bandwidth": limit_outgoing_bandwidth,
                           "compression": compression,
                           "type_of_service": type_of_service,
                           "ipv6": ipv6,
                           "pull_routes": pull_routes,
                           "add_remove_routes": add_remove_routes,
                           "verb": verb,
                           }
            
            if proxy_authentication_option == 'basic':
                proxy_authentication_username = proxy_authentication.get('username', '')
                proxy_authentication_password = proxy_authentication.get('password', '')
                client_data["proxy_auth_username"] = proxy_authentication_username
                client_data["proxy_auth_password"] = proxy_authentication_password

            client_serializer = ClientOpenvpnSerializer(data=client_data)
            if client_serializer.is_valid():

                # Update the client config
                client_conf = json_to_str_client(data)
                
                # Install the client in system
                install_client_openvpn(client_name=data["name"], client_conf=client_conf, tls_auth=tls_auth)

                # Add the client to the database
                client_serializer.save()
                return JsonResponse({"msg": f"Client {data['name']} Configuration is done"}, status=201)
            else:
                return JsonResponse({"msg": f"Error in client configuration\n{client_serializer.errors}"}, status=400)
        except CommandExecutionError:
            return JsonResponse({"msg": f"Error in creating client for openvpn server"}, status=400)
        except ServerOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN OPENVPN CLIENT",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteClientOpenvpn(request, id):
    """Deleting a client from system and then from database"""
    if (request.method == 'DELETE'):
        try:

            client = ClientOpenvpn.objects.get(id=id)

            # Delete the client from system
            delete_client_openvpn(client.name)

            # Delete the client from database
            client.delete()
            return JsonResponse({"msg": f"delete {client.name} succesfully"})
        
        except ClientOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Client does not exist"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE AN OPENVPN Client (same as create)",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['server_name', 'name', 'server_mode', 'protocol', 'device_mode', 'interface', 'resolv_retry', 'local_port', 'tls_auth', 'ca_name', 'client_cert', 'encryption_algorithm', 'auth_digest_algorithm', 'hardware_crypto', 'compression', 'type_of_service', 'ipv6', 'pull_routes', 'add_remove_routes', 'verbosity_level'],
                                                 properties={'server_name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the selected server"),
                                                             'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'description': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'server_mode': openapi.Schema(type=openapi.TYPE_OBJECT, required=['mode'], properties={'mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["peer_to_peer"])}),
                                                             'protocol': openapi.Schema(type=openapi.TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                             'device_mode': openapi.Schema(type=openapi.TYPE_STRING, enum=["tun", "tap"]),
                                                             'interface': openapi.Schema(type=openapi.TYPE_INTEGER, description="Interface ID"),
                                                             'resolv_retry': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'proxy_host': openapi.Schema(type=openapi.TYPE_STRING, description="address of poxy like 10.1.12.249"),
                                                             'proxy_port': openapi.Schema(type=openapi.TYPE_STRING, pattern=r"\d\d\d\d", default="1194", desciption="port number of 4 digits"),
                                                             'proxy_authentication': openapi.Schema(type=openapi.TYPE_OBJECT, description="Additional options for proxy authentication", 
                                                                                        required=['option'], properties={'option': openapi.Schema(type=openapi.TYPE_STRING, default="none", enum=["none", "basic", "ntlm"]),
                                                                                                                         'username': openapi.Schema(type=openapi.TYPE_STRING, description="required when choosing basic in authentication method option"),
                                                                                                                         'password': openapi.Schema(type=openapi.TYPE_STRING, description="required when choosing basic in authentication method option"),}),
                                                             'local_port': openapi.Schema(type=openapi.TYPE_STRING, description="local port number with 4 digits"),
                                                             'username': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'password': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'renegotiate_time': openapi.Schema(type=openapi.TYPE_STRING, description="Number of seconds to renogotiate"),
                                                             'tls_auth': openapi.Schema(type=openapi.TYPE_OBJECT, description="importing tls key or generating it", 
                                                                                        required=['generate'], properties={'generate': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                                           'tls_key': openapi.Schema(type=openapi.TYPE_STRING, description="tls_key only when generate is false")}),
                                                             'ca_name': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate authority name"),
                                                             'client_cert': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate name from Certificates list with type client"),
                                                             'dh_params_length': openapi.Schema(type=openapi.TYPE_STRING, enum=["2048", "4096"]),
                                                             'encryption_algorithm': openapi.Schema(type=openapi.TYPE_STRING, description="example: AES-256-GCM"),
                                                             'auth_digest_algorithm': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                             'hardware_crypto': openapi.Schema(type=openapi.TYPE_STRING, enum=["No Hardware Crypto"]),
                                                             'ipv4_tunnel_network': openapi.Schema(type=openapi.TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                             'ipv4_remote_network': openapi.Schema(type=openapi.TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                             'limit_outgoing_bandwidth': openapi.Schema(type=openapi.TYPE_STRING, description="Number of limit outgoing bandwith"),
                                                             'compression': openapi.Schema(type=openapi.TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                             'type_of_service': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'ipv6': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'pull_routes': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'add_remove_routes': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'verbosity_level': openapi.Schema(type=openapi.TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                                 }
                                                                 ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def updateClientOpenvpn(request, id):
    """Updating a client from system and database"""
    if (request.method == 'PUT'):
        try:

            client = ClientOpenvpn.objects.get(id=id)
            data = request.data
            server_name = data.get('server_name', '')
            server = ServerOpenvpn.objects.get(name=server_name)
            client.server_openvpn = server
            server_host = IP4Config.objects.get(id=Interface.objects.get(id=server.interface).pk).ip_address
            server_port = server.port
            # server_host = data.get('server_host', '')
            # server_port = data.get('server_port', '')
            client.name = data.get('name', '')
            client.description = data.get('description', '')
            server_mode = data.get('server_mode', '')
            client.server_mode = server_mode.get('mode', '')
            client.proto = data.get('protocol', '')
            client.dev = data.get('device_mode', '')
            client.interface = data.get('interface', '')
            client.resolv_retry = data.get('retry_dns', '')
            client.port = data.get('local_port', '')
            client.auth = data.get('auth_digest_algorithm', '')
            client.cipher = data.get('encryption_algorithm', '')
            client.verb = data.get('verbosity_level', '')
            client.proxy_host = data.get('proxy_host', '')
            client.proxy_port = data.get('proxy_port', '')
            proxy_authentication = data.get('proxy_authentication', '')
            client.proxy_authentication_option = proxy_authentication.get('option', '')
            client.port = data.get('local_port', '')
            client.username = data.get('username', '')
            client.password = data.get('password', '')
            client.renegotiate_time = data.get('renegotiate_time', '')
            tls_auth = data.get('tls_auth', '')
            ca_name = data.get('ca_name', '')
            client_cert_name = data.get('client_cert', '')
            client.tls = f'/etc/openvpn/client/static_{client.name}.key'
            client.ca = f'/etc/certificates_{ca_name}/ca.crt'
            client.cert = f'/etc/openvpn/client/certificates_{client_cert_name}/{client_cert_name}.crt'
            client.key = f'/etc/openvpn/client/certificates_{client_cert_name}/{client_cert_name}.key'
            client.cipher = data.get('encryption_algorithm', '')
            client.auth = data.get('auth_digest_algorithm', '')
            client.hardware_crypto = data.get('hardware_crypto', '')
            client.ipv4_tunnel_network = data.get('ipv4_tunnel_network', '')
            client.ipv4_remote_network = data.get('ipv4_remote_network', '')
            client.limit_outgoing_bandwidth = data.get('limit_outgoing_bandwidth', '')
            client.compression = data.get('compression', '')
            client.type_of_service = data.get('type_of_service', '')
            client.ipv6 = data.get('ipv6', '')
            client.pull_routes = data.get('pull_routes', '')
            client.add_remove_routes = data.get('add_remove_routes', '')
            client.verb = data.get('verbosity_level', '')
            interface_address = IP4Config.objects.get(interface_id=client.interface)

            if client.proxy_authentication_option == 'basic':
                client.proxy_auth_username = proxy_authentication.get('username', '')
                client.proxy_auth_password = proxy_authentication.get('password', '')
                
            data["interface_address"] = interface_address.ip_address
            data["server_host"] = server_host
            data["server_port"] = server_port
            # client_conf = json_to_str_client(data)
            data['server_openvpn'] = server.pk
            data['server_mode'] = client.server_mode

            client_serializer = ClientOpenvpnSerializer(client, data=data)
            if client_serializer.is_valid():

                # Update the client config
                client_conf = json_to_str_client(data)

                # Updating the client in system
                install_client_openvpn(client_name=client.name, client_conf=client_conf, tls_auth=tls_auth)

                # Updating the client in database
                client_serializer.save()
                return JsonResponse({"msg": f"updating {client.name} succesfully"}, status=201)
            else:
                return JsonResponse({"msg": f"{client_serializer.errors}"}, status=400)
            
        except ClientOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Client does not exist"}, status=400)
        except ServerOpenvpn.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=400)
