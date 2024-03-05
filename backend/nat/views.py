from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from backend.nat.contant_variables import CONSTANT_DNAT_RULE, CONSTANT_SNAT_RULE, CONSTANT_ONE_TO_ONE_NAT_RULE
from backend.nat.list_nat import get_list_all_dnat, get_list_all_one_to_one_nat, get_list_all_snat, get_one_dnat, get_one_one_to_one_nat, get_one_snat
from backend.nat.models import DNat, OneToOneNat, SNat
from backend.nat.serializers import DNatSerializer, OneToOneNatSerializer, SNatSerializer
from backend.nat.utils_dnat_system import create_dnat_rule_in_system, delete_dnat_rule_in_system, update_dnat_rule_in_system
from backend.nat.utils_one_to_one_nat_system import create_one_to_one_nat_rule_in_system, delete_one_to_one_nat_rule_in_system, update_one_to_one_nat_rule_in_system
from backend.nat.utils_snat_system import create_snat_rule_in_system, delete_snat_rule_in_system, update_snat_rule_in_system

from backend.network.models import Interface
from utils.constant_variables import ERROR_MESSAGES_CREATING, ERROR_MESSAGES_DELETING, ERROR_MESSAGES_INEXISTANT, ERROR_MESSAGES_START, ERROR_MESSAGES_STOP, ERROR_MESSAGES_UPDATING, SUCCESS_MESSAGES_CREATING_ITEM, SUCCESS_MESSAGES_DELETE, SUCCESS_MESSAGES_START, SUCCESS_MESSAGES_STOP, SUCCESS_MESSAGES_UPDATE
from utils.errors_utils import CommandExecutionError


