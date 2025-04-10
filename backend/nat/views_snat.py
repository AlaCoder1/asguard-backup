from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg.openapi import TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from backend.nat.models import OneToOneNat, SNat
from backend.nat.serializers import SNatSerializer
from backend.nat.utils import change_position_rule, get_next_nat_handle, input_create_snat, save_rules_positions
from backend.nat.list_nat import get_list_all_snat, get_one_snat
from backend.nat.utils_snat_system import change_rule_snat_position_in_system, create_snat_rule_in_system, delete_snat_rule_in_system, update_snat_rule_in_system
from backend.network.models import Interface
from utils.errors_utils import CommandExecutionError
from utils.utils_functions import fix_ipv4_address


# Constants
CONSTANT_SNAT_RULE = _("SNAT rule")
CONSTANT_SNAT_RULE_POSITION = _("SNAT rule position")
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


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN SNAT RULE", 
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'interface', 'source_address', 'source_port', 'destination_address',
            'destination_port', 'snat_type'],
        properties={
            'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface"),
            'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
            'protocol': Schema(type=TYPE_STRING, enum=["udp", "tcp"], description="required when choosing Static"),
            'source_address': Schema(type=TYPE_STRING, enum="10.1.12.0/24", description="format of address/mask or blank for Any"),
            'source_port': Schema(type=TYPE_STRING, enum="80"),
            'destination_address': Schema(type=TYPE_STRING, enum="192.168.30.0/24", description="format of address/mask or blank for Any"),
            'destination_port': Schema(type=TYPE_STRING, enum="443"),
            'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
            'translation_address_from': Schema(type=TYPE_STRING, enum="51.51.51.5", description="required when choosing Static, format of address like 51.32.100.5"),
            'translation_address_to': Schema(type=TYPE_STRING, enum="51.51.51.10", description="Optional when choosing Static, format of address like 51.32.100.10"),
            'translation_port': Schema(type=TYPE_STRING, enum="100", description="Optional when choosing Static"),
            'description': Schema(type=TYPE_STRING, enum="Description of SNAT", description="description of SNAT rule"),
            }
            ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_snat(request):
    """Creating a new SNAT rule and adding it to the database"""
    try:
        data = request.data
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        data["destination_address"] = fix_ipv4_address(data["destination_address"])

        serializer_snat = SNatSerializer(data=data)
        if serializer_snat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname

            # create the input for creating SNAT rule
            if data["snat_type"] == "MASQ":
                source, destination, masking = input_create_snat(
                    data["source_address"], data["source_port"], data["destination_address"], 
                    data["destination_port"], data["snat_type"])
            elif data["snat_type"] == "Static":
                source, destination, masking = input_create_snat(
                    data["source_address"], data["source_port"], data["destination_address"], 
                    data["destination_port"], data["snat_type"], data["translation_address_from"], 
                    data["translation_address_to"], data["translation_port"])
            else:
                return JsonResponse({"error": "Data error"}, status=400)

            # Add the rule in system and get the rule handle and content
            rule_number, rule_content = create_snat_rule_in_system(interface_ifname, source, destination, data["protocol"], masking)
            
            # Remove the new rule from the system if a similar rule already exists
            if len(SNat.objects.filter(rule_content=rule_content)) > 0:
                delete_snat_rule_in_system(rule_number)

            data["rule_number"] = int(rule_number)
            data["rule_content"] = rule_content

            data["db_position"] = 1
            for snat_rule in SNat.objects.all().order_by("-db_position"):
                snat_rule.db_position += 1
                snat_rule.save()

            serializer_snat = SNatSerializer(data=data)
            if serializer_snat.is_valid():

                # Add the rule to the database
                serializer_snat.save()
                return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_CREATING}"}, status=201)

        return JsonResponse({"error": list(serializer_snat.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_SNAT_RULE}"}, status=400)


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

            snat.delete()

            for snat_rule in SNat.objects.filter(db_position__gt=snat.db_position).order_by("db_position"):
                snat_rule.db_position -= 1
                snat_rule.save()
            return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

        # delete rule from database
        snat.delete()
        return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SNAT_RULE}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN SNAT RULE", 
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'interface', 'source_address', 'source_port', 'destination_address',
            'destination_port', 'snat_type'],
        properties={
            'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface"),
            'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
            'protocol': Schema(type=TYPE_STRING, enum=["udp", "tcp"], description="required when choosing Static"),
            'source_address': Schema(type=TYPE_STRING, enum="10.1.12.0/24", description="format of address/mask or blank for Any"),
            'source_port': Schema(type=TYPE_STRING, enum="80"),
            'destination_address': Schema(type=TYPE_STRING, enum="192.168.30.0/24", description="format of address/mask or blank for Any"),
            'destination_port': Schema(type=TYPE_STRING, enum="443"),
            'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
            'translation_address_from': Schema(type=TYPE_STRING, enum="51.51.51.5", description="required when choosing Static, format of address like 51.32.100.5"),
            'translation_address_to': Schema(type=TYPE_STRING, enum="51.51.51.10", description="Optional when choosing Static, format of address like 51.32.100.10"),
            'translation_port': Schema(type=TYPE_STRING, enum="100", description="Optional when choosing Static"),
            'description': Schema(type=TYPE_STRING, enum="Description of SNAT", description="description of SNAT rule"),
            }
            ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_snat(request, id):
    """Updating an SNAT rule"""
    try:
        data = request.data
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        data["destination_address"] = fix_ipv4_address(data["destination_address"])

        snat = SNat.objects.get(id=id)

        interface_ifname = Interface.objects.get(id=data["interface"]).ifname

        # create the input for creating SNAT rule
        if data["snat_type"] == "MASQ":
            source, destination, masking = input_create_snat(
                data["source_address"], data["source_port"], data["destination_address"], 
                data["destination_port"], data["snat_type"])
        elif data["snat_type"] == "Static":
            source, destination, masking = input_create_snat(
                data["source_address"], data["source_port"], data["destination_address"], 
                data["destination_port"], data["snat_type"], data["translation_address_from"], 
                data["translation_address_to"], data["translation_port"])
        else:
            return JsonResponse({"error": "Data error"}, status=400)
        
        if data["snat_type"] != "Static":
            snat.translation_address_from = None
            snat.translation_address_to = None
            snat.translation_port = None
        serializer_snat = SNatSerializer(snat, data=data)
        if serializer_snat.is_valid():

            if snat.rule_status:
                # Get the rule handle of the next rule (by position)
                next_postrouting_handle = get_next_nat_handle(snat)
                # Update the rule in system
                rule_number, rule_content = update_snat_rule_in_system(
                    interface_ifname, source, destination, data["protocol"], masking, snat.rule_number,
                    next_postrouting_handle)

                data["rule_number"] = int(rule_number)
                data["rule_content"] = rule_content

                serializer_snat = SNatSerializer(snat, data=data)
                if serializer_snat.is_valid():

                    # Update the rule in the database
                    serializer_snat.save()
                    return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)
                return JsonResponse({"error": list(serializer_snat.errors.values())[0][0]}, status=400)

            serializer_snat.save()
            return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

        return JsonResponse({"error": list(serializer_snat.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SNAT_RULE}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO START AN SNAT RULE",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_snat(request, id):
    """Start an SNAT rule. Change rule_status to True to add the rule to the nft table"""
    try:
        snat = SNat.objects.get(id=id)

        source, destination, masking = input_create_snat(
            snat.source_address, snat.source_port, 
            snat.destination_address, snat.destination_port,
            snat.snat_type, snat.translation_address_from, snat.translation_address_to, 
            snat.translation_port)

        # Add the rule in system
        # Find the next activated rule handle to insert the started rule above
        list_next_snat = SNat.objects.filter(rule_status=True, db_position__gt=snat.db_position)
        position_insert = -1
        if len(list_next_snat) > 0:
            next_snat = list_next_snat.order_by('db_position')[0]
            position_insert = next_snat.rule_number
        rule_number, _ = create_snat_rule_in_system(
            snat.interface.ifname, source, destination, snat.protocol, masking, position_insert)
        snat.rule_number = int(rule_number)

        snat.rule_status = True
        snat.save()

        return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_STARTING}"}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_SNAT_RULE}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO STOP AN SNAT RULE",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_snat(request, id):
    """Stop an SNAT rule. By changing rule_status to False, the while loop of the script will be breaked"""
    try:
        snat = SNat.objects.get(id=id)

        # Delete rule from system
        delete_snat_rule_in_system(snat.rule_number)

        # Update the rule fields by 
        snat.rule_status = False
        snat.rule_number = None
        snat.postrouting_position = None
        snat.save()

        return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_STOPING}"}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_SNAT_RULE}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CHANGE POSITION OF A SNAT RULE",
    request_body=Schema(
        type=TYPE_OBJECT, required=["new_position"], properties={
            "new_position": Schema(type=TYPE_INTEGER, example="4", description="New position of SNAT rule after changing its position")}))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_snat_position(request, id):
    """Change an snat rule position"""
    try:
        data = request.data
        new_position = data["new_position"]
        snat = SNat.objects.get(id=id)
        change_rule_snat_position_in_system(snat, new_position)
        rules_result = change_position_rule(snat.pk, new_position, SNat)
        save_rules_positions(rules_result, SNat)

        return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE_POSITION} {SUCCESS_MESSAGES_CHANGE}"}, status=201)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CHANGING} {CONSTANT_SNAT_RULE_POSITION}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
