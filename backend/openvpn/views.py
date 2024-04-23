import time
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError
from django.contrib.auth.hashers import check_password, make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from backend.network.models import IP4Config, Interface
from backend.openvpn.constant_variables import PATH_SERVER_STATIC
from backend.openvpn.list_servers_clients import get_list_all_client_openvpn, get_list_all_server_openvpn, get_one_client_openvpn, get_one_server_openvpn
from utils.constant_variables import ERROR_MESSAGES_CREATING, ERROR_MESSAGES_DELETE_USED_SERVER, ERROR_MESSAGES_EXPORTING, ERROR_MESSAGES_INEXISTANT, ERROR_MESSAGES_STATUS_OPENVPN_SERVER, IPV4_CONFIG, SUCCESS_MESSAGES_CREATING_ITEM, SUCCESS_MESSAGES_DELETE, SUCCESS_MESSAGES_STATUS_OPENVPN_SERVER, SUCCESS_MESSAGES_UPDATE
from utils.errors_utils import CommandExecutionError
from .servers_status import change_status_server_openvpn
from .models import ServerOpenvpn, ClientOpenvpn
from .serializers import ServerOpenvpnSerializer, ClientOpenvpnSerializer
from .utils import json_to_str_client, json_to_str_server
from .server_openvpn import install_server_openvpn_in_system, delete_server_openvpn_in_system, update_server_openvpn_in_system
from .client_openvpn import delete_client_openvpn_in_system, export_client_in_system, install_client_openvpn_in_system, update_client_openvpn_in_system

# Create your views here.