########################################
################ SNAT ##################
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL SNAT RULES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_snat(request):
    """Getting all snat from database"""
    list_snat = []
    list_snat = get_list_all_snat()
    return JsonResponse(list_snat, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN SNAT RULE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_snat(request, id):
    """Getting snat by id from database"""
    snat = get_one_snat(id)
    return JsonResponse(snat, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE AN SNAT RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'destination_address', 'snat_type'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
                                     'protocol': Schema(type=TYPE_STRING, description="required when choosing Static"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'source_port': Schema(type=TYPE_STRING),
                                     'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'destination_port': Schema(type=TYPE_STRING),
                                     'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
                                     'translation_address_from': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.5"),
                                     'translation_address_to': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.10"),
                                     'translation_port': Schema(type=TYPE_STRING),
                                     'description': Schema(type=TYPE_STRING, description="description of SNAT rule"),
                                     }
                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_snat(request):
    """Creating a new SNAT rule and adding it to the database"""
    try:
        data = request.data
        
        serializer_snat = SNatSerializer(data=data)
        if serializer_snat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname
            
            source = "any"
            if data["source_address"] != "":
                source = {"address": data["source_address"],
                          "port": data["source_port"]}
            destination = "any"
            if data["destination_address"] != "":
                destination = {"address": data["destination_address"],
                          "port": data["destination_port"]}
            
            outgoing_ip_address = ["masquerade"]
            if data["snat_type"] == "Static":
                outgoing_ip_address = ["snat", "ip", "to", 
                                       f"""{data["translation_address_from"]}-{data["translation_address_to"]}:{data["translation_port"]}"""]

            # Add the rule in system
            rule_number = create_snat_rule_in_system(interface_ifname, source, destination, data["protocol"],
                                                     outgoing_ip_address)
            data["rule_number"] = int(rule_number)

            serializer_snat = SNatSerializer(data=data)
            if serializer_snat.is_valid():

                # Add the rule to the database
                serializer_snat.save()
                return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format(CONSTANT_SNAT_RULE, "")}, status=201)

        return JsonResponse({"error": list(serializer_snat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format(CONSTANT_SNAT_RULE)}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN SNAT RULE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_snat(request, id):
    """Deleting an snat from database"""
    try:
        snat = SNat.objects.get(id=id)

        if snat.rule_status:
            # Delete rule from system
            delete_snat_rule_in_system(snat.rule_number)

        # delete rule from database
        snat.delete()
        return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(CONSTANT_SNAT_RULE)}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_DELETING.format(CONSTANT_SNAT_RULE)}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_SNAT_RULE)}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UPDATE AN SNAT RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'destination_address', 'snat_type'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
                                     'protocol': Schema(type=TYPE_STRING, description="required when choosing Static"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'source_port': Schema(type=TYPE_STRING),
                                     'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'destination_port': Schema(type=TYPE_STRING),
                                     'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
                                     'translation_address_from': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.5"),
                                     'translation_address_to': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.10"),
                                     'translation_port': Schema(type=TYPE_STRING),
                                     'description': Schema(type=TYPE_STRING, description="description of SNAT rule"),
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_snat(request, id):
    """Updating an SNAT rule"""
    try:
        data = request.data
        snat = SNat.objects.get(id=id)

        interface_ifname = Interface.objects.get(id=data["interface"]).ifname

        source = "any"
        if data["source_address"] != "":
            source = {"address": data["source_address"],
                      "port": data["source_port"]}
        else:
            snat.source_port = None
        destination = "any"
        if data["destination_address"] != "":
            destination = {"address": data["destination_address"],
                           "port": data["destination_port"]}
        else:
            snat.destination_port = None
        
        outgoing_ip_address = ["masquerade"]
        if data["snat_type"] == "Static":
            outgoing_ip_address = ["snat", "ip", "to", 
                                   f"""{data["translation_address_from"]}-{data["translation_address_to"]}:{data["translation_port"]}"""]
        else:
            snat.translation_address_from = None
            snat.translation_address_to = None
            snat.translation_port = None
        serializer_snat = SNatSerializer(snat, data=data)
        if serializer_snat.is_valid():

            if snat.rule_status:
                # Update the rule in system
                rule_number = update_snat_rule_in_system(interface_ifname, source, destination, data["protocol"],
                                                         outgoing_ip_address, snat.rule_number)
                data["rule_number"] = int(rule_number)

                serializer_snat = SNatSerializer(snat, data=data)
                if serializer_snat.is_valid():

                    # Update the rule in the database
                    serializer_snat.save()
                    return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(CONSTANT_SNAT_RULE)}, status=201)
                else:
                    return JsonResponse({"error": list(serializer_snat.errors.values())[0][0]}, status=400)
            
            serializer_snat.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(CONSTANT_SNAT_RULE)}, status=201)
        
        return JsonResponse({"error": list(serializer_snat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_UPDATING.format(CONSTANT_SNAT_RULE)}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_SNAT_RULE)}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_snat(request, id):
    """Start an SNAT rule. Change rule_status to True to add the rule to the nft table"""
    try:
        snat = SNat.objects.get(id=id)

        source = "any"
        if snat.source_address != "":
            source = {"address": snat.source_address,
                      "port": snat.source_port}
        destination = "any"
        if snat.destination_address != "":
            destination = {"address": snat.destination_address,
                           "port": snat.destination_port}
        
        outgoing_ip_address = ["masquerade"]
        if snat.snat_type == "Static":
            outgoing_ip_address = ["snat", "ip", "to", 
                                   f"""{snat.translation_address_from}-{snat.translation_address_to}:{snat.translation_port}"""]

        # Add the rule in system
        rule_number = create_snat_rule_in_system(snat.interface.ifname, source, destination, snat.protocol,
                                                 outgoing_ip_address)
        snat.rule_number = int(rule_number)

        snat.rule_status = True
        snat.save()
        
        return JsonResponse({"msg": SUCCESS_MESSAGES_START.format(CONSTANT_SNAT_RULE, "")}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_START.format(CONSTANT_SNAT_RULE)}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_SNAT_RULE)}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_snat(request, id):
    """Stop an SNAT rule. By changing rule_status to False, the while loop of the script will be breaked"""
    try:
        snat = SNat.objects.get(id=id)

        # Delete rule from system
        delete_snat_rule_in_system(snat.rule_number)
        
        snat.rule_status = False
        snat.rule_number = None
        snat.save()
        
        return JsonResponse({"msg": SUCCESS_MESSAGES_STOP.format(CONSTANT_SNAT_RULE, "")}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STOP.format(CONSTANT_SNAT_RULE)}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_SNAT_RULE)}, status=400)


