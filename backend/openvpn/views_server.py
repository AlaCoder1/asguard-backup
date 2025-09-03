import time
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models.deletion import ProtectedError
from django.contrib.auth.hashers import check_password, make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import IN_PATH, Parameter, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.network.models import IP4Config, Interface
from backend.dashboard.models import Services
from backend.openvpn.constant_variables import CONSTANT_BODY_OPENVPN_SERVER
from backend.openvpn.list_servers_clients import get_list_all_server_openvpn, get_one_server_openvpn
from utils.errors_utils import CommandExecutionError
from utils.utils_address import fix_ipv4_address
from .servers_status import change_status_server_openvpn
from .models import ServerOpenvpn
from .serializers import ServerOpenvpnSerializer
from .utils import check_validity_server, json_to_str_server
from .server_openvpn import install_server_openvpn_in_system, delete_server_openvpn_in_system, update_server_openvpn_in_system
from django.views.decorators.http import require_http_methods


# Constants
CONSTANT_OPENVPN_SERVER = _('openvpn server')
CONSTANT_OPENVPN_CLIENT = _('openvpn client')
CONSTANT_IPV4_CONFIG = _("IPv4 config")
CONSTANT_INTERFACE = _("interface")
CONSTANT_CA = _("Certificate Authority")
CONSTANT_CERTIF = _("Certificate")
CONSTANT_USED_ITEM = _("it's used in")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
SUCCESS_MESSAGES_STARTING = _("is started")
SUCCESS_MESSAGES_RESTARTING = _("is restarted")
SUCCESS_MESSAGES_STOPING = _("is stoped")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UPDATING = _("System error in updating")
ERROR_MESSAGES_STARTING = _("System error in starting")
ERROR_MESSAGES_RESTARTING = _("System error in restarting")
ERROR_MESSAGES_STOPING = _("System error in stoping")
ERROR_MESSAGES_DELETING_USED_ITEM = _("Unable to delete")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_DATA = _("Invalid data")


########################################
################ Server ################
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL OPENVPN SERVERS",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_server_openvpn(request):
    """Getting all servers from database"""
    list_server_openvpn = []
    if (request.method == 'GET'):
        list_server_openvpn = get_list_all_server_openvpn()
        return JsonResponse(list_server_openvpn, safe=False)
    

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO GET AN OPENVPN SERVER",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_server_openvpn(request, id):
    """Getting server by id from database"""
    if (request.method == 'GET'):
        server = get_one_server_openvpn(id)
        if server:
            return JsonResponse(server, safe=False)
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE AN OPENVPN SERVER",
    request_body=CONSTANT_BODY_OPENVPN_SERVER)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_server_openvpn(request):
    """Creating a new server in system and adding it to the database"""
    try:
        data = request.data

        # Check the payload validity
        if not check_validity_server(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        
        # Apply correction for ipv4 addresses
        data["ipv4_tunnel_network"], data["ipv4_local_network"], data["ipv4_remote_network"] = fix_ipv4_address(
            [data["ipv4_tunnel_network"], data["ipv4_local_network"], data["ipv4_remote_network"]])

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
    
        server_data = {
            "name": name,
            "description": description,
            "server_mode": server_mode,
            "proto": proto,
            "dev": dev,
            "interface": interface_name,
            "port": port,
            "ca_name": CertificateAuthority.objects.get(name=ca_name).pk,
            "cert_name": Certificate.objects.get(name=server_cert_name).pk,
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

            # Add the server to the list of services
            Services.objects.create(service_name=f"openvpn-server@server_{name}", description=f"Server OpenVPN {name}")

            return JsonResponse({"msg": f"{name} {SUCCESS_MESSAGES_CREATING}"}, status=201)
        
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)
    
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_OPENVPN_SERVER}"}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERTIF} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO DELETE AN OPENVPN SERVER",)
@api_view(['Delete'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_server_openvpn(_, id):
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

        # Remove the server from the list of services
        Services.objects.get(service_name=f"openvpn-server@server_{server.name}").delete()

        return JsonResponse({"msg": f"{server.name} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    except ProtectedError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING_USED_ITEM} {CONSTANT_OPENVPN_SERVER}, {CONSTANT_USED_ITEM} {CONSTANT_OPENVPN_CLIENT}"}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Services.DoesNotExist:
        return JsonResponse({"msg": f"{server.name} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_OPENVPN_SERVER}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    operation_summary="API TO CREATE AN OPENVPN SERVER",
    request_body=CONSTANT_BODY_OPENVPN_SERVER)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_server_openvpn(request, id):
    """Updating a server from system and database"""
    try:
        data = request.data

        # Check the payload validity
        if not check_validity_server(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        
        # Apply correction for ipv4 addresses
        data["ipv4_tunnel_network"], data["ipv4_local_network"], data["ipv4_remote_network"] = fix_ipv4_address(
            [data["ipv4_tunnel_network"], data["ipv4_local_network"], data["ipv4_remote_network"]])

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
        ca_name = data.get('ca_name', '')
        cert_name = data.get('server_cert', '')
        server.ca_name = CertificateAuthority.objects.get(name=ca_name).pk
        server.cert_name = Certificate.objects.get(name=cert_name).pk
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
        if client_management.get('client_management_select') and client_management.get('password'):
            server.client_management_port = client_management.get('port')
            if server.client_management_password and not check_password(client_management.get('password'), server.client_management_password):
                return JsonResponse({"error": "error previous password"}, status=400)
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

            # Update the server in the list of services
            service = Services.objects.get(service_name=f"openvpn-server@server_{previous_name}")
            service.service_name = f"openvpn-server@server_{server.name}"
            service.description = f"Server OpenVPN with name {server.name}"
            service.save()

            return JsonResponse({"msg": f"{server.name} {SUCCESS_MESSAGES_UPDATING}"}, status=201)
        
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERTIF} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Services.DoesNotExist:
        # Add the server to the list of services
        Services.objects.create(service_name=f"openvpn-server@server_{server.name}", description=f"Server OpenVPN with name {server.name}")
        return JsonResponse({"msg": f"{server.name} {SUCCESS_MESSAGES_UPDATING}"}, status=201)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_OPENVPN_SERVER}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO Start AN OPENVPN SERVER",)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_server_openvpn(_, id):
    """Starting a server and opening a tunnel"""
    try:
        server = ServerOpenvpn.objects.get(id=id)
        change_status_server_openvpn(server_name=server.name, server_status='start')
        time.sleep(3)
        return JsonResponse({"msg": f"{server.name} {SUCCESS_MESSAGES_STARTING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_OPENVPN_SERVER}"}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO Restart AN OPENVPN SERVER",)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def restart_server_openvpn(_, id):
    """Retarting a server and reopening a tunnel"""
    try:
        server = ServerOpenvpn.objects.get(id=id)
        change_status_server_openvpn(server_name=server.name, server_status='restart')
        time.sleep(3)
        return JsonResponse({"msg": f"{server.name} {SUCCESS_MESSAGES_RESTARTING}"}, status=201)
    
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_RESTARTING} {CONSTANT_OPENVPN_SERVER}"}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO STOP AN OPENVPN SERVER",)
@api_view(['DELETE'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_server_openvpn(_, id):
    """Stoping a server and closing a tunnel"""
    try:
        server = ServerOpenvpn.objects.get(id=id)
        change_status_server_openvpn(server_name=server.name, server_status='stop')
        time.sleep(3)
        return JsonResponse({"msg": f"{server.name} {SUCCESS_MESSAGES_STOPING}"}, status=201)
    
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_OPENVPN_SERVER}"}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
