import time
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import IN_PATH, Parameter, Schema, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING

from backend.ipsec.utils import check_payload_change_status, check_payload_create_tunnel, json_to_str_server_ipsec, up_ipsec_conn
from backend.ipsec.list_ipsec import get_list_all_server_ipsec, get_one_server_ipsec, get_status_ipsec
from backend.ipsec.serializers import ServerIPsecSerializer
from backend.ipsec.server_ipsec import disable_conn, enable_conn, change_status_ipsec_in_system, delete_server_ipsec_in_system, install_server_ipsec_in_system, update_server_ipsec_in_system
from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.managementKeypairs.models import PublicKey
from backend.network.models import IP4Config, Interface
from backend.ipsec.constant_variables import CONSTANT_METHOD_PSK, CONSTANT_METHOD_PUBLIC_KEY, CONSTANT_REQUEST_BODY_IPSEC
from utils.errors_utils import CommandExecutionError
from .models import ServerIPsec
from django.views.decorators.http import require_http_methods


# Constants
CONSTANT_IPSEC_SERVICE = _("IPsec Service")
CONSTANT_IPSEC_CONFIGURATION = _("IPsec configuration")
CONSTANT_IPV4_CONFIG = _("IPv4 config")
CONSTANT_INTERFACE = _("interface")
CONSTANT_CA = _("Certificate Authority")
CONSTANT_CERT = _("Certificate")
CONSTANT_PUBLIC_KEY = _("Public Key")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
SUCCESS_MESSAGES_ENABLED = _("is enabled")
SUCCESS_MESSAGES_DISABLED = _("is disabled")
SUCCESS_MESSAGES_START = _("is started")
SUCCESS_MESSAGES_STOP = _("is stoped")
SUCCESS_MESSAGES_UP = _("is up")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UP_CONFIG = _("System error in up ipsec")
ERROR_MESSAGES_CHANGE_STATUS = _("System error in changing status of")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_DATA = _("Invalid data")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET IPSEC STATUS",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_ipsec_status(request):
    """Getting IPsec status from system. This API return the status of IPsec in boolean field: 
    True means IPsec is started and False means IPsec is stoped"""
    if (request.method == 'GET'):
        ipsec_status = get_status_ipsec()
        return JsonResponse(ipsec_status, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL IPSEC",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_server_ipsec(request):
    """Getting all IPsec server from database"""
    if (request.method == 'GET'):
        list_ipsec = get_list_all_server_ipsec()
        return JsonResponse(list_ipsec, safe=False)
    

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO GET AN IPSEC",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_server_ipsec(request, id):
    """Getting server by id from database"""
    if (request.method == 'GET'):
        server_ipsec = get_one_server_ipsec(id)
        if server_ipsec:
            return JsonResponse(server_ipsec, safe=False)
        return JsonResponse({"error": f"{CONSTANT_IPSEC_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema(
        'POST', responses={201: 'Created', 400: 'Bad Request'}, 
        operation_summary="API TO CREATE AN IPSEC",
        request_body=Schema(type=TYPE_OBJECT, required=['conn_name', 'connection_method', 'key_exchange', 'internet_protocol', 'interface_name', 'remote_gateway', 'dynamic_gateway', 'authentication', 'encryption_algorithm_ph1', 'hash_algorithm_ph1', 'dh_key_group', 'policy', 'rekey', 'reauth', 'nat_traversal', 'mobike', 'deed_peer', 'mode_ph2', 'local_network', 'remote_network', 'sa_key_exchange'],
        properties=CONSTANT_REQUEST_BODY_IPSEC))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_server_ipsec(request):
    """Creating a new server in system and adding it to the database"""
    try:
        data = request.data

        # Check data validity
        if not check_payload_create_tunnel(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)

        conn_name = data.get("conn_name", "")
        connection_method = data.get("connection_method", "")
        key_exchange = data.get("key_exchange", "")
        key_exchange_version = key_exchange.get("key_exchange_version", "")
        internet_protocol = data.get("internet_protocol", "")
        interface_name = data.get("interface_name", "")
        remote_gateway = data.get("remote_gateway", "")
        dynamic_gateway = data.get("dynamic_gateway", "")
        description_ph1 = data.get("description_ph1", "")

        authentication = data.get("authentication", "")
        authentication_method = authentication.get("authentication_method", "")

        encryption_algorithm_ph1 = data.get("encryption_algorithm_ph1", "")
        hash_algorithm_ph1_list = data.get("hash_algorithm_ph1", "")
        hash_algorithm_ph1 = ",".join(hash_algorithm_ph1_list)
        dh_key_group_list = data.get("dh_key_group", "")
        dh_key_group = ",".join(dh_key_group_list)
        lifetime_ph1 = data.get("lifetime_ph1", "")

        policy = data.get("policy", "")
        rekey = data.get("rekey", "")
        reauth = data.get("reauth", "")
        nat_traversal = data.get("nat_traversal", "")
        mobike = data.get("mobike", "")

        deed_peer = data.get("deed_peer", "")
        deed_peer_detection = deed_peer.get("disable", "")

        inactivity_timeout = data.get("inactivity_timeout", "")
        margin_time = data.get("margin_time", "")
        rekey_fuzz = data.get("rekey_fuzz", "")

        mode_ph2 = data.get("mode_ph2", "")
        mode = mode_ph2.get("mode", "")

        description_ph2 = data.get("description_ph2", "")

        sa_key_exchange = data.get("sa_key_exchange", "")
        protocol = sa_key_exchange.get("protocol", "")
        hash_algorithm_ph2_list = sa_key_exchange.get("hash_algorithm_ph2", "")
        hash_algorithm_ph2 = ",".join(hash_algorithm_ph2_list)
        pfs_key_group = sa_key_exchange.get("pfs_key_group", "")
        lifetime_ph2 = data.get("lifetime_ph2", "")

        interface = 'Any'
        if interface_name != 'Any':
            interface = Interface.objects.get(name_interface=interface_name)
            interface = interface.pk
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = f'{interface_address.ip_address}'

        server_data = {"conn_name": conn_name,
                        "connection_method": connection_method,
                        "key_exchange_version": key_exchange_version,
                        "internet_protocol": internet_protocol,
                        "interface": interface_name,
                        "remote_gateway": remote_gateway,
                        "dynamic_gateway": dynamic_gateway,
                        "description_ph1": description_ph1,

                        "authentication_method": authentication_method,
                        
                        "encryption_algorithm_ph1": encryption_algorithm_ph1,
                        "hash_algorithm_ph1": hash_algorithm_ph1,
                        "dh_key_group": dh_key_group,
                        "lifetime_ph1": lifetime_ph1,
                        
                        "policy": policy,
                        "rekey": rekey,
                        "reauth": reauth,
                        "nat_traversal": nat_traversal,
                        "mobike": mobike,
                        "deed_peer_detection": deed_peer_detection,
                        "inactivity_timeout": inactivity_timeout,
                        "margin_time": margin_time,
                        "rekey_fuzz": rekey_fuzz,
                        
                        "mode": mode,
                        "description_ph2": description_ph2,
                        
                        "protocol": protocol,
                        "hash_algorithm_ph2": hash_algorithm_ph2,
                        "pfs_key_group": pfs_key_group,
                        "lifetime_ph2": lifetime_ph2,
                        }
        
        if key_exchange_version == "V1":
            negotiation_mode = key_exchange.get("negotiation_mode", "")
            server_data["negotiation_mode"] = negotiation_mode

        ca = ''
        if authentication_method == CONSTANT_METHOD_PSK:
            pre_shared_key = authentication.get("pre_shared_key", "")
            server_data["pre_shared_key"] = pre_shared_key
        elif authentication_method == CONSTANT_METHOD_PUBLIC_KEY:
            local_key_pair = authentication.get("local_key_pair", "")
            peer_key_pair = authentication.get("peer_key_pair", "")
            server_data["local_key_pair"] = local_key_pair
            server_data["peer_key_pair"] = peer_key_pair
        else:
            cert = authentication.get("cert")
            certificate = Certificate.objects.get(name=cert)
            remote_cert = authentication.get("remote_cert", "")
            server_data["cert"] = cert
            server_data["remote_cert"] = remote_cert

            # if the certificate dosen't have a CA (imported cert) ca will be null
            ca = certificate.certificate_authority
            if ca:
                ca = CertificateAuthority.objects.get(id=ca.pk).name
            
        if deed_peer_detection:
            deed_peer_delay = deed_peer.get("deed_peer_delay", "")
            deed_peer_timeout = deed_peer.get("deed_peer_timeout", "")
            deed_peer_action = deed_peer.get("deed_peer_action")
            server_data["deed_peer_delay"] = deed_peer_delay
            server_data["deed_peer_timeout"] = deed_peer_timeout
            server_data["deed_peer_action"] = deed_peer_action
        
        if mode == "Tunnel IPv4":
            # Local Network
            local_network = mode_ph2.get("local_network", "")
            type_local_network = local_network.get("type_local_network", "")
            if type_local_network == "Address":
                address_local_network = local_network.get("address_local_network", "")
            elif type_local_network == "Network":
                address_local_network = f'{local_network.get("address_local_network", "")}/{local_network.get("mask", "")}'
            else:
                interface_local = Interface.objects.get(name_interface=type_local_network).pk
                address_local_network = IP4Config.objects.get(interface_id=interface_local).ip_address
            server_data["type_local_network"] = type_local_network
            server_data["address_local_network"] = address_local_network
            data["address_local_network"] = address_local_network

            # Remote Network
            remote_network = mode_ph2.get("remote_network", "")
            type_remote_network = remote_network.get("type_remote_network", "")
            address_remote_network = remote_network.get("address_remote_network", "")
            if type_remote_network == "Network":
                address_remote_network += f'/{remote_network.get("mask", "")}'
            server_data["type_remote_network"] = type_remote_network
            server_data["address_remote_network"] = address_remote_network
            data["address_remote_network"] = address_remote_network

        if protocol == "ESP":
            encryption_algorithm_ph2_list = sa_key_exchange.get("encryption_algorithm_ph2", "")
            encryption_algorithm_ph2 = ",".join(encryption_algorithm_ph2_list)
            server_data["encryption_algorithm_ph2"] = encryption_algorithm_ph2

        serializer_server = ServerIPsecSerializer(data=server_data)
        if serializer_server.is_valid():
        
            # Update the server config
            server_conf = json_to_str_server_ipsec(data)

            # Install the server configuration in system
            interface_ip_address = "any"
            if interface_name != 'Any':
                interface_ip_address = interface_address.ip_address
            postrouting_rule_content, postrouting_rule_handle = install_server_ipsec_in_system(server_conf, authentication, interface_ip_address, remote_gateway, address_remote_network)
            time.sleep(3)

            # Add the postrouting rule data to the serializer
            server_data["postrouting_rule_content"] = postrouting_rule_content
            server_data["postrouting_rule_handle"] = postrouting_rule_handle
            serializer_server = ServerIPsecSerializer(data=server_data)
            if serializer_server.is_valid():

                # Add the server to the database
                serializer_server.save()
                return JsonResponse({"msg": f"{conn_name} {SUCCESS_MESSAGES_CREATING}"}, status=201)
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_IPSEC_CONFIGURATION}"}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CertificateAuthority.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CA} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERT} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except PublicKey.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_PUBLIC_KEY} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO DELETE AN IPSEC",)
@api_view(['DELETE'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_server_ipsec(_, id):
    """Deleting a server from system and then from database"""
    try:
        server = ServerIPsec.objects.get(id=id)
        
        delete_server_ipsec_in_system(server)
        # delete from database
        server.delete()
        return JsonResponse({"msg": f"{server.conn_name} {SUCCESS_MESSAGES_DELETING}"}, status=201)
    except ServerIPsec.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPSEC_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_IPSEC_CONFIGURATION}"}, status=400)


@swagger_auto_schema(
        'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
        manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
        operation_summary="API TO UPDATE AN IPSEC",
        request_body=Schema(type=TYPE_OBJECT, required=['conn_name', 'connection_method', 'key_exchange', 'internet_protocol', 'interface_name', 'remote_gateway', 'dynamic_gateway', 'authentication', 'encryption_algorithm_ph1', 'hash_algorithm_ph1', 'dh_key_group', 'policy', 'rekey', 'reauth', 'nat_traversal', 'mobike', 'deed_peer', 'mode_ph2', 'local_network', 'remote_network', 'sa_key_exchange'],
        properties=CONSTANT_REQUEST_BODY_IPSEC))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_server_ipsec(request, id):
    """Updating a server from system and database"""
    try:
        # parse the incoming information
        data = request.data

        # Check data validity
        if not check_payload_create_tunnel(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        
        previous_server = ServerIPsec.objects.get(id=id)
        server = ServerIPsec.objects.get(id=id)
        
        server.conn_name = data.get("conn_name", "")
        server.connection_method = data.get("connection_method", "")
        key_exchange = data.get("key_exchange", "")
        server.key_exchange_version = key_exchange.get("key_exchange_version", "")
        server.internet_protocol = data.get("internet_protocol", "")
        server.interface = data.get("interface_name", "")
        server.remote_gateway = data.get("remote_gateway", "")
        server.dynamic_gateway = data.get("dynamic_gateway", "")
        server.description_ph1 = data.get("description_ph1", "")

        authentication = data.get("authentication", "")
        server.authentication_method = authentication.get("authentication_method", "")

        server.encryption_algorithm_ph1 = data.get("encryption_algorithm_ph1", "")
        
        hash_algorithm_ph1_list = data.get("hash_algorithm_ph1", "")
        server.hash_algorithm_ph1 = ",".join(hash_algorithm_ph1_list)
        dh_key_group_list = data.get("dh_key_group", "")
        server.dh_key_group = ",".join(dh_key_group_list)
        server.lifetime_ph1 = data.get("lifetime_ph1", "")

        server.policy = data.get("policy", "")
        server.rekey = data.get("rekey", "")
        server.reauth = data.get("reauth", "")
        server.nat_traversal = data.get("nat_traversal", "")
        server.mobike = data.get("mobike", "")

        deed_peer = data.get("deed_peer", "")
        server.deed_peer_detection = deed_peer.get("disable", "")

        server.inactivity_timeout = data.get("inactivity_timeout", "")
        server.margin_time = data.get("margin_time", "")
        server.rekey_fuzz = data.get("rekey_fuzz", "")

        mode_ph2 = data.get("mode_ph2", "")
        server.mode = mode_ph2.get("mode", "")
        server.description_ph2 = data.get("description_ph2", "")

        sa_key_exchange = data.get("sa_key_exchange", "")
        server.protocol = sa_key_exchange.get("protocol", "")
        hash_algorithm_ph2_list = sa_key_exchange.get("hash_algorithm_ph2", "")
        server.hash_algorithm_ph2 = ",".join(hash_algorithm_ph2_list)
        server.pfs_key_group = sa_key_exchange.get("pfs_key_group", "")
        server.lifetime_ph2 = data.get("lifetime_ph2", "")

        if server.interface != "Any":
            interface = Interface.objects.get(name_interface=server.interface)
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = interface_address.ip_address

        server.negotiation_mode = None
        if server.key_exchange_version == "V1":
            server.negotiation_mode = key_exchange.get("negotiation_mode", "")
            

        ca = ''
        server.pre_shared_key = None
        server.local_key_pair = None
        server.peer_key_pair = None
        server.cert = None
        server.remote_cert = None
        if server.authentication_method == CONSTANT_METHOD_PSK:
            server.pre_shared_key = authentication.get("pre_shared_key", "")
        elif server.authentication_method == CONSTANT_METHOD_PUBLIC_KEY:
            server.local_key_pair = authentication.get("local_key_pair", "")
            server.peer_key_pair = authentication.get("peer_key_pair")
        else:
            server.cert = authentication.get("cert")
            certificate = Certificate.objects.get(name=server.cert)
            ca = certificate.certificate_authority
            if ca:
                ca = ca.name
            server.remote_cert = authentication.get("remote_cert", "")
        
        server.deed_peer_delay = None
        server.deed_peer_timeout = None
        server.deed_peer_action = None
        if server.deed_peer_detection:
            server.deed_peer_delay = deed_peer.get("deed_peer_delay", "")
            server.deed_peer_timeout = deed_peer.get("deed_peer_timeout", "")
            server.deed_peer_action = deed_peer.get("deed_peer_action")

        if server.mode == "Tunnel IPv4":
            # Local Network
            local_network = mode_ph2.get("local_network", "")
            server.type_local_network = local_network.get("type_local_network", "")
            if server.type_local_network == "Address":
                server.address_local_network = local_network.get("address_local_network", "")
            elif server.type_local_network == "Network":
                server.address_local_network = f'{local_network.get("address_local_network", "")}/{local_network.get("mask", "")}'
            else:
                interface_local = Interface.objects.get(name_interface=server.type_local_network).pk
                server.address_local_network = IP4Config.objects.get(interface_id=interface_local).ip_address
            data["address_local_network"] = server.address_local_network

            # Remote Network
            remote_network = mode_ph2.get("remote_network", "")
            server.type_remote_network = remote_network.get("type_remote_network", "")
            server.address_remote_network = remote_network.get("address_remote_network", "")
            if server.type_remote_network == "Network":
                server.address_remote_network += f'/{remote_network.get("mask", "")}'
            data["address_remote_network"] = server.address_remote_network

        elif server.mode == "Route-based":
            server.local_address = mode_ph2.get("local_address", "")
            server.remote_address = mode_ph2.get("remote_address", "")

        server.encryption_algorithm_ph2 = None
        if server.protocol == "ESP":
            encryption_algorithm_ph2_list = sa_key_exchange.get("encryption_algorithm_ph2", "")
            server.encryption_algorithm_ph2 = ",".join(encryption_algorithm_ph2_list)
            data["encryption_algorithm_ph2"] = server.encryption_algorithm_ph2
        data_serializer = data.copy()
        serializer_server = ServerIPsecSerializer(server, data=data_serializer)
        data_serializer["hash_algorithm_ph1"] = server.hash_algorithm_ph1
        data_serializer["dh_key_group"] = server.dh_key_group
        if serializer_server.is_valid():

            # Update the server config and secrets
            server_conf = json_to_str_server_ipsec(data)
            
            # Install the server in system
            postrouting_rule_content, postrouting_rule_handle = update_server_ipsec_in_system(previous_server, server, server_conf)
            time.sleep(3)

            # Add the postrouting rule data to the serializer
            data_serializer["postrouting_rule_content"] = postrouting_rule_content
            data_serializer["postrouting_rule_handle"] = postrouting_rule_handle
            serializer_server = ServerIPsecSerializer(server, data=data_serializer)
            if serializer_server.is_valid():

                # Add the server to the database
                serializer_server.save()
                return JsonResponse({"msg": f"{server.conn_name} {SUCCESS_MESSAGES_UPDATING}"}, status=201)
        
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)

    except ServerIPsec.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPSEC_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO UP A CONN IPSEC",)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def up_server_ipsec(_, id):
    """Up a conn IPsec from system"""
    server = ServerIPsec.objects.get(id=id)
    up_ipsec_status = up_ipsec_conn(server.conn_name)
    if up_ipsec_status:
        return JsonResponse({"msg": f"{server.conn_name} {SUCCESS_MESSAGES_UP}"}, status=201)
    return JsonResponse({"error": ERROR_MESSAGES_UP_CONFIG}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO ENABLE OR DISABLE AN IPSEC CONFIGURATION",
                     request_body=Schema(
                         type=TYPE_OBJECT, required=['enable'], properties={
                             'enable': Schema(type=TYPE_BOOLEAN)}))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def status_server_ipsec(request, id):
    """Change status (enable or diable) of a server config from system and then from database"""
    try:
        data = request.data
        enable = data.get("enable", "")
        server = ServerIPsec.objects.get(id=id)

        # Enable IPsec tunnel
        if enable:
            # Check if the IPsec tunnel is enactive
            if not server.server_status:
                rule_content, handle_number = enable_conn(server)
                server.postrouting_rule_content = rule_content
                server.postrouting_rule_handle = handle_number
                server.server_status = enable
                server.save()
            return JsonResponse({"msg": f"{server.conn_name} {SUCCESS_MESSAGES_ENABLED}"})
        
        # Disable IPsec tunnel
        # Check if the IPsec tunnel is active
        if server.server_status:
            disable_conn(server)
            server.postrouting_rule_content = None
            server.postrouting_rule_handle = None
            server.server_status = enable
            server.save()
        return JsonResponse({"msg": f"{server.conn_name} {SUCCESS_MESSAGES_DISABLED}"})
        
    except ServerIPsec.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPSEC_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CHANGE_STATUS} {CONSTANT_IPSEC_CONFIGURATION}"}, status=400)


@swagger_auto_schema(
        'POST', responses={200: 'Created', 400: 'Bad Request'},
        operation_summary="API TO STOP OR START IPSEC",
        request_body=Schema(
            type=TYPE_OBJECT, required=['status'],
            properties={'status': Schema(type=TYPE_STRING, enum=['start', 'stop'])}))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def status_ipsec(request):
    """Change status of a server config from system and then from database"""
    try:
        data = request.data
        
        # Check data validity
        if not check_payload_change_status(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)

        status = data.get("status", "")

        change_status_ipsec_in_system(status)
        
        if status == "start":
            return JsonResponse({"msg": f"{CONSTANT_IPSEC_SERVICE} {SUCCESS_MESSAGES_START}"}, status=200)
        return JsonResponse({"msg": f"{CONSTANT_IPSEC_SERVICE} {SUCCESS_MESSAGES_STOP}"}, status=200)
        
    except ServerIPsec.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPSEC_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IPV4_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
