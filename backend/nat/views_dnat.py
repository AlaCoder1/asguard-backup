from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from .list_nat import get_list_all_dnat, get_one_dnat
from .models import DNat
from .serializers import DNatSerializer
from .utils import change_position_rule, get_next_nat_handle, input_create_dnat
from .utils_dnat_system import change_rule_dnat_position_in_system, create_dnat_rule_in_system, delete_dnat_rule_in_system, update_dnat_rule_in_system

from backend.network.models import Interface
from utils.errors_utils import CommandExecutionError
from utils.utils_functions import fix_ipv4_address


# Constants
CONSTANT_DNAT_RULE = _("DNAT rule")
CONSTANT_DNAT_RULE_POSITION = _("DNAT rule position")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
SUCCESS_MESSAGES_STARTING = _("is started")
SUCCESS_MESSAGES_STOPING = _("is stoped")
SUCCESS_MESSAGES_CHANGE = _("is changed")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UPDATING = _("System error in updating")
ERROR_MESSAGES_STARTING = _("System error in starting")
ERROR_MESSAGES_STOPING = _("System error in stoping")
ERROR_MESSAGES_CHANGING = _("System error in changing")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


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


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE A DNAT RULE", 
    request_body=Schema(type=TYPE_OBJECT, required=[
        'interface', 'source_address', 'source_port_from', 'source_port_to', 
        'external_address', 'internal_address', 'port_forwarding'],
    properties={
        'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface"),
        'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"]),
        'protocol': Schema(type=TYPE_STRING, enum=["udp", "tcp"]),
        'source_address': Schema(type=TYPE_STRING, example="50.50.50.0/24", description="format of address/mask or blank for Any"),
        'source_port_from': Schema(type=TYPE_STRING, example="80"),
        'source_port_to': Schema(type=TYPE_STRING, example="443"),
        'external_address': Schema(type=TYPE_STRING, example="41.41.41.0", description="format of address or blank for Any"),
        'internal_address': Schema(type=TYPE_STRING, example="10.1.12.75", description="required in format of address"),
        'port_forwarding': Schema(type=TYPE_BOOLEAN, default=False),
        'destination_port_from': Schema(type=TYPE_STRING, example="80", description="required when selecting Port Forwarding"),
        'destination_port_to': Schema(type=TYPE_STRING, example="443", description="required when selecting Port Forwarding"),
        'destination_port': Schema(type=TYPE_STRING, example="5000", description="required when selecting Port Forwarding"),
        'description': Schema(type=TYPE_STRING, example="Description DNAT", description="description of DNAT rule"),
        }
        ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_dnat(request):
    """Creating a new DNAT rule and adding it to the database"""
    try:
        data = request.data
        # Apply correction for ipv4 addresses
        data["source_address"], data["external_address"], data["internal_address"] = fix_ipv4_address(
            [data["source_address"], data["external_address"], data["internal_address"]])
        
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
            
            rule_number, rule_content = create_dnat_rule_in_system(
                interface_ifname, source, destination, data["protocol"])
            data["rule_number"] = int(rule_number)
            data["rule_content"] = rule_content

            data["db_position"] = 1
            for dnat_rule in DNat.objects.all().order_by("-db_position"):
                dnat_rule.db_position += 1
                dnat_rule.save()

            serializer_dnat = DNatSerializer(data=data)
            if serializer_dnat.is_valid():

                # Add the rule to the database
                serializer_dnat.save()
                return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_CREATING}"}, status=201)

        return JsonResponse({"error": list(serializer_dnat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_DNAT_RULE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN DNAT RULE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_dnat(request, id):
    """Deleting a dnat from database"""
    try:
        dnat = DNat.objects.get(id=id)

        if dnat.rule_status:
            # Delete rule from system
            delete_dnat_rule_in_system(dnat.rule_number)

            dnat.delete()
            
            for dnat_rule in DNat.objects.filter(db_position__gt=dnat.db_position).order_by("db_position"):
                dnat_rule.db_position -= 1
                dnat_rule.save()
            return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

        # delete rule from database
        dnat.delete()
        return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_DNAT_RULE}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE A DNAT RULE", 
    request_body=Schema(type=TYPE_OBJECT, required=[
        'interface', 'source_address', 'source_port_from', 'source_port_to', 
        'external_address', 'internal_address', 'port_forwarding'],
    properties={
        'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface"),
        'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"]),
        'protocol': Schema(type=TYPE_STRING, enum=["udp", "tcp"]),
        'source_address': Schema(type=TYPE_STRING, example="50.50.50.0/24", description="format of address/mask or blank for Any"),
        'source_port_from': Schema(type=TYPE_STRING, example="80"),
        'source_port_to': Schema(type=TYPE_STRING, example="443"),
        'external_address': Schema(type=TYPE_STRING, example="41.41.41.0", description="format of address or blank for Any"),
        'internal_address': Schema(type=TYPE_STRING, example="10.1.12.75", description="required in format of address"),
        'port_forwarding': Schema(type=TYPE_BOOLEAN, default=False),
        'destination_port_from': Schema(type=TYPE_STRING, example="80", description="required when selecting Port Forwarding"),
        'destination_port_to': Schema(type=TYPE_STRING, example="443", description="required when selecting Port Forwarding"),
        'destination_port': Schema(type=TYPE_STRING, example="5000", description="required when selecting Port Forwarding"),
        'description': Schema(type=TYPE_STRING, example="Description DNAT", description="description of DNAT rule"),
        }
        ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_dnat(request, id):
    """Updating a DNAT rule"""
    try:
        data = request.data
        # Apply correction for ipv4 addresses
        data["source_address"], data["external_address"], data["internal_address"] = fix_ipv4_address(
            [data["source_address"], data["external_address"], data["internal_address"]])
        
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
                # Get the rule handle of the next rule (by position)
                next_postrouting_handle = get_next_nat_handle(dnat, "prerouting")
                # Update the rule in system
                rule_number, rule_content = update_dnat_rule_in_system(
                    interface_ifname, source, destination, data["protocol"], dnat.rule_number, 
                    next_postrouting_handle)
                data["rule_number"] = int(rule_number)
                data["rule_content"] = rule_content

                serializer_dnat = DNatSerializer(dnat, data=data)
                if serializer_dnat.is_valid():

                    # Update the rule in the database
                    serializer_dnat.save()
                    return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)
            serializer_dnat.save()
            return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)
        
        return JsonResponse({"error": list(serializer_dnat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_DNAT_RULE}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO START A DNAT RULE",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_dnat(request, id):
    """Start a DNAT rule. Change rule_status to True to add the rule to the nft table"""
    try:
        dnat = DNat.objects.get(id=id)

        source, destination = input_create_dnat(dnat)

        # Add the rule in system
        # Find the next activated rule handle to insert the started rule above
        list_next_dnat = DNat.objects.filter(rule_status=True, db_position__gt=dnat.db_position)
        position_insert = -1
        if len(list_next_dnat) > 0:
            next_dnat = list_next_dnat.order_by('db_position')[0]
            position_insert = next_dnat.rule_number
        rule_number, _ = create_dnat_rule_in_system(
            dnat.interface.ifname, source, destination, dnat.protocol, position_insert)
        dnat.rule_number = int(rule_number)

        dnat.rule_status = True
        dnat.save()
        
        return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_STARTING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_DNAT_RULE}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO STOP A DNAT RULE",)
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
        dnat.prerouting_position = None
        dnat.save()
        
        return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_STOPING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_DNAT_RULE}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CHANGE POSITION OF A DNAT RULE",
    request_body=Schema(
        type=TYPE_OBJECT, required=["new_position"], properties={
            "new_position": Schema(type=TYPE_INTEGER, example="4", description="New position of DNAT rule after changing its position")}))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_dnat_position(request, id):
    """Change a rule position"""
    try:
        data = request.data
        new_position = data["new_position"]
        dnat = DNat.objects.get(id=id)
        change_rule_dnat_position_in_system(dnat, new_position)
        change_position_rule(dnat.pk, new_position, DNat)
        
        return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE_POSITION} {SUCCESS_MESSAGES_CHANGE}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CHANGING} {CONSTANT_DNAT_RULE_POSITION}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