########################################
################ Server ################
########################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL OPENVPN SERVERS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_server_openvpn(request):
    """Getting all servers from database"""
    list_server_openvpn = []
    if (request.method == 'GET'):
        list_server_openvpn = get_list_all_server_openvpn()
        return JsonResponse(list_server_openvpn, safe=False)
    

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN OPENVPN SERVER",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_server_openvpn(request, id):
    """Getting server by id from database"""
    if (request.method == 'GET'):
        server = get_one_server_openvpn(id)
        return JsonResponse(server, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE AN OPENVPN SERVER",
                     request_body=Schema(type=TYPE_OBJECT, 
                                         required=['name', 'server_mode', 'protocol', 'device_mode', 'interface', 'local_port',
                                                   'tls_auth', 'ca_name', 'server_cert', 'dh_params_length', 'encryption_algorithm',
                                                   'auth_digest_algorithm', 'gateway', 'bridge', 'compression', 'type_of_service',
                                                   'duplicate_connections', 'ipv6', 'inter_clients', 'address_pool', 'dynamic_ip',
                                                   'dns_default_domain', 'dns_servers', 'force_dns', 'ntp_servers'],
                                                   properties={'name': Schema(type=TYPE_STRING),
                                                               'description': Schema(type=TYPE_STRING),
                                                               'server_mode': Schema(type=TYPE_OBJECT, required=['mode'], properties={'mode': Schema(type=TYPE_STRING, enum=["remote_access", "peer_to_peer"])}),
                                                               'protocol': Schema(type=TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                               'device_mode': Schema(type=TYPE_STRING, enum=["tun", "tap"]),
                                                               'interface': Schema(type=TYPE_STRING, description="Interface name like LAN or WAN or Any"),
                                                               'local_port': Schema(type=TYPE_STRING, description="port number with 4 digits"),
                                                               'tls_auth': Schema(type=TYPE_OBJECT, description="importing tls key or generating it", required=['generate'], 
                                                                                  properties={'generate': Schema(type=TYPE_BOOLEAN, default=False), 
                                                                                              'tls_key': Schema(type=TYPE_STRING, description="tls_key only when generate is false")}),
                                                               'ca_name': Schema(type=TYPE_STRING, description="Certificate authority name"),
                                                               'server_cert': Schema(type=TYPE_STRING, description="Certificate name"),
                                                               'dh_params_length': Schema(type=TYPE_STRING, enum=["2048", "4096"]),
                                                               'encryption_algorithm': Schema(type=TYPE_STRING, description="example: AES-256-GCM"),
                                                               'auth_digest_algorithm': Schema(type=TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                               'ipv4_tunnel_network': Schema(type=TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                               'gateway': Schema(type=TYPE_BOOLEAN),
                                                               'bridge': Schema(type=TYPE_OBJECT, description="Bridge block only appears if the device mode is TAP", required=['bridge_select'],
                                                                                properties={'bridge_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                            'bridge_interface': Schema(type=TYPE_INTEGER, description="ID of the interface bridge, required when selecting bridge"),
                                                                                            'bridge_start_dhcp': Schema(type=TYPE_STRING, description="Address start of the interface bridge like 192.168.10.254, required when selecting bridge"),
                                                                                            'bridge_end_dhcp': Schema(type=TYPE_STRING, description="Address end of the interface bridge like 192.168.1.3, required when selecting bridge"),}),
                                                               'ipv4_local_network': Schema(type=TYPE_STRING, description="IPv4 local network address in format address/mask like 192.168.10.0/24"),
                                                               'ipv4_remote_network': Schema(type=TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                               'concurrent_connections': Schema(type=TYPE_STRING, description="Number of concurrent connections"),
                                                               'compression': Schema(type=TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                               'type_of_service': Schema(type=TYPE_BOOLEAN, default=False),
                                                               'duplicate_connections': Schema(type=TYPE_BOOLEAN, default=False),
                                                               'ipv6': Schema(type=TYPE_BOOLEAN, default=False),
                                                               'inter_clients': Schema(type=TYPE_BOOLEAN, default=False),
                                                               'address_pool': Schema(type=TYPE_OBJECT, description="Address pool block", required=['address_pool_select'],
                                                                                      properties={'address_pool_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                  'address_pool_start': Schema(type=TYPE_STRING, description="Address pool start like 10.8.0.2, required when selecting address pool"),
                                                                                                  'address_pool_end': Schema(type=TYPE_STRING, description="Address pool end like 10.8.0.250, required when selecting address pool"),}),
                                                               'dynamic_ip': Schema(type=TYPE_BOOLEAN, default=False),
                                                               'dns_default_domain': Schema(type=TYPE_OBJECT, description="DNS default domain block", required=['dns_default_domain_select'],
                                                                                            properties={'dns_default_domain_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                        'dns_default_domain_server': Schema(type=TYPE_STRING, description="Address default domain server like 8.8.8.8, required when selecting DNS default domain")}),
                                                               'dns_servers': Schema(type=TYPE_OBJECT, description="DNS servers block",
                                                                                      required=['dns_servers_select'], properties={'dns_servers_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                                                   'dns_server1': Schema(type=TYPE_STRING, description="Address of DNS server1 like 8.8.8.8, required when selecting DNS servers"),
                                                                                                                                   'dns_server2': Schema(type=TYPE_STRING, description="Address of DNS server2 like 8.8.4.4, Optionally you can set the second DNS server afer setting the first DNS server"),}),
                                                               'force_dns_cache_update': Schema(type=TYPE_BOOLEAN, default=False),
                                                               'ntp_servers': Schema(type=TYPE_OBJECT, description="NTP servers block", required=['ntp_servers_select'],
                                                                                     properties={'ntp_servers_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                 'ntp_server1': Schema(type=TYPE_STRING, description="Address of NTP server1 like 8.8.8.8, required when selecting NTP servers"),
                                                                                                 'ntp_server2': Schema(type=TYPE_STRING, description="Address of NTP server2 like 8.8.4.4, Optionally you can set the second NTP server afer setting the first NTP server"),}),
                                                               'client_management': Schema(type=TYPE_OBJECT, description="Client Management Port block", required=['client_management_select'],
                                                                                           properties={"client_management_select": Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                       "port": Schema(type=TYPE_STRING, description="Port number like 17562"),
                                                                                                       "password": Schema(type=TYPE_STRING)}),
                                                               'verbosity_level': Schema(type=TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                               }
                                                               ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_server_openvpn(request):
    """Creating a new server in system and adding it to the database"""
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
        dns_default_domain = data.get('dns_default_domain', '')
        dns_servers = data.get('dns_servers', '')
        force_dns_cache_update = data.get('force_dns_cache_update', '')
        ntp_servers = data.get('ntp_servers', '')
        client_management = data.get('client_management')
        verb = data.get('verbosity_level', '')
        if interface_name != "Any":
            interface = Interface.objects.get(name_interface=interface_name)
            interface = interface.pk
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = interface_address.ip_address
        else:
            interface = "Any"
    
        server_data = {"name": name,
                        "description": description,
                        "server_mode": server_mode,
                        "proto": proto,
                        "dev": dev,
                        "interface": interface_name,
                        "port": port,
                        "ca_name": ca_name,
                        "cert_name": server_cert_name,
                        "dh": dh,
                        "cipher": cipher,
                        "auth": auth,
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
        
        if client_management.get('client_management_select'):
            client_management_port = client_management.get('port')
            client_management_password = client_management.get('password')
            server_data["client_management_port"] = client_management_port
            server_data["client_management_password"] = make_password(client_management_password)
            data["client_management"]["password"] = server_data["client_management_password"]

        serializer_server = ServerOpenvpnSerializer(data=server_data)
        if serializer_server.is_valid():
        
            # Update the server config
            server_conf = json_to_str_server(data)

            # Install the server in system
            install_server_openvpn_in_system(server_name=data["name"], ca_name=ca_name, tls_auth=tls_auth, dh_length=dh, 
                                             server_conf=server_conf)

            # Add the server to the database
            serializer_server.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('Server', name)}, status=201)
        
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)
    
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format('openvpn server')}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('interface')}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(IPV4_CONFIG)}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN OPENVPN SERVER",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_server_openvpn(request, id):
    """Deleting a server from system and then from database"""
    try:
        server = ServerOpenvpn.objects.get(id=id)
        
        if len(Interface.objects.filter(name_interface=server.name)):
            interface = Interface.objects.get(name_interface=server.name)
            if len(IP4Config.objects.filter(interface_id=interface.pk)):
                ipv4 = IP4Config.objects.get(interface_id=interface.pk)
                ipv4.delete()
                interface.delete()

        # delete from system
        delete_server_openvpn_in_system(server.name)

        # delete from database
        server.delete()
        return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(server.name)}, status=201)
    except ProtectedError:
        return JsonResponse({"error": ERROR_MESSAGES_DELETE_USED_SERVER}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE AN OPENVPN SERVER (same as creation API)",
                     request_body=Schema(type=TYPE_OBJECT,  required=['name', 'server_mode', 'protocol', 'device_mode', 'interface', 'local_port', 'tls_auth', 'ca_name', 'server_cert', 'dh_params_length', 'encryption_algorithm', 'auth_digest_algorithm', 'gateway', 'bridge', 'compression', 'type_of_service', 'duplicate_connections', 'ipv6', 'inter_clients', 'address_pool', 'dynamic_ip', 'dns_default_domain', 'dns_servers', 'force_dns', 'ntp_servers'],
                                                 properties={'name': Schema(type=TYPE_STRING),
                                                             'description': Schema(type=TYPE_STRING),
                                                             'server_mode': Schema(type=TYPE_OBJECT, required=['mode'], properties={'mode': Schema(type=TYPE_STRING, enum=["remote_access", "peer_to_peer"])}),
                                                             'protocol': Schema(type=TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                             'device_mode': Schema(type=TYPE_STRING, enum=["tun", "tap"]),
                                                             'interface': Schema(type=TYPE_STRING, description="Interface name like LAN or WAN or Any"),
                                                             'local_port': Schema(type=TYPE_STRING, description="port number with 4 digits"),
                                                             'tls_auth': Schema(type=TYPE_OBJECT, description="importing tls key or generating it", required=['generate'],
                                                                                properties={'generate': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                            'tls_key': Schema(type=TYPE_STRING, description="tls_key only when generate is false")}),
                                                             'ca_name': Schema(type=TYPE_STRING, description="Certificate authority name"),
                                                             'server_cert': Schema(type=TYPE_STRING, description="Certificate name"),
                                                             'dh_params_length': Schema(type=TYPE_STRING, enum=["2048", "4096"]),
                                                             'encryption_algorithm': Schema(type=TYPE_STRING, description="example: AES-256-GCM"),
                                                             'auth_digest_algorithm': Schema(type=TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                             'ipv4_tunnel_network': Schema(type=TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                             'gateway': Schema(type=TYPE_BOOLEAN),
                                                             'bridge': Schema(type=TYPE_OBJECT, description="Bridge block only appears if the device mode is TAP", required=['bridge_select'],
                                                                              properties={'bridge_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                          'bridge_interface': Schema(type=TYPE_INTEGER, description="ID of the interface bridge, required when selecting bridge"),
                                                                                          'bridge_start_dhcp': Schema(type=TYPE_STRING, description="Address start of the interface bridge like 192.168.10.254, required when selecting bridge"),
                                                                                          'bridge_end_dhcp': Schema(type=TYPE_STRING, description="Address end of the interface bridge like 192.168.1.3, required when selecting bridge"),}),
                                                             'ipv4_local_network': Schema(type=TYPE_STRING, description="IPv4 local network address in format address/mask like 192.168.10.0/24"),
                                                             'ipv4_remote_network': Schema(type=TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                             'concurrent_connections': Schema(type=TYPE_STRING, description="Number of concurrent connections"),
                                                             'compression': Schema(type=TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                             'type_of_service': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'duplicate_connections': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'ipv6': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'inter_clients': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'address_pool': Schema(type=TYPE_OBJECT, description="Address pool block", required=['address_pool_select'],
                                                                                    properties={'address_pool_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                'address_pool_start': Schema(type=TYPE_STRING, description="Address pool start like 10.8.0.2, required when selecting address pool"),
                                                                                                'address_pool_end': Schema(type=TYPE_STRING, description="Address pool end like 10.8.0.250, required when selecting address pool"),}),
                                                             'dynamic_ip': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'dns_default_domain': Schema(type=TYPE_OBJECT, description="DNS default domain block", required=['dns_default_domain_select'],
                                                                                          properties={'dns_default_domain_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                      'dns_default_domain_server': Schema(type=TYPE_STRING, description="Address default domain server like 8.8.8.8, required when selecting DNS default domain")}),
                                                             'dns_servers': Schema(type=TYPE_OBJECT, description="DNS servers block", required=['dns_servers_select'],
                                                                                   properties={'dns_servers_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                               'dns_server1': Schema(type=TYPE_STRING, description="Address of DNS server1 like 8.8.8.8, required when selecting DNS servers"),
                                                                                               'dns_server2': Schema(type=TYPE_STRING, description="Address of DNS server2 like 8.8.4.4, Optionally you can set the second DNS server afer setting the first DNS server"),}),
                                                             'force_dns_cache_update': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'ntp_servers': Schema(type=TYPE_OBJECT, description="NTP servers block", required=['ntp_servers_select'],
                                                                                   properties={'ntp_servers_select': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                               'ntp_server1': Schema(type=TYPE_STRING, description="Address of NTP server1 like 8.8.8.8, required when selecting NTP servers"),
                                                                                               'ntp_server2': Schema(type=TYPE_STRING, description="Address of NTP server2 like 8.8.4.4, Optionally you can set the second NTP server afer setting the first NTP server"),}),
                                                             'client_management': Schema(type=TYPE_OBJECT, description="Client Management Port block", required=['client_management_select'],
                                                                                           properties={"client_management_select": Schema(type=TYPE_BOOLEAN, default=False),
                                                                                                       "port": Schema(type=TYPE_STRING, description="Port number like 17562"),
                                                                                                       "password": Schema(type=TYPE_STRING, description="Old password"),
                                                                                                       "new_password": Schema(type=TYPE_STRING, description="New password")}),
                                                             'verbosity_level': Schema(type=TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                             }
                                                             ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_server_openvpn(request, id):
    """Updating a server from system and database"""
    try:
        # parse the incoming information
        data = request.data
        server = ServerOpenvpn.objects.get(id=id)
        previous_name = server.name
        server.name = data.get('name', '')
        server.description = data.get('description', '')
        server_mode = data.get('server_mode', '')
        server.server_mode = server_mode.get('mode', '')
        server.proto = data.get('protocol', '')
        server.dev = data.get('device_mode', '')
        server.interface=data.get('interface', '')
        server.port = data.get('local_port', '')
        tls_auth = data.get('tls_auth', '')
        server.ca_name = data.get('ca_name', '')
        server.cert_name = data.get('server_cert', '')
        server.dh = data.get('dh_params_length', '')
        server.cipher = data.get('encryption_algorithm', '')
        server.auth = data.get('auth_digest_algorithm', '')
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
        dns_default_domain = data.get('dns_default_domain', '')
        server.force_dns_cache_update = data.get('force_dns_cache_update', '')
        dns_servers = data.get('dns_servers', '')
        ntp_servers = data.get('ntp_servers', '')
        client_management = data.get('client_management')
        server.verb = data.get('verbosity_level', '')
        if server.interface != "Any":
            server.interface = Interface.objects.get(name_interface=server.interface)
            interface_address = IP4Config.objects.get(interface_id=server.interface)
            data["interface_address"] = interface_address.ip_address

        if bridge.get('bridge_select', ''):
            server.bridge_interface = bridge.get('bridge_interface', '')
            server.bridge_start_dhcp = bridge.get('bridge_start_dhcp', '')
            server.bridge_end_dhcp = bridge.get('bridge_end_dhcp', '')
            bridge_interface_address = IP4Config.objects.get(interface_id=server.bridge_interface)
            data["bridge_interface_address"] = f'{bridge_interface_address.ip_address}/{bridge_interface_address.netmask}'
        else:
            server.bridge_interface = None
            server.bridge_start_dhcp = None
            server.bridge_end_dhcp = None

        if address_pool.get('address_pool_select'):
            server.address_pool_start = address_pool.get('address_pool_start')
            server.address_pool_end = address_pool.get('address_pool_end')
        else:
            server.address_pool_start = None
            server.address_pool_end = None

        if dns_default_domain.get('dns_default_domain_select', ''):
            server.dns_default_domain_server = dns_default_domain.get('dns_default_domain_server', '')
        else:
            server.dns_default_domain_server = None

        if dns_servers.get('dns_servers_select', ''):
            server.dns_server1 = dns_servers.get('dns_server1', '')
            server.dns_server2 = dns_servers.get('dns_server2', '')
        else:
            server.dns_server1 = None
            server.dns_server2 = None

        if ntp_servers.get('ntp_servers_select', ''):
            server.ntp_server1 = ntp_servers.get('ntp_server1', '')
            server.ntp_server2 = ntp_servers.get('ntp_server2', '')
        else:
            server.ntp_server1 = None
            server.ntp_server2 = None
        
        if client_management.get('client_management_select'):
            server.client_management_port = client_management.get('port')
            if check_password(client_management.get('password'), server.client_management_password):
                server.client_management_password = make_password(client_management.get('new_password'))
            data["client_management"]["password"] = server.client_management_password
        else:
            server.client_management_port = None
            server.client_management_password = None

        data['server_mode'] = server.server_mode
        serializer_server = ServerOpenvpnSerializer(server, data=data)
        if serializer_server.is_valid():

            # Update the server config
            server_conf = json_to_str_server(data)
        
            #updating the server in system
            update_server_openvpn_in_system(previous_server_name=previous_name, server_name=server.name, tls_auth=tls_auth, 
                                            server_conf=server_conf, server_status=server.server_status)

            #updating the server in database
            serializer_server.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(server.name)}, status=201)
        
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('interface')}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(IPV4_CONFIG)}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO Start AN OPENVPN SERVER",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_server_openvpn(request, id):
    """Starting a server and opening a tunnel"""
    try:
        server = ServerOpenvpn.objects.get(id=id)
        change_status_server_openvpn(server_name=server.name, server_status='start')
        time.sleep(3)
        return JsonResponse({"msg": SUCCESS_MESSAGES_STATUS_OPENVPN_SERVER.format(server.name, 'started')}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STATUS_OPENVPN_SERVER.format('starting')}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO Restart AN OPENVPN SERVER",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def restart_server_openvpn(request, id):
    """Retarting a server and reopening a tunnel"""
    try:
        server = ServerOpenvpn.objects.get(id=id)
        change_status_server_openvpn(server_name=server.name, server_status='restart')
        time.sleep(3)
        return JsonResponse({"msg": SUCCESS_MESSAGES_STATUS_OPENVPN_SERVER.format(server.name, 'restarted')}, status=201)
    
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STATUS_OPENVPN_SERVER.format('starting')}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO STOP AN OPENVPN SERVER",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_server_openvpn(request, id):
    """Stoping a server and closing a tunnel"""
    try:
        server = ServerOpenvpn.objects.get(id=id)
        change_status_server_openvpn(server_name=server.name, server_status='stop')
        time.sleep(3)
        return JsonResponse({"msg": SUCCESS_MESSAGES_STATUS_OPENVPN_SERVER.format(server.name, 'stoped')}, status=201)
    
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STATUS_OPENVPN_SERVER.format('stoping')}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)


########################################
################ Client ################
########################################

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL OPENVPN CLIENTS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_client_openvpn(request):
    """Getting all clients from database"""
    if (request.method == 'GET'):
        list_client_openvpn = get_list_all_client_openvpn()
        return JsonResponse(list_client_openvpn, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN OPENVPN CLIENT",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_client_openvpn(request, id):
    """Getting client by id from database"""
    if (request.method == 'GET'):
        client = get_one_client_openvpn(id)
        return JsonResponse(client, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE AN OPENVPN Client",
                     request_body=Schema(type=TYPE_OBJECT, required=['server_name', 'name', 'server_mode', 'protocol', 'device_mode', 'resolv_retry', 'local_port', 'tls_auth', 'ca_name', 'client_cert', 'encryption_algorithm', 'auth_digest_algorithm', 'compression', 'type_of_service', 'ipv6', 'pull_routes', 'add_remove_routes'],
                                                 properties={'name': Schema(type=TYPE_STRING),
                                                             'description': Schema(type=TYPE_STRING),
                                                             'server_mode': Schema(type=TYPE_OBJECT, required=['mode'], properties={'mode': Schema(type=TYPE_STRING, enum=["peer_to_peer"])}),
                                                             'protocol': Schema(type=TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                             'device_mode': Schema(type=TYPE_STRING, enum=["tun", "tap"]),
                                                             'resolv_retry': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'proxy_host': Schema(type=TYPE_STRING, description="address of poxy like 10.1.12.249"),
                                                             'proxy_port': Schema(type=TYPE_STRING, pattern=r"\d\d\d\d", default="1194", desciption="port number of 4 digits"),
                                                             'proxy_authentication': Schema(type=TYPE_OBJECT, description="Additional options for proxy authentication", required=['option'],
                                                                                            properties={'option': Schema(type=TYPE_STRING, default="none", enum=["none", "basic", "ntlm"]),
                                                                                                        'username': Schema(type=TYPE_STRING, description="required when choosing basic in authentication method option"),
                                                                                                        'password': Schema(type=TYPE_STRING, description="required when choosing basic in authentication method option"),}),
                                                             'local_port': Schema(type=TYPE_STRING, description="local port number with 4 digits"),
                                                             'username': Schema(type=TYPE_STRING),
                                                             'password': Schema(type=TYPE_STRING),
                                                             'renegotiate_time': Schema(type=TYPE_STRING, description="Number of seconds to renogotiate"),
                                                             'tls_auth': Schema(type=TYPE_OBJECT, description="importing tls key or generating it", required=['generate'],
                                                                                properties={'generate': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                            'tls_key': Schema(type=TYPE_STRING, description="tls_key only when generate is false")}),
                                                             'ca_name': Schema(type=TYPE_STRING, description="Certificate authority name"),
                                                             'client_cert': Schema(type=TYPE_STRING, description="Certificate name from Certificates list with type client"),
                                                             'dh_params_length': Schema(type=TYPE_STRING, enum=["2048", "4096"]),
                                                             'encryption_algorithm': Schema(type=TYPE_STRING, description="example: AES-256-GCM"),
                                                             'auth_digest_algorithm': Schema(type=TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                             'ipv4_tunnel_network': Schema(type=TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                             'ipv4_remote_network': Schema(type=TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                             'limit_outgoing_bandwidth': Schema(type=TYPE_STRING, description="Number of limit outgoing bandwith"),
                                                             'compression': Schema(type=TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                             'type_of_service': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'ipv6': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'pull_routes': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'add_remove_routes': Schema(type=TYPE_BOOLEAN, default=False),
                                                             'verbosity_level': Schema(type=TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                             'server_remote': Schema(type=TYPE_ARRAY, description="Set the list of servers remote",
                                                                                     items=Schema(type=TYPE_OBJECT, required=['host', 'port'],
                                                                                                  properties={'host': Schema(type=TYPE_STRING),
                                                                                                              'port': Schema(type=TYPE_STRING),
                                                                                                              },)),
                                                             }
                                                             ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_client_openvpn(request):
    """Creating a new client in system and adding it to the database"""
    try:
        # parse the incoming information
        data = request.data

        name = data.get('name', '')
        description = data.get('description', '')
        server_mode = data.get('server_mode', '')
        server_mode = server_mode.get('mode', '')
        proto = data.get('protocol', '')
        dev = data.get('device_mode', '')
        resolv_retry = data.get('resolv_retry', '')
        proxy_host = data.get('proxy_host', '')
        proxy_port = data.get('proxy_port', '')
        proxy_authentication = data.get('proxy_authentication', '')
        proxy_authentication_option = proxy_authentication.get('option', '')
        port = data.get('local_port', '')
        username = data.get('username', '')
        data["password"] = make_password(data.get('password', ''))
        password = data["password"]
        renegotiate_time = data.get('renegotiate_time', '')
        tls_auth = data.get('tls_auth', '')
        ca_name = data.get('ca_name', '')
        cert_name = data.get('client_cert', '')
        cipher = data.get('encryption_algorithm', '')
        auth = data.get('auth_digest_algorithm', '')
        ipv4_tunnel_network = data.get('ipv4_tunnel_network', '')
        ipv4_remote_network = data.get('ipv4_remote_network', '')
        limit_outgoing_bandwidth = data.get('limit_outgoing_bandwidth', '')
        compression = data.get('compression', '')
        type_of_service = data.get('type_of_service', '')
        ipv6 = data.get('ipv6', '')
        pull_routes = data.get('pull_routes', '')
        add_remove_routes = data.get('add_remove_routes', '')
        verb = data.get('verbosity_level', '')
        servers_list = data.get('server_remote', '')
        server_remote = ''
        for server in servers_list:
            server_remote += f'{server["host"]}:{server["port"]},'
        server_remote = server_remote[:len(server_remote)-1]

        client_data = {"name": name,
                        "description": description,
                        "server_mode": server_mode,
                        "proto": proto,
                        "dev": dev,
                        "resolv_retry": resolv_retry,
                        "proxy_host": proxy_host,
                        "proxy_port": proxy_port,
                        "proxy_authentication_option": proxy_authentication_option,
                        "port": port,
                        "username": username,
                        "password": password,
                        "renegotiate_time": renegotiate_time,
                        "ca_name": ca_name,
                        "cert_name": cert_name,
                        "cipher": cipher,
                        "auth": auth,
                        "ipv4_tunnel_network": ipv4_tunnel_network,
                        "ipv4_remote_network": ipv4_remote_network,
                        "limit_outgoing_bandwidth": limit_outgoing_bandwidth,
                        "compression": compression,
                        "type_of_service": type_of_service,
                        "ipv6": ipv6,
                        "pull_routes": pull_routes,
                        "add_remove_routes": add_remove_routes,
                        "verb": verb,
                        "server_remote": server_remote,
                        }
        
        if proxy_authentication_option == 'basic':
            client_data["proxy_auth_username"] = proxy_authentication.get('username', '')
            data["proxy_authentication"]["password"] = make_password(proxy_authentication.get('password', ''))
            client_data["proxy_auth_password"] = data["proxy_authentication"]["password"]

        client_serializer = ClientOpenvpnSerializer(data=client_data)
        if client_serializer.is_valid():

            # Update the client config
            client_conf = json_to_str_client(data)
            
            # Install the client in system
            install_client_openvpn_in_system(client_name=data["name"], client_conf=client_conf, tls_auth=tls_auth)

            # Add the client to the database
            client_serializer.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('Client', data['name'])}, status=201)
        else:
            return JsonResponse({"error": list(client_serializer.errors.values())[0][0]}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format('client for openvpn server')}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(IPV4_CONFIG)}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN OPENVPN CLIENT",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_client_openvpn(request, id):
    """Deleting a client from system and then from database"""
    try:

        client = ClientOpenvpn.objects.get(id=id)

        # Delete the client from system
        delete_client_openvpn_in_system(client.name)

        # Delete the client from database
        client.delete()
        return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(client.name)}, status=201)
    
    except ClientOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Client')}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE AN OPENVPN Client (same as create)",
                     request_body=Schema(type=TYPE_OBJECT, required=['server_name', 'name', 'server_mode', 'protocol', 'device_mode', 'resolv_retry', 'local_port', 'tls_auth', 'ca_name', 'client_cert', 'encryption_algorithm', 'auth_digest_algorithm', 'compression', 'type_of_service', 'ipv6', 'pull_routes', 'add_remove_routes',],
                                         properties={'name': Schema(type=TYPE_STRING),
                                                     'description': Schema(type=TYPE_STRING),
                                                     'server_mode': Schema(type=TYPE_OBJECT, required=['mode'], properties={'mode': Schema(type=TYPE_STRING, enum=["peer_to_peer"])}),
                                                     'protocol': Schema(type=TYPE_STRING, enum=["udp", "udp4", "udp6", "tcp", "tcp4", "tcp6"]),
                                                     'device_mode': Schema(type=TYPE_STRING, enum=["tun", "tap"]),
                                                     'resolv_retry': Schema(type=TYPE_BOOLEAN, default=False),
                                                     'proxy_host': Schema(type=TYPE_STRING, description="address of poxy like 10.1.12.249"),
                                                     'proxy_port': Schema(type=TYPE_STRING, pattern=r"\d\d\d\d", default="1194", desciption="port number of 4 digits"),
                                                     'proxy_authentication': Schema(type=TYPE_OBJECT, required=['option'], description="Additional options for proxy authentication", 
                                                                                    properties={'option': Schema(type=TYPE_STRING, default="none", enum=["none", "basic", "ntlm"]),
                                                                                                'username': Schema(type=TYPE_STRING, description="required when choosing basic in authentication method option"),
                                                                                                'password': Schema(type=TYPE_STRING, description="Old password if user choose basic and want to change proxy password"),
                                                                                                'new_password': Schema(type=TYPE_STRING, description="New password if user choose basic and want to change proxy password"),}),
                                                     'local_port': Schema(type=TYPE_STRING, description="local port number with maximum of 5 digits"),
                                                     'username': Schema(type=TYPE_STRING),
                                                     'password': Schema(type=TYPE_STRING, description="Old password if user want to change password for user authentication"),
                                                     'new_password': Schema(type=TYPE_STRING, description="New password if user want to change password for user authentication"),
                                                     'renegotiate_time': Schema(type=TYPE_STRING, description="Number of seconds to renogotiate"),
                                                     'tls_auth': Schema(type=TYPE_OBJECT, description="importing tls key or generating it", required=['generate'],
                                                                        properties={'generate': Schema(type=TYPE_BOOLEAN, default=False),
                                                                                    'tls_key': Schema(type=TYPE_STRING, description="tls_key only when generate is false")}),
                                                     'ca_name': Schema(type=TYPE_STRING, description="Certificate authority name"),
                                                     'client_cert': Schema(type=TYPE_STRING, description="Certificate name from Certificates list with type client"),
                                                     'dh_params_length': Schema(type=TYPE_STRING, enum=["2048", "4096"]),
                                                     'encryption_algorithm': Schema(type=TYPE_STRING, description="example: AES-256-GCM"),
                                                     'auth_digest_algorithm': Schema(type=TYPE_STRING, pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
                                                     'ipv4_tunnel_network': Schema(type=TYPE_STRING, description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
                                                     'ipv4_remote_network': Schema(type=TYPE_STRING, description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
                                                     'limit_outgoing_bandwidth': Schema(type=TYPE_STRING, description="Number of limit outgoing bandwith"),
                                                     'compression': Schema(type=TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
                                                     'type_of_service': Schema(type=TYPE_BOOLEAN, default=False),
                                                     'ipv6': Schema(type=TYPE_BOOLEAN, default=False),
                                                     'pull_routes': Schema(type=TYPE_BOOLEAN, default=False),
                                                     'add_remove_routes': Schema(type=TYPE_BOOLEAN, default=False),
                                                     'verbosity_level': Schema(type=TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
                                                     'server_remote': Schema(type=TYPE_ARRAY, description="Set the list of servers remote",
                                                                             items=Schema(type=TYPE_OBJECT, required=['host', 'port'],
                                                                                          properties={'host': Schema(type=TYPE_STRING),
                                                                                                      'port': Schema(type=TYPE_STRING),
                                                                                                      },)),
                                                             }
                                                             ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_client_openvpn(request, id):
    """Updating a client from system and database"""
    try:
        data = request.data

        client = ClientOpenvpn.objects.get(id=id)
        previous_name = client.name
        client.name = data.get('name', '')
        client.description = data.get('description', '')
        server_mode = data.get('server_mode', '')
        client.server_mode = server_mode.get('mode', '')
        client.proto = data.get('protocol', '')
        client.dev = data.get('device_mode', '')
        client.resolv_retry = data.get('resolv_retry', '')
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
        if check_password(data.get('password', ''), client.password):
            client.password = make_password(data.get('new_password', ''))
        data["password"] = client.password
        client.renegotiate_time = data.get('renegotiate_time', '')
        tls_auth = data.get('tls_auth', '')
        client.ca_name = data.get('ca_name', '')
        client.cert_name = data.get('client_cert', '')
        client.cipher = data.get('encryption_algorithm', '')
        client.auth = data.get('auth_digest_algorithm', '')
        client.ipv4_tunnel_network = data.get('ipv4_tunnel_network', '')
        client.ipv4_remote_network = data.get('ipv4_remote_network', '')
        client.limit_outgoing_bandwidth = data.get('limit_outgoing_bandwidth', '')
        client.compression = data.get('compression', '')
        client.type_of_service = data.get('type_of_service', '')
        client.ipv6 = data.get('ipv6', '')
        client.pull_routes = data.get('pull_routes', '')
        client.add_remove_routes = data.get('add_remove_routes', '')
        client.verb = data.get('verbosity_level', '')
        servers_list = data.get('server_remote', '')
        client.server_remote = ''
        for server in servers_list:
            client.server_remote += f'{server["host"]}:{server["port"]},'
        client.server_remote = client.server_remote[:len(client.server_remote)-1]

        if client.proxy_authentication_option == 'basic':
            client.proxy_auth_username = proxy_authentication.get('username', '')
            if check_password(proxy_authentication.get('password', ''), client.proxy_auth_password):
                client.proxy_auth_password = make_password(proxy_authentication.get('password', ''))
            data["proxy_authentication"]["password"] = client.proxy_auth_password
            
        data['server_mode'] = client.server_mode
        data['server_remote'] = client.server_remote

        client_serializer = ClientOpenvpnSerializer(client, data=data)
        if client_serializer.is_valid():
            data['server_remote'] = servers_list
            # Update the client config
            client_conf = json_to_str_client(data)

            # Updating the client in system
            update_client_openvpn_in_system(previous_client_name=previous_name, client_name=client.name, 
                                            client_conf=client_conf, tls_auth=tls_auth)

            # Updating the client in database
            client_serializer.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(client.name)}, status=201)
        
        return JsonResponse({"error": list(client_serializer.errors.values())[0][0]}, status=400)
        
    except ClientOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Client')}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(IPV4_CONFIG)}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DOWNLOAD A CLIENT",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def export_client_openvpn(request, id):
    """Exporting a Client openvpn"""
    try:
        client = ClientOpenvpn.objects.get(id=id)
        with open(f'/etc/openvpn/client/client_{client.name}.ovpn') as config_file:
            config_input = config_file.read()
        list_balise_client = ['ca', 'cert', 'key', 'crl-verify', 'tls-auth']
        config_input = export_client_in_system(list_balise_client, config_input)

        return JsonResponse({"client": config_input}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_EXPORTING.format("openvpn client")}, status=400)
    except ClientOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('CA')}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO GENERATE AN OPENVPN Client FROM A SERVER",
                     request_body=Schema(type=TYPE_OBJECT, required=['name', 'client_cert'],
                                                 properties={'name': Schema(type=TYPE_STRING),
                                                             'client_cert': Schema(type=TYPE_STRING, description="Certificate name from Certificates list with type client"),
                                                             'interface_address': Schema(type=TYPE_STRING, description="Set an interface address for the client to connect to it if the server is configured on interface Any")}
                                                             ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def generate_client_openvpn(request, id):
    """Generating a new client from a server in system and adding it to the database"""
    try:
        # parse the incoming information
        data = request.data
        server = ServerOpenvpn.objects.get(id=id)

        # Construct a complete data variable:
        # 1. Getting from API body
        # 2. Taking some parameters from server
        # 3. Set default values for the rest of fields
        name = data.get('name', '')
        data['protocol'] = server.proto
        data['device_mode'] = server.dev
        data['resolv_retry'] = False
        data['proxy_host'] = ''
        data['proxy_port'] = ''
        data['proxy_authentication'] = {'option': 'none'}
        data['local_port'] = ''
        data['username'] = ''
        data['password'] = ''
        data['renegotiate_time'] = ''
        # Get the same TLS as the server
        with open(PATH_SERVER_STATIC.format(server.name)) as tls_file:
            tls_key = tls_file.read()
            tls_auth = {"generate": False,
                        "tls_key": tls_key}
        data['tls_auth'] = tls_auth
        data['ca_name'] = server.ca_name
        cert_name = data.get('client_cert', '')
        data['encryption_algorithm'] = server.cipher
        data['auth_digest_algorithm'] = server.auth
        data['ipv4_tunnel_network'] = ''
        data['ipv4_remote_network'] = ''
        data['limit_outgoing_bandwidth'] = ''
        data['compression'] = server.compression
        data['type_of_service'] = False
        data['ipv6'] = False
        data['pull_routes'] = False
        data['add_remove_routes'] = False
        data['verbosity_level'] = '3'
        data['server_remote'] = [{"port": server.port}]

        if server.interface != "Any":
            server_interface = Interface.objects.get(name_interface=server.interface)
            interface_address = IP4Config.objects.get(interface_id=server_interface)
            server_remote = f'{interface_address.ip_address}:{server.port}'
            data['server_remote'][0]["host"] = interface_address.ip_address
        else:
            server_remote = f"{data['interface_address']}:{server.port}"
            data['server_remote'][0]["host"] = data['interface_address']

        client_data = {"name": name,
                        "description": f"Client generate from server {server.name}",
                        "server_mode": "peer_to_peer",
                        "proto": server.proto,
                        "dev": server.dev,
                        "resolv_retry": False,
                        "proxy_host": '',
                        "proxy_port": '',
                        "proxy_authentication_option": 'none',
                        "port": '',
                        "username": '',
                        "password": '',
                        "renegotiate_time": '',
                        "ca_name": server.ca_name,
                        "cert_name": cert_name,
                        "cipher": server.cipher,
                        "auth": server.auth,
                        "ipv4_tunnel_network": '',
                        "ipv4_remote_network": '',
                        "limit_outgoing_bandwidth": '',
                        "compression": server.compression,
                        "type_of_service": False,
                        "ipv6": False,
                        "pull_routes": False,
                        "add_remove_routes": False,
                        "verb": "3",
                        "server_remote": server_remote,
                        }

        client_serializer = ClientOpenvpnSerializer(data=client_data)
        if client_serializer.is_valid():

            # Update the client config
            client_conf = json_to_str_client(data)
            
            # Install the client in system
            install_client_openvpn_in_system(client_name=name, client_conf=client_conf, tls_auth=tls_auth)

            # Add the client to the database
            client_serializer.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('Client', data['name'])}, status=201)
        else:
            return JsonResponse({"error": list(client_serializer.errors.values())[0][0]}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format('client for openvpn server')}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Server')}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(IPV4_CONFIG)}, status=400)