########################################
################ OneToOne NAT ##################
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL OneToOneNat RULES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_one_to_one_nat(request):
    """Getting all one_to_one_nat from database"""
    list_one_to_one_nat = []
    list_one_to_one_nat = get_list_all_one_to_one_nat()
    return JsonResponse(list_one_to_one_nat, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN OneToOneNat RULE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_one_to_one_nat(request, id):
    """Getting one_to_one_nat by id from database"""
    one_to_one_nat = get_one_one_to_one_nat(id)
    return JsonResponse(one_to_one_nat, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE A OneToOneNat RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'translation_address', 'destination_address'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'translation_address': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.5"),
                                     'description': Schema(type=TYPE_STRING, description="description of OneToOneNat rule"),
                                     }
                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_one_to_one_nat(request):
    """Creating a new OneToOneNat rule and adding it to the database"""
    try:
        data = request.data
        
        serializer_one_to_one_nat = OneToOneNatSerializer(data=data)
        if serializer_one_to_one_nat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname
            
            destination = "any"
            if data["destination_address"] != "":
                destination = data["destination_address"]
            
            # Add the rule in system
            rule_number = create_one_to_one_nat_rule_in_system(interface_ifname, data["source_address"], destination, data["translation_address"])
            data["rule_number"] = int(rule_number)

            serializer_one_to_one_nat = OneToOneNatSerializer(data=data)
            if serializer_one_to_one_nat.is_valid():

                # Add the rule to the database
                serializer_one_to_one_nat.save()
                return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format(CONSTANT_ONE_TO_ONE_NAT_RULE, "")}, status=201)

        return JsonResponse({"error": list(serializer_one_to_one_nat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN OneToOneNat RULE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_one_to_one_nat(request, id):
    """Deleting an one_to_one_nat from database"""
    try:
        one_to_one_nat = OneToOneNat.objects.get(id=id)

        if one_to_one_nat.rule_status:
            # Delete rule from system
            delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)

        # delete rule from database
        one_to_one_nat.delete()
        return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_DELETING.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UPDATE A OneToOneNat RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'translation_address', 'destination_address'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'translation_address': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.5"),
                                     'description': Schema(type=TYPE_STRING, description="description of OneToOneNat rule"),
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_one_to_one_nat(request, id):
    """Updating an OneToOneNat rule"""
    try:
        data = request.data
        one_to_one_nat = OneToOneNat.objects.get(id=id)
        
        serializer_one_to_one_nat = OneToOneNatSerializer(one_to_one_nat, data=data)
        if serializer_one_to_one_nat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname
            
            destination = "any"
            if data["destination_address"] != "":
                destination = data["destination_address"]
            
            # update the rule in system if the rule was started
            if one_to_one_nat.rule_status:
                rule_number = update_one_to_one_nat_rule_in_system(interface_ifname, data["source_address"], destination, 
                                                                   data["translation_address"], one_to_one_nat.rule_number)
                data["rule_number"] = int(rule_number)

                serializer_one_to_one_nat = OneToOneNatSerializer(one_to_one_nat, data=data)
                if serializer_one_to_one_nat.is_valid():

                    # Add the rule to the database
                    serializer_one_to_one_nat.save()
                    return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=201)
                else:
                    return JsonResponse({"error": list(serializer_one_to_one_nat.errors.values())[0][0]}, status=400)
        
            serializer_one_to_one_nat.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=201)

        return JsonResponse({"error": list(serializer_one_to_one_nat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_one_to_one_nat(request, id):
    """Start a OneToOneNat rule"""
    try:
        one_to_one_nat = OneToOneNat.objects.get(id=id)

        destination = "any"
        if one_to_one_nat.destination_address != "":
            destination = one_to_one_nat.destination_address

        # Add the rule in system
        rule_number = create_one_to_one_nat_rule_in_system(one_to_one_nat.interface.ifname, one_to_one_nat.source_address, destination,
                                                           one_to_one_nat.translation_address)
        one_to_one_nat.rule_number = int(rule_number)

        one_to_one_nat.rule_status = True
        one_to_one_nat.save()
        
        return JsonResponse({"msg": SUCCESS_MESSAGES_START.format(CONSTANT_ONE_TO_ONE_NAT_RULE, "")}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_START.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_one_to_one_nat(request, id):
    """Stop a OneToOneNat rule"""
    try:
        one_to_one_nat = OneToOneNat.objects.get(id=id)

        # Delete rule from system
        delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
        
        one_to_one_nat.rule_status = False
        one_to_one_nat.rule_number = None
        one_to_one_nat.save()
        
        return JsonResponse({"msg": SUCCESS_MESSAGES_STOP.format(CONSTANT_ONE_TO_ONE_NAT_RULE, "")}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STOP.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_ONE_TO_ONE_NAT_RULE)}, status=400)


########################################
################ DNAT ##################
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL DNAT RULES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_dnat(request):
    """Getting all dnat from database"""
    list_dnat = []
    list_dnat = get_list_all_dnat()
    return JsonResponse(list_dnat, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A DNAT RULE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_dnat(request, id):
    """Getting dnat by id from database"""
    dnat = get_one_dnat(id)
    return JsonResponse(dnat, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE A DNAT RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'source_port_from', 'source_port_to', 
                                                     'external_address', 'internal_address', 'port_forwarding'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
                                     'protocol': Schema(type=TYPE_STRING, description="required when choosing Static"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'source_port_from': Schema(type=TYPE_STRING),
                                     'source_port_to': Schema(type=TYPE_STRING),
                                     'external_address': Schema(type=TYPE_STRING, description="format of address or blank for Any"),
                                     'internal_address': Schema(type=TYPE_STRING, description="required in format of address"),
                                     'port_forwarding': Schema(type=TYPE_BOOLEAN),
                                     'destination_port_from': Schema(type=TYPE_STRING, description="required when selecting Port Forwarding"),
                                     'destination_port_to': Schema(type=TYPE_STRING, description="required when selecting Port Forwarding"),
                                     'destination_port': Schema(type=TYPE_STRING, description="required when selecting Port Forwarding"),
                                     'description': Schema(type=TYPE_STRING, description="description of DNAT rule"),
                                     }
                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_dnat(request):
    """Creating a new DNAT rule and adding it to the database"""
    try:
        data = request.data
        
        serializer_dnat = DNatSerializer(data=data)
        if serializer_dnat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname
            
            source = "any"
            if data["source_address"] != "":
                source = {"address": data["source_address"],
                          "port": data["source_port_from"]}
                if data["source_port_to"] != "":
                    source["port"] += f"""-{data["source_port_to"]}"""

            destination = {"external_address": data["external_address"],
                           "internal_address": data["internal_address"],
                           "port_forwarding": data["port_forwarding"]}
            if data["port_forwarding"]:
                destination["port_forwarding"] = f'{data["destination_port_from"]}-{data["destination_port_to"]}'
                destination["port"] = f' : {data["destination_port"]}'
            
            rule_number = create_dnat_rule_in_system(interface_ifname, source, destination, data["protocol"])
            data["rule_number"] = int(rule_number)

            serializer_dnat = DNatSerializer(data=data)
            if serializer_dnat.is_valid():

                # Add the rule to the database
                serializer_dnat.save()
                return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format(CONSTANT_DNAT_RULE, "")}, status=201)

        return JsonResponse({"error": list(serializer_dnat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format(CONSTANT_DNAT_RULE)}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN DNAT RULE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_dnat(request, id):
    """Deleting an dnat from database"""
    try:
        dnat = DNat.objects.get(id=id)

        if dnat.rule_status:
            # Delete rule from system
            delete_dnat_rule_in_system(dnat.rule_number)

        # delete rule from database
        dnat.delete()
        return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(CONSTANT_DNAT_RULE)}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_DELETING.format(CONSTANT_DNAT_RULE)}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_DNAT_RULE)}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE A DNAT RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'source_port_from', 'source_port_to', 
                                                     'external_address', 'internal_address', 'port_forwarding'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
                                     'protocol': Schema(type=TYPE_STRING, description="required when choosing Static"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'source_port_from': Schema(type=TYPE_STRING),
                                     'source_port_to': Schema(type=TYPE_STRING),
                                     'external_address': Schema(type=TYPE_STRING, description="format of address or blank for Any"),
                                     'internal_address': Schema(type=TYPE_STRING, description="required in format of address"),
                                     'port_forwarding': Schema(type=TYPE_BOOLEAN),
                                     'destination_port_from': Schema(type=TYPE_STRING, description="required when selecting Port Forwarding"),
                                     'destination_port_to': Schema(type=TYPE_STRING, description="required when selecting Port Forwarding"),
                                     'destination_port': Schema(type=TYPE_STRING, description="required when selecting Port Forwarding"),
                                     'description': Schema(type=TYPE_STRING, description="description of DNAT rule"),
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_dnat(request, id):
    """Updating a DNAT rule"""
    try:
        data = request.data
        dnat = DNat.objects.get(id=id)

        interface_ifname = Interface.objects.get(id=data["interface"]).ifname

        source = "any"
        if data["source_address"] != "":
            source = {"address": data["source_address"],
                      "port": data["source_port_from"]}
            if data["source_port_to"] != "":
                source["port"] += f"""-{data["source_port_to"]}"""

        destination = {"external_address": data["external_address"],
                       "internal_address": data["internal_address"],
                       "port_forwarding": data["port_forwarding"]}
        if data["port_forwarding"]:
            destination["port_forwarding"] = f'{data["destination_port_from"]}-{data["destination_port_to"]}'
            destination["port"] = f' : {data["destination_port"]}'
        else:
            dnat.destination_port_from = None
            dnat.destination_port_to = None
            dnat.destination_port = None
        
        serializer_dnat = DNatSerializer(dnat, data=data)
        if serializer_dnat.is_valid():

            if dnat.rule_status:
                # Update the rule in system
                rule_number = update_dnat_rule_in_system(interface_ifname, source, destination, data["protocol"],
                                                         dnat.rule_number)
                data["rule_number"] = int(rule_number)

                serializer_dnat = DNatSerializer(dnat, data=data)
                if serializer_dnat.is_valid():

                    # Update the rule in the database
                    serializer_dnat.save()
                    return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(CONSTANT_DNAT_RULE)}, status=201)
            serializer_dnat.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(CONSTANT_DNAT_RULE)}, status=201)
        
        return JsonResponse({"error": list(serializer_dnat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_UPDATING.format(CONSTANT_DNAT_RULE)}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_SNAT_RULE)}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_dnat(request, id):
    """Start a DNAT rule. Change rule_status to True to add the rule to the nft table"""
    try:
        dnat = DNat.objects.get(id=id)

        source = "any"
        if dnat.source_address != "":
            source = {"address": dnat.source_address,
                      "port": dnat.source_port_from}
            if dnat.source_port_to != "":
                source["port"] += f"""-{dnat.source_port_to}"""

        destination = {"external_address": dnat.external_address,
                       "internal_address": dnat.internal_address}
        
        if dnat.destination_port_from:
            destination["port_forwarding"] = f'{dnat.destination_port_from}-{dnat.destination_port_to}'
            destination["port"] = f' : {dnat.destination_port}'
        else:
            destination["port_forwarding"] = False

        # Add the rule in system
        rule_number = create_dnat_rule_in_system(dnat.interface.ifname, source, destination, dnat.protocol)
        dnat.rule_number = int(rule_number)

        dnat.rule_status = True
        dnat.save()
        
        return JsonResponse({"msg": SUCCESS_MESSAGES_START.format(CONSTANT_DNAT_RULE, "")}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_START.format(CONSTANT_DNAT_RULE)}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_DNAT_RULE)}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_dnat(request, id):
    """Stop an DNAT rule. By changing rule_status to False, the while loop of the script will be breaked"""
    try:
        dnat = DNat.objects.get(id=id)

        # Delete rule from system
        delete_dnat_rule_in_system(dnat.rule_number)
        
        dnat.rule_status = False
        dnat.rule_number = None
        dnat.save()
        
        return JsonResponse({"msg": SUCCESS_MESSAGES_STOP.format(CONSTANT_DNAT_RULE, "")}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STOP.format(CONSTANT_DNAT_RULE)}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format(CONSTANT_DNAT_RULE)}, status=400)
