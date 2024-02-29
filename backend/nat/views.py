from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from backend.nat.contant_variables import CONSTANT_SNAT_RULE
from backend.nat.list_nat import get_list_all_snat, get_one_snat
from backend.nat.models import SNat
from backend.nat.serializers import SNatSerializer
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
                         type=TYPE_OBJECT, required=['name', 'source_address', 'area', 'algorythme_type', 
                                                     'health_check', 'health_check_target'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"]),
                                     'protocol': Schema(type=TYPE_STRING),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask"),
                                     'source_port': Schema(type=TYPE_STRING),
                                     'destination_address': Schema(type=TYPE_STRING, description="Genrally it takes Any but can take format of address/mask"),
                                     'destination_port': Schema(type=TYPE_STRING),
                                     'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
                                     'translation_address_from': Schema(type=TYPE_STRING, description="format of address like 51.32.100.5"),
                                     'translation_address_to': Schema(type=TYPE_STRING, description="format of address like 51.32.100.10"),
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
                         type=TYPE_OBJECT, required=['name', 'source_address', 'area', 'algorythme_type', 
                                                     'health_check', 'health_check_target'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"]),
                                     'protocol': Schema(type=TYPE_STRING),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask"),
                                     'source_port': Schema(type=TYPE_STRING),
                                     'destination_address': Schema(type=TYPE_STRING, description="Genrally it takes Any but can take format of address/mask"),
                                     'destination_port': Schema(type=TYPE_STRING),
                                     'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
                                     'translation_address_from': Schema(type=TYPE_STRING, description="format of address like 51.32.100.5"),
                                     'translation_address_to': Schema(type=TYPE_STRING, description="format of address like 51.32.100.10"),
                                     'translation_port': Schema(type=TYPE_STRING),
                                     'description': Schema(type=TYPE_STRING, description="description of SNAT rule"),
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_snat(request, id):
    """Updating a new SNAT rule"""
    try:
        data = request.data
        snat = SNat.objects.get(id=id)

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
