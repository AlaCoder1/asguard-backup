import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from backend.ipsec.functions import json_to_str_server_ipsec
from backend.ipsec.list_ipsec import get_all_server_ipsec, get_server_ipsec
from backend.ipsec.serializers import ServerIPsecSerializer
from backend.ipsec.server_ipsec import delete_server_ipsec, install_server_ipsec, update_server_ipsec
from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.network.models import IP4Config, Interface
from backend.openvpn.manage_errors import CommandExecutionError

from .models import ServerIPsec


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL IPSEC",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllServerIPsec(request):
    if (request.method == 'GET'):
        list_ipsec = get_all_server_ipsec()
        return JsonResponse(list_ipsec, safe=False)
    

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN IPSEC",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getServerIPsec(request, id):
    """Getting server by id from database"""
    if (request.method == 'GET'):
        server_ipsec = get_server_ipsec(id)
        return JsonResponse(server_ipsec, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE AN IPSEC",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, 
                                                 required=['conn_name', 'connection_method', 'key_exchange', 'internet_protocol', 'interface_name', 'remote_gateway', 'dynamic_gateway', 'authentication', 'my_identifier', 'encryption_algorithm_ph1', 'hash_algorithm_ph1', 'dh_key_group', 'policy', 'rekey', 'reauth', 'tunnel', 'nat_traversal', 'mobike', 'deed_peer', 'mode_ph2', 'local_network', 'remote_network', 'sa_key_exchange'],
                                                 properties={'conn_name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'connection_method': openapi.Schema(type=openapi.TYPE_STRING, enum=["default", "Respond Only", "Start on traffic", "Start immediate"]),
                                                             'key_exchange': openapi.Schema(type=openapi.TYPE_OBJECT, required=['key_exchange_version'], 
                                                                                            properties={'key_exchange_version': openapi.Schema(type=openapi.TYPE_STRING, default="auto", enum=["auto", "V1", "V2"]),
                                                                                                        'negotiation_mode': openapi.Schema(type=openapi.TYPE_STRING, description="When Key version is V1", enum=["Main", "Aggressive"])}),
                                                             'internet_protocol': openapi.Schema(type=openapi.TYPE_STRING, enum=["IPv4", "IPv6"]),
                                                             'interface_name': openapi.Schema(type=openapi.TYPE_STRING, description="Interface name like LAN or WAN or any"),
                                                             'remote_gateway': openapi.Schema(type=openapi.TYPE_STRING, description="Remote address like 10.1.12.22"),
                                                             'dynamic_gateway': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'description_ph1': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'authentication': openapi.Schema(type=openapi.TYPE_OBJECT, required=['authentication'], 
                                                                                              properties={'authentication': openapi.Schema(type=openapi.TYPE_STRING, default="Mutual PSK", enum=["Mutual PSK", "Mutual Public Key", "Mutual RSA"]),
                                                                                                          'pre_shared_key': openapi.Schema(type=openapi.TYPE_STRING, description="required when authentication_method is Mutual PSK"),
                                                                                                          'local_key_pair': openapi.Schema(type=openapi.TYPE_STRING, description="required when authentication_method is Mutual Public Key"),
                                                                                                          'peer_key_pair': openapi.Schema(type=openapi.TYPE_STRING, description="required when authentication_method is Mutual Public Key"),
                                                                                                          'cert': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate name from list of certificates, required when authentication_method is Mutual RSA"),
                                                                                                          'remote_distingushed_name': openapi.Schema(type=openapi.TYPE_STRING, description="all distingushed name of the remote server, required when authentication_method is Mutual RSA. Example:C=CH, ST=IPsec, L=Tunis, O=strongSwan, OU=My Organizational Unit, CN=device1, E=bak.akram94@gmail.com")}),
                                                             'my_identifier': openapi.Schema(type=openapi.TYPE_STRING, enum=["My IP address", "IP address", "Distinguished name", "User distinguished name", "ASN.1 distinguished name", "KeyID tag", "Dynamic DN"]),
                                                             'peer_identifier': openapi.Schema(type=openapi.TYPE_STRING, enum=["Peer IP address", "IP address", "Distinguished name", "User distinguished name", "ASN.1 distinguished name", "KeyID tag"]),
                                                             'encryption_algorithm_ph1': openapi.Schema(type=openapi.TYPE_STRING, enum=["128", "192", "256"]),
                                                             'hash_algorithm_ph1': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like sha256 and the list of hash_algorithm must sepeate with comma. Example: sha256,sha512"),
                                                             'dh_key_group': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like group:key like 15:3072 and the list of key_group must sepeate with comma. Example: 15:3072,20:384"),
                                                             'lifetime_ph1': openapi.Schema(type=openapi.TYPE_STRING, description="set lifetime with its unit like 1h or 3600s", pattern=r"(\d+)([hms])"),
                                                             'policy': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                                                             'rekey': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'reauth': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'tunnel': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'nat_traversal': openapi.Schema(type=openapi.TYPE_STRING, default="auto", enum=["Disable", "E,able", "Force"]),
                                                             'mobike': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'deed_peer': openapi.Schema(type=openapi.TYPE_OBJECT, description="Deed Peer block", required=['disable'], 
                                                                                         properties={'disable': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                     'deed_peer_delay': openapi.Schema(type=openapi.TYPE_STRING, pattern=r"(\d+)([hms])", description="set deed peer delay with its unit like 10s, required when selecting deed peer"),
                                                                                                     'deed_peer_timeout': openapi.Schema(type=openapi.TYPE_STRING, pattern=r"(\d+)([hms])", description="set deed peer timeout with its unit like 160s, required when selecting deed peer"),
                                                                                                     'deed_peer_action': openapi.Schema(type=openapi.TYPE_STRING, enum=["default", "Restart the tunnel", "Stop the tunnel"], default="default", description="set deed peer action, required when selecting deed peer")}),
                                                             'inactivity_timeout': openapi.Schema(type=openapi.TYPE_STRING, description="set inactivity timeout with its unit like 10s", pattern=r"(\d+)([hms])"),
                                                             'margin_time': openapi.Schema(type=openapi.TYPE_STRING, description="set margin time with its unit like 10s", pattern=r"(\d+)([hms])"),
                                                             'rekey_fuzz': openapi.Schema(type=openapi.TYPE_STRING, description="set rekey_fuzz with % (percentage symbol) like 10%", pattern=r"(\d+)%"),
                                                             'mode_ph2': openapi.Schema(type=openapi.TYPE_OBJECT, description="General information of phase 2", required=['mode'], 
                                                                                        properties={'mode': openapi.Schema(type=openapi.TYPE_STRING, default="Tunnel IPv4", enum=["Tunnel IPv4", "Tunnel IPv6", "Route-based", "Transport"]),
                                                                                                    'local_address': openapi.Schema(type=openapi.TYPE_STRING, description="Local Address, required when selecting Route-based"),
                                                                                                    'remote_address': openapi.Schema(type=openapi.TYPE_STRING, description="Remote Address, required when selecting Route-based"),}),
                                                             'description_ph2': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'local_network': openapi.Schema(type=openapi.TYPE_OBJECT, description="Local network block", required=['type_local_network'], 
                                                                                             properties={'type_local_network': openapi.Schema(type=openapi.TYPE_STRING, default="Address", enum=["Address", "Network", "WAN subnet", "LAN subnet"]),
                                                                                                         'address_local_network': openapi.Schema(type=openapi.TYPE_STRING, description="Address of local network like 10.1.12.0, required when selecting Address or Network"),
                                                                                                         'mask': openapi.Schema(type=openapi.TYPE_STRING, description="Address mask like 24, required when selecting Network"),}),
                                                             'remote_network': openapi.Schema(type=openapi.TYPE_OBJECT, description="Remote network block", required=['type_remote_network', 'address_remote_network'], 
                                                                                              properties={'type_remote_network': openapi.Schema(type=openapi.TYPE_STRING, default="Address", enum=["Address", "Network"]),
                                                                                                          'address_remote_network': openapi.Schema(type=openapi.TYPE_STRING, description="Address of remote network like 51.68.170.149"),
                                                                                                          'mask': openapi.Schema(type=openapi.TYPE_STRING, description="Address mask like 24, required when selecting Network"),}),
                                                             'sa_key_exchange': openapi.Schema(type=openapi.TYPE_OBJECT, description="Key Exchange block", required=['protocol', 'hash_algorithm_ph2', 'pfs_key_group'], 
                                                                                               properties={'protocol': openapi.Schema(type=openapi.TYPE_STRING, default="ESP", enum=["ESP", "AH"]),
                                                                                                           'encryption_algorithm_ph2': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like 256 and the list of hash_algorithm must sepeate with comma. Example: 128,256"),
                                                                                                           'hash_algorithm_ph2': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like sha256 and the list of hash_algorithm must sepeate with comma. Example: sha256,sha384"),
                                                                                                           'pfs_key_group': openapi.Schema(type=openapi.TYPE_STRING, description="If not off should be group:key like 15:3072. Example: 15:3072")}),
                                                             'lifetime_ph2': openapi.Schema(type=openapi.TYPE_STRING, description="set lifetime with its unit like 1h or 3600s", pattern=r"(\d+)([hms])"),
                                                             }
                                                             ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createServerIPsec(request):
    """Creating a new server in system and adding it to the database"""
    if request.method == 'POST':
        try:
            data = request.data

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

            my_identifier = data.get("my_identifier", "")
            peer_identifier = data.get("peer_identifier", "")

            encryption_algorithm_ph1 = data.get("encryption_algorithm_ph1", "")
            hash_algorithm_ph1 = data.get("hash_algorithm_ph1", "")
            dh_key_group = data.get("dh_key_group", "")
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

            local_network = data.get("local_network", "")
            type_local_network = local_network.get("type_local_network", "")

            remote_network = data.get("remote_network", "")
            type_remote_network = remote_network.get("type_remote_network", "")
            address_remote_network = remote_network.get("address_local_network", "")

            sa_key_exchange = data.get("sa_key_exchange", "")
            protocol = sa_key_exchange.get("protocol", "")
            hash_algorithm_ph2 = sa_key_exchange.get("hash_algorithm_ph2", "")
            pfs_key_group = sa_key_exchange.get("pfs_key_group", "")
            lifetime_ph2 = data.get("lifetime_ph2", "")

            # auto_ping_host = data.get("auto_ping_host", "")
            # manual_spd_entries = data.get("manual_spd_entries", "")
            interface = Interface.objects.get(name_interface=interface_name)
            interface = interface.pk
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = interface_address.ip_address

            server_data = {"conn_name": conn_name,
                           "connection_method": connection_method,
                           "key_exchange_version": key_exchange_version,
                           "internet_protocol": internet_protocol,
                           "interface": interface,
                           "remote_gateway": remote_gateway,
                           "dynamic_gateway": dynamic_gateway,
                           "description_ph1": description_ph1,

                           "authentication_method": authentication_method,
                           "my_identifier": my_identifier,
                           "peer_identifier": peer_identifier,
                           
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
                           
                           "type_local_network": type_local_network,
                           
                           "type_remote_network": type_remote_network,
                           
                           "protocol": protocol,
                           "hash_algorithm_ph2": hash_algorithm_ph2,
                           "pfs_key_group": pfs_key_group,
                           "lifetime_ph2": lifetime_ph2,
                           
                           # auto_ping_host": auto_ping_host,
                           # manual_spd_entries": manual_spd_entries,
                           }
            
            if key_exchange_version == "V1":
                negotiation_mode = key_exchange.get("negotiation_mode", "")
                server_data["negotiation_mode"] = negotiation_mode

            ca = ''
            if authentication_method == "Mutual PSK":
                pre_shared_key = authentication.get("pre_shared_key", "")
                server_data["pre_shared_key"] = pre_shared_key
            elif authentication_method == "Mutual Public Key":
                local_key_pair = authentication.get("local_key_pair", "")
                peer_key_pair = authentication.get("peer_key_pair", "")
                server_data["local_key_pair"] = local_key_pair
                server_data["peer_key_pair"] = peer_key_pair
            else:
                cert = authentication.get("cert")
                certificate = Certificate.objects.get(name=cert)
                ca = CertificateAuthority.objects.get(id=certificate.certificate_authority.pk).name
                remote_distingushed_name = authentication.get("remote_distingushed_name", "")
                server_data["cert"] = cert
                server_data["remote_distingushed_name"] = remote_distingushed_name
                
            if deed_peer_detection:
                deed_peer_delay = deed_peer.get("deed_peer_delay", "")
                deed_peer_timeout = deed_peer.get("deed_peer_timeout", "")
                deed_peer_action = deed_peer.get("deed_peer_action")
                server_data["deed_peer_delay"] = deed_peer_delay
                server_data["deed_peer_timeout"] = deed_peer_timeout
                server_data["deed_peer_action"] = deed_peer_action

            if mode == "Route-based":
                local_address = mode_ph2.get("local_address", "")
                remote_address = mode_ph2.get("remote_address", "")
                server_data["local_address"] = local_address
                server_data["remote_address"] = remote_address

            if type_local_network == "Address":
                address_local_network = local_network.get("address_local_network", "")
            elif type_local_network == "Network":
                address_local_network = f'{local_network.get("address_local_network", "")}/{local_network.get("mask", "")}'
            else:
                address_local_network = f'{interface_address.ip_address}/{interface_address.netmask}'
            server_data["address_local_network"] = address_local_network
            data["address_local_network"] = address_local_network
                
            if type_remote_network == "Network":
                address_remote_network += remote_network.get("mask", "")
            server_data["address_remote_network"] = address_remote_network
            data["address_remote_network"] = address_remote_network

            if protocol == "ESP":
                encryption_algorithm_ph2 = sa_key_exchange.get("encryption_algorithm_ph2", "")
                data["encryption_algorithm_ph2"] = encryption_algorithm_ph2

            serializer_server = ServerIPsecSerializer(data=server_data)
            if serializer_server.is_valid():
            
                # Update the server config
                server_conf = json_to_str_server_ipsec(data)
                print("server_conf= ")
                print(server_conf)

                # Install the server in system
                install_server_ipsec(server_conf, authentication, interface_address.ip_address, remote_gateway, ca)

                # Add the server to the database
                serializer_server.save()
                return JsonResponse({"msg": f"Connection {conn_name} Configuration is done"}, status=201)
            else:
                return JsonResponse({"msg": list(serializer_server.errors.values())[0][0]}, status=400)
        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating ipsec server"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=400)
        except CertificateAuthority.DoesNotExist:
            return JsonResponse({"msg": "This CA does not exist"}, status=400)
        except Certificate.DoesNotExist:
            return JsonResponse({"msg": "This Certificate does not exist"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN IPSEC",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteServerIPsec(request, id):
    """Deleting a server from system and then from database"""
    try:
        if (request.method == 'DELETE'):
            server = ServerIPsec.objects.get(id=id)
            # delete from system
            interface = Interface.objects.get(id=server.interface)
            interface_address = IP4Config.objects.get(interface_id=interface.pk)
            if server.authentication_method == "Mutual PSK":
                deleted_line_in_secrets_file = f"""{interface_address.ip_address} {server.remote_gateway} : PSK '{server.pre_shared_key}' """
            else:
                deleted_line_in_secrets_file = f""" : RSA {server.cert}Key.pem """
            print("deleted_line_in_secrets_file: ", deleted_line_in_secrets_file)
            
            delete_server_ipsec(server.conn_name, deleted_line_in_secrets_file)
            # delete from database
            server.delete()
            return JsonResponse({"msg": f"delete {server.conn_name} succesfully"})
    except ServerIPsec.DoesNotExist:
        return JsonResponse({"msg": "This Server does not exist"}, status=400)
    except IP4Config.DoesNotExist:
        return JsonResponse({"msg": "This IPv4 config does not exist"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE AN IPSEC (same as create)",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, 
                                                 required=['conn_name', 'connection_method', 'key_exchange', 'internet_protocol', 'interface_name', 'remote_gateway', 'dynamic_gateway', 'authentication', 'my_identifier', 'encryption_algorithm_ph1', 'hash_algorithm_ph1', 'dh_key_group', 'policy', 'rekey', 'reauth', 'tunnel', 'nat_traversal', 'mobike', 'deed_peer', 'mode_ph2', 'local_network', 'remote_network', 'sa_key_exchange'],
                                                 properties={'conn_name': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'connection_method': openapi.Schema(type=openapi.TYPE_STRING, enum=["default", "Respond Only", "Start on traffic", "Start immediate"]),
                                                             'key_exchange': openapi.Schema(type=openapi.TYPE_OBJECT, required=['key_exchange_version'], 
                                                                                            properties={'key_exchange_version': openapi.Schema(type=openapi.TYPE_STRING, default="auto", enum=["auto", "V1", "V2"]),
                                                                                                        'negotiation_mode': openapi.Schema(type=openapi.TYPE_STRING, description="When Key version is V1", enum=["Main", "Aggressive"])}),
                                                             'internet_protocol': openapi.Schema(type=openapi.TYPE_STRING, enum=["IPv4", "IPv6"]),
                                                             'interface_name': openapi.Schema(type=openapi.TYPE_STRING, description="Interface name like LAN or WAN or any"),
                                                             'remote_gateway': openapi.Schema(type=openapi.TYPE_STRING, description="Remote address like 10.1.12.22"),
                                                             'dynamic_gateway': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'description_ph1': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'authentication': openapi.Schema(type=openapi.TYPE_OBJECT, required=['authentication'], 
                                                                                              properties={'authentication': openapi.Schema(type=openapi.TYPE_STRING, default="Mutual PSK", enum=["Mutual PSK", "Mutual Public Key", "Mutual RSA"]),
                                                                                                          'pre_shared_key': openapi.Schema(type=openapi.TYPE_STRING, description="required when authentication_method is Mutual PSK"),
                                                                                                          'local_key_pair': openapi.Schema(type=openapi.TYPE_STRING, description="required when authentication_method is Mutual Public Key"),
                                                                                                          'peer_key_pair': openapi.Schema(type=openapi.TYPE_STRING, description="required when authentication_method is Mutual Public Key"),
                                                                                                          'cert': openapi.Schema(type=openapi.TYPE_STRING, description="Certificate name from list of certificates, required when authentication_method is Mutual RSA"),
                                                                                                          'remote_distingushed_name': openapi.Schema(type=openapi.TYPE_STRING, description="all distingushed name of the remote server, required when authentication_method is Mutual RSA. Example:C=CH, ST=IPsec, L=Tunis, O=strongSwan, OU=My Organizational Unit, CN=device1, E=bak.akram94@gmail.com")}),
                                                             'my_identifier': openapi.Schema(type=openapi.TYPE_STRING, enum=["My IP address", "IP address", "Distinguished name", "User distinguished name", "ASN.1 distinguished name", "KeyID tag", "Dynamic DN"]),
                                                             'peer_identifier': openapi.Schema(type=openapi.TYPE_STRING, enum=["Peer IP address", "IP address", "Distinguished name", "User distinguished name", "ASN.1 distinguished name", "KeyID tag"]),
                                                             'encryption_algorithm_ph1': openapi.Schema(type=openapi.TYPE_STRING, enum=["128", "192", "256"]),
                                                             'hash_algorithm_ph1': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like sha256 and the list of hash_algorithm must sepeate with comma. Example: sha256,sha512"),
                                                             'dh_key_group': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like group:key like 15:3072 and the list of key_group must sepeate with comma. Example: 15:3072,20:384"),
                                                             'lifetime_ph1': openapi.Schema(type=openapi.TYPE_STRING, description="set lifetime with its unit like 1h or 3600s", pattern=r"(\d+)([hms])"),
                                                             'policy': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
                                                             'rekey': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'reauth': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'tunnel': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'nat_traversal': openapi.Schema(type=openapi.TYPE_STRING, default="auto", enum=["Disable", "E,able", "Force"]),
                                                             'mobike': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                             'deed_peer': openapi.Schema(type=openapi.TYPE_OBJECT, description="Deed Peer block", required=['disable'], 
                                                                                         properties={'disable': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                                                                                                     'deed_peer_delay': openapi.Schema(type=openapi.TYPE_STRING, pattern=r"(\d+)([hms])", description="set deed peer delay with its unit like 10s, required when selecting deed peer"),
                                                                                                     'deed_peer_timeout': openapi.Schema(type=openapi.TYPE_STRING, pattern=r"(\d+)([hms])", description="set deed peer timeout with its unit like 160s, required when selecting deed peer"),
                                                                                                     'deed_peer_action': openapi.Schema(type=openapi.TYPE_STRING, enum=["default", "Restart the tunnel", "Stop the tunnel"], default="default", description="set deed peer action, required when selecting deed peer")}),
                                                             'inactivity_timeout': openapi.Schema(type=openapi.TYPE_STRING, description="set inactivity timeout with its unit like 10s", pattern=r"(\d+)([hms])"),
                                                             'margin_time': openapi.Schema(type=openapi.TYPE_STRING, description="set margin time with its unit like 10s", pattern=r"(\d+)([hms])"),
                                                             'rekey_fuzz': openapi.Schema(type=openapi.TYPE_STRING, description="set rekey_fuzz with % (percentage symbol) like 10%", pattern=r"(\d+)%"),
                                                             'mode_ph2': openapi.Schema(type=openapi.TYPE_OBJECT, description="General information of phase 2", required=['mode'], 
                                                                                        properties={'mode': openapi.Schema(type=openapi.TYPE_STRING, default="Tunnel IPv4", enum=["Tunnel IPv4", "Tunnel IPv6", "Route-based", "Transport"]),
                                                                                                    'local_address': openapi.Schema(type=openapi.TYPE_STRING, description="Local Address, required when selecting Route-based"),
                                                                                                    'remote_address': openapi.Schema(type=openapi.TYPE_STRING, description="Remote Address, required when selecting Route-based"),}),
                                                             'description_ph2': openapi.Schema(type=openapi.TYPE_STRING),
                                                             'local_network': openapi.Schema(type=openapi.TYPE_OBJECT, description="Local network block", required=['type_local_network'], 
                                                                                             properties={'type_local_network': openapi.Schema(type=openapi.TYPE_STRING, default="Address", enum=["Address", "Network", "WAN subnet", "LAN subnet"]),
                                                                                                         'address_local_network': openapi.Schema(type=openapi.TYPE_STRING, description="Address of local network like 10.1.12.0, required when selecting Address or Network"),
                                                                                                         'mask': openapi.Schema(type=openapi.TYPE_STRING, description="Address mask like 24, required when selecting Network"),}),
                                                             'remote_network': openapi.Schema(type=openapi.TYPE_OBJECT, description="Remote network block", required=['type_remote_network', 'address_remote_network'], 
                                                                                              properties={'type_remote_network': openapi.Schema(type=openapi.TYPE_STRING, default="Address", enum=["Address", "Network"]),
                                                                                                          'address_remote_network': openapi.Schema(type=openapi.TYPE_STRING, description="Address of remote network like 51.68.170.149"),
                                                                                                          'mask': openapi.Schema(type=openapi.TYPE_STRING, description="Address mask like 24, required when selecting Network"),}),
                                                             'sa_key_exchange': openapi.Schema(type=openapi.TYPE_OBJECT, description="Key Exchange block", required=['protocol', 'hash_algorithm_ph2', 'pfs_key_group'], 
                                                                                               properties={'protocol': openapi.Schema(type=openapi.TYPE_STRING, default="ESP", enum=["ESP", "AH"]),
                                                                                                           'encryption_algorithm_ph2': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like 256 and the list of hash_algorithm must sepeate with comma. Example: 128,256"),
                                                                                                           'hash_algorithm_ph2': openapi.Schema(type=openapi.TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be like sha256 and the list of hash_algorithm must sepeate with comma. Example: sha256,sha384"),
                                                                                                           'pfs_key_group': openapi.Schema(type=openapi.TYPE_STRING, description="If not off should be group:key like 15:3072. Example: 15:3072")}),
                                                             'lifetime_ph2': openapi.Schema(type=openapi.TYPE_STRING, description="set lifetime with its unit like 1h or 3600s", pattern=r"(\d+)([hms])"),
                                                             }
                                                             ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def updateServerIPsec(request, id):
    """Updating a server from system and database"""
    if (request.method == 'PUT'):
        try:
            # parse the incoming information
            data = request.data
            server = ServerIPsec.objects.get(id=id)

            if server.authentication_method == "Mutual PSK":
                previous_interface_address = IP4Config.objects.get(interface_id=server.interface)
                updated_line_in_secrets_file = f"""{previous_interface_address.ip_address} {server.remote_gateway} : PSK '{server.pre_shared_key}' """
            else:
                updated_line_in_secrets_file = f""" : RSA {server.cert}Key.pem """
            print("updated_line_in_secrets_file: ", updated_line_in_secrets_file)

            
            server.conn_name = data.get("conn_name", "")
            server.connection_method = data.get("connection_method", "")
            key_exchange = data.get("key_exchange", "")
            server.key_exchange_version = key_exchange.get("key_exchange_version", "")
            server.internet_protocol = data.get("internet_protocol", "")
            interface_name = data.get("interface_name", "")
            server.remote_gateway = data.get("remote_gateway", "")
            server.dynamic_gateway = data.get("dynamic_gateway", "")
            server.description_ph1 = data.get("description_ph1", "")

            authentication = data.get("authentication", "")
            server.authentication_method = authentication.get("authentication_method", "")

            server.my_identifier = data.get("my_identifier", "")
            server.peer_identifier = data.get("peer_identifier", "")

            server.encryption_algorithm_ph1 = data.get("encryption_algorithm_ph1", "")
            server.hash_algorithm_ph1 = data.get("hash_algorithm_ph1", "")
            server.dh_key_group = data.get("dh_key_group", "")
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

            local_network = data.get("local_network", "")
            server.type_local_network = local_network.get("type_local_network", "")

            remote_network = data.get("remote_network", "")
            server.type_remote_network = remote_network.get("type_remote_network", "")
            server.address_remote_network = remote_network.get("address_local_network", "")

            sa_key_exchange = data.get("sa_key_exchange", "")
            server.protocol = sa_key_exchange.get("protocol", "")
            server.hash_algorithm_ph2 = sa_key_exchange.get("hash_algorithm_ph2", "")
            server.pfs_key_group = sa_key_exchange.get("pfs_key_group", "")
            server.lifetime_ph2 = data.get("lifetime_ph2", "")

            # auto_ping_host = data.get("auto_ping_host", "")
            # manual_spd_entries = data.get("manual_spd_entries", "")
            interface = Interface.objects.get(name_interface=interface_name)
            server.interface = interface.pk
            interface_address = IP4Config.objects.get(interface_id=interface)
            data["interface_address"] = interface_address.ip_address

            if server.key_exchange_version == "V1":
                server.negotiation_mode = key_exchange.get("negotiation_mode", "")

            ca = ''
            if server.authentication_method == "Mutual PSK":
                server.pre_shared_key = authentication.get("pre_shared_key", "")
            elif server.authentication_method == "Mutual Public Key":
                server.local_key_pair = authentication.get("local_key_pair", "")
                server.peer_key_pair = authentication.get("peer_key_pair")
            else:
                server.cert = authentication.get("cert")
                certificate = Certificate.objects.get(name=server.cert)
                ca = CertificateAuthority.objects.get(id=certificate.pk).name
                server.remote_distingushed_name = authentication.get("remote_distingushed_name", "")
                
            if server.deed_peer_detection:
                server.deed_peer_delay = deed_peer.get("deed_peer_delay", "")
                server.deed_peer_timeout = deed_peer.get("deed_peer_timeout", "")
                server.deed_peer_action = deed_peer.get("deed_peer_action")

            if server.mode == "Route-based":
                server.local_address = mode_ph2.get("local_address", "")
                server.remote_address = mode_ph2.get("remote_address", "")

            if server.type_local_network == "Address":
                server.address_local_network = local_network.get("address_local_network", "")
            elif server.type_local_network == "Network":
                server.address_local_network = f'{local_network.get("address_local_network", "")}/{local_network.get("mask", "")}'
            else:
                server.address_local_network = f'{interface_address.ip_address}/{interface_address.netmask}'
            data["address_local_network"] = server.address_local_network
                
            if server.type_remote_network == "Network":
                server.address_remote_network += f'/{remote_network.get("mask", "")}'
            data["address_remote_network"] = server.address_remote_network

            if server.protocol == "ESP":
                server.encryption_algorithm_ph2 = sa_key_exchange.get("encryption_algorithm_ph2", "")
                data["encryption_algorithm_ph2"] = server.encryption_algorithm_ph2

            serializer_server = ServerIPsecSerializer(server, data=data)
            if serializer_server.is_valid():
            
                # Update the server config
                server_conf = json_to_str_server_ipsec(data)
                print("server_conf= ")
                print(server_conf)

                # Install the server in system
                update_server_ipsec(server.conn_name, updated_line_in_secrets_file, server_conf, 
                                    authentication, interface_address.ip_address, server.remote_gateway, ca)

                # Add the server to the database
                serializer_server.save()
                return JsonResponse({"msg": f"Connection {server.conn_name} Configuration is updated"}, status=201)
            else:
                return JsonResponse({"msg": list(serializer_server.errors.values())[0][0]}, status=400)

        except ServerIPsec.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=400)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=400)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=400)
