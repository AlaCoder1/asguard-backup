import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core import serializers

from backend.ipsec.functions import json_to_str_server_ipsec
from backend.ipsec.serializers import ServerIPsecSerializer
from backend.ipsec.server_ipsec import delete_server_ipsec, install_server_ipsec, update_server_ipsec
from backend.managementCertificates.models import Certificate, CertificateAuthority
from backend.network.models import IP4Config, Interface
from backend.openvpn.manage_errors import CommandExecutionError

from .models import ServerIPsec


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllServerIPsec(request):
    list_ipsec = []
    if (request.method == 'GET'):
        ipsec = ServerIPsec.objects.all()
        ipsecDict = serializers.serialize("json", ipsec)
        res = json.loads(ipsecDict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_ipsec.append(res[i]['fields'])
        # return list_ipsec
        return JsonResponse(list_ipsec, safe=False)
    

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getServerIPsec(request, id):
    """Getting server by id from database"""
    if (request.method == 'GET'):
        server_ipsec = ServerIPsec.objects.filter(pk=id)
        server_ipsecDict = serializers.serialize("json", server_ipsec)
        res = json.loads(server_ipsecDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        return JsonResponse(res[0]['fields'], safe=False)


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
                print(serializer_server.errors)
                return JsonResponse({"msg": "Error in server configuration"}, status=401)
        except CommandExecutionError:
            return JsonResponse({"msg": "Error in creating ipsec server"}, status=401)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=401)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=401)
        except CertificateAuthority.DoesNotExist:
            return JsonResponse({"msg": "This CA does not exist"}, status=401)
        except Certificate.DoesNotExist:
            return JsonResponse({"msg": "This Certificate does not exist"}, status=401)


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
        return JsonResponse({"msg": "This Server does not exist"}, status=401)
    except IP4Config.DoesNotExist:
        return JsonResponse({"msg": "This IPv4 config does not exist"}, status=401)


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
                print(serializer_server.errors)
                return JsonResponse({"msg": "Error in server configuration"}, status=401)

        except ServerIPsec.DoesNotExist:
            return JsonResponse({"msg": "This Server does not exist"}, status=401)
        except Interface.DoesNotExist:
            return JsonResponse({"msg": "This Interface does not exist"}, status=401)
        except IP4Config.DoesNotExist:
            return JsonResponse({"msg": "This IPv4 config does not exist"}, status=401)
