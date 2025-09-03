from django.contrib.auth.hashers import check_password, make_password
from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.network.models import IP4Config, Interface
from backend.openvpn.client_openvpn import delete_client_openvpn_in_system, export_client_in_system, install_client_openvpn_in_system, update_client_openvpn_in_system
from backend.openvpn.constant_variables import CONSTANT_BODY_OPENVPN_CLIENT, PATH_SERVER_STATIC
from backend.openvpn.list_servers_clients import get_list_all_client_openvpn, get_one_client_openvpn
from backend.openvpn.models import ClientOpenvpn, ServerOpenvpn
from backend.openvpn.serializers import ClientOpenvpnSerializer
from backend.openvpn.utils import check_validity_client, json_to_str_client
from utils.commands_utils import read_file_from_system
from utils.errors_utils import CommandExecutionError

from decouple import config
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from drf_yasg.openapi import IN_PATH, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Parameter, Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utils.utils_address import fix_ipv4_address


# Constants
CONSTANT_OPENVPN_SERVER = _('openvpn server')
CONSTANT_OPENVPN_CLIENT = _('openvpn client')
CONSTANT_IPV4_CONFIG = _("IPv4 config")
CONSTANT_INTERFACE = _("interface")
CONSTANT_CA = _("Certificate Authority")
CONSTANT_CERTIF = _("Certificate")
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
ERROR_MESSAGES_EXPORTING = _("System error in exporting")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_DATA = _("Invalid data")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL OPENVPN CLIENTS",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_client_openvpn(request):
    """Getting all clients from database"""
    if (request.method == 'GET'):
        list_client_openvpn = get_list_all_client_openvpn()
        return JsonResponse(list_client_openvpn, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO GET AN OPENVPN CLIENT",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_client_openvpn(request, id):
    """Getting client by id from database"""
    if (request.method == 'GET'):
        client = get_one_client_openvpn(id)
        if client:
            return JsonResponse(client, safe=False)
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_CLIENT} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN OPENVPN Client",
    request_body=CONSTANT_BODY_OPENVPN_CLIENT)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_client_openvpn(request):
    """Creating a new client in system and adding it to the database"""
    try:
        # parse the incoming information
        data = request.data

        # Check the payload validity
        if not check_validity_client(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        
        # Apply correction for ipv4 addresses
        data["ipv4_tunnel_network"], data["ipv4_remote_network"] = fix_ipv4_address(
            [data["ipv4_tunnel_network"], data["ipv4_remote_network"]])

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

        client_data = {
            "name": name,
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
            "ca_name": CertificateAuthority.objects.get(name=ca_name).pk,
            "cert_name": Certificate.objects.get(name=cert_name).pk,
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
            return JsonResponse({"msg": f"{data['name']} {SUCCESS_MESSAGES_CREATING}"}, status=201)
        return JsonResponse({"error": list(client_serializer.errors.values())[0][0]}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_OPENVPN_CLIENT}"}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERTIF} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'},
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO DELETE AN OPENVPN CLIENT",)
@api_view(['Delete'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_client_openvpn(_, id):
    """Deleting a client from system and then from database"""
    try:

        client = ClientOpenvpn.objects.get(id=id)

        # Delete the client from system
        delete_client_openvpn_in_system(client.name)

        # Delete the client from database
        client.delete()
        return JsonResponse({"msg": f"{client.name} {SUCCESS_MESSAGES_DELETING}"}, status=201)

    except ClientOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_CLIENT} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_OPENVPN_CLIENT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'},
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    operation_summary="API TO CREATE AN OPENVPN Client",
    request_body=CONSTANT_BODY_OPENVPN_CLIENT)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_client_openvpn(request, id):
    """Updating a client from system and database"""
    try:
        data = request.data

        # Check the payload validity
        if not check_validity_client(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        
        # Apply correction for ipv4 addresses
        data["ipv4_tunnel_network"], data["ipv4_remote_network"] = fix_ipv4_address(
            [data["ipv4_tunnel_network"], data["ipv4_remote_network"]])

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
        ca_name = data.get('ca_name', '')
        cert_name = data.get('client_cert', '')
        client.ca_name = CertificateAuthority.objects.get(name=ca_name).pk
        client.cert_name = Certificate.objects.get(name=cert_name).pk
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
            return JsonResponse({"msg": f"{client.name} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

        return JsonResponse({"error": list(client_serializer.errors.values())[0][0]}, status=400)

    except ClientOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_CLIENT} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERTIF} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_OPENVPN_CLIENT}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'},
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO EXPORT A CLIENT OPENVPN FROM A SERVER",)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def export_client_openvpn(_, id):
    """Exporting a Client openvpn"""
    try:
        client = ClientOpenvpn.objects.get(id=id)
        config_input = read_file_from_system(f'/etc/openvpn/client/client_{client.name}.ovpn')
        list_balise_client = ['ca', 'cert', 'key', 'crl-verify', 'tls-auth']
        config_input = export_client_in_system(list_balise_client, config_input)

        return JsonResponse({"client": config_input}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_EXPORTING} {CONSTANT_OPENVPN_CLIENT}"}, status=400)
    except ClientOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_CLIENT} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    operation_summary="API TO GENERATE AN OPENVPN Client FROM A SERVER",
    request_body=Schema(type=TYPE_OBJECT, required=['name', 'client_cert'],
                        properties={
                            'name': Schema(type=TYPE_STRING, example="gen_client1"),
                            'client_cert': Schema(type=TYPE_STRING, example="cert_client", description="Certificate name from Certificates list with type client"),
                            'interface_address': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Set an interface address for the client to connect to it if the server is configured on interface Any")}
                                                             ))
@api_view(['POST'])
@require_http_methods(['POST'])
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
        tls_key = read_file_from_system(PATH_SERVER_STATIC.format(server.name))
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
            return JsonResponse({"msg": f"{data['name']} {SUCCESS_MESSAGES_CREATING}"}, status=201)
        else:
            return JsonResponse({"error": list(client_serializer.errors.values())[0][0]}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_OPENVPN_CLIENT}"}, status=400)
    except ServerOpenvpn.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_OPENVPN_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
