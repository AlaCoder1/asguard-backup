from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from drf_yasg.openapi import Parameter, IN_PATH, TYPE_ARRAY, TYPE_INTEGER, TYPE_OBJECT, Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from backend.nat.contant_variables import REQUEST_BODY_ONE_TO_ONE_NAT
from backend.nat.models import OneToOneNat
from backend.nat.serializers import OneToOneNatSerializer
from backend.nat.utils import change_position_rule, get_next_nat_handle
from backend.nat.list_nat import get_list_all_one_to_one_nat, get_one_one_to_one_nat
from backend.nat.utils_one_to_one_nat import check_payload, input_create_one_to_one_nat
from backend.nat.utils_one_to_one_nat_system import change_rule_one_to_one_nat_position_in_system, create_one_to_one_nat_rule_in_system, delete_one_to_one_nat_rule_in_system, update_one_to_one_nat_rule_in_system
from backend.network.models import Interface
from utils.errors_utils import CommandExecutionError
from utils.utils_address import fix_ipv4_address


# Constants
CONSTANT_ONE_TO_ONE_NAT_RULE = _("OneToOneNat rule")
CONSTANT_ONE_TO_ONE_NAT_RULE_POSITION = _("OneToOneNat rule position")
CONSTANT_INTERFACE = _("interface")
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
ERROR_MESSAGES_INVALID_DATA = _("Invalid data")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL OneToOneNat RULES",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_one_to_one_nat(_):
    """Getting all one_to_one_nat from database"""
    list_one_to_one_nat = []
    list_one_to_one_nat = get_list_all_one_to_one_nat()
    return JsonResponse(list_one_to_one_nat, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO GET AN OneToOneNat RULE",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_one_to_one_nat(_, id):
    """Getting one_to_one_nat by id from database"""
    one_to_one_nat = get_one_one_to_one_nat(id)
    return JsonResponse(one_to_one_nat, safe=False)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A OneToOneNat RULE", 
    request_body=REQUEST_BODY_ONE_TO_ONE_NAT)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_one_to_one_nat(request):
    """Creating a new OneToOneNat rule and adding it to the database"""
    try:
        data = request.data
        # Check data validity
        if not check_payload(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        # Apply correction for ipv4 addresses
        data["source_address"], data["destination_address"], data["translation_address"] = fix_ipv4_address(
            [data["source_address"], data["destination_address"], data["translation_address"]])

        serializer_one_to_one_nat = OneToOneNatSerializer(data=data)
        if serializer_one_to_one_nat.is_valid():
            interface_ifname = None
            if data["interface"]:
                interface_ifname = Interface.objects.get(id=data["interface"]).ifname

            destination = input_create_one_to_one_nat(data["destination_address"])

            # Add the rule in system
            rule_number, rule_content = create_one_to_one_nat_rule_in_system(
                interface_ifname, data["source_address"], destination, data["translation_address"])
            data["rule_number"] = int(rule_number)
            data["rule_content"] = rule_content

            data["db_position"] = 1
            for one_to_one_nat_rule in OneToOneNat.objects.all().order_by("-db_position"):
                one_to_one_nat_rule.db_position += 1
                one_to_one_nat_rule.save()

            serializer_one_to_one_nat = OneToOneNatSerializer(data=data)
            if serializer_one_to_one_nat.is_valid():

                # Add the rule to the database
                serializer_one_to_one_nat.save()
                return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_CREATING}"}, status=201)

        return JsonResponse({"error": list(serializer_one_to_one_nat.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'},
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO DELETE AN OneToOneNat RULE",)
@api_view(['Delete'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_one_to_one_nat(request, id):
    """Deleting an one_to_one_nat from database"""
    try:
        one_to_one_nat = OneToOneNat.objects.get(id=id)

        if one_to_one_nat.rule_status:
            # Delete rule from system
            delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
            one_to_one_nat.delete()

            for one_to_one_nat_rule in OneToOneNat.objects.filter(db_position__gt=one_to_one_nat.db_position).order_by("db_position"):
                one_to_one_nat_rule.db_position -= 1
                one_to_one_nat_rule.save()
            return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

        # delete rule from database
        one_to_one_nat.delete()
        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO DELETE A LIST OF OneToOneNAT RULE AND RETURN A LIST OF RESPONSES FOR EACH OneToOneNAT",
    request_body=Schema(
        type=TYPE_OBJECT, required=['list_rules'],
        properties={
            'list_rules': Schema(type=TYPE_ARRAY, description="Set the OneToOneNAT rule list of IDs",
                                items=Schema(type=TYPE_INTEGER, example=1)),
            }))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_list_one_to_one_nat(request):
    """Deleting a list of one_to_one_nat rules"""
    data = request.data
    list_id_one_to_one_nat = data.get("list_rules")
    list_responses = []
    for id_one_to_one_nat in list_id_one_to_one_nat:
        try:
            one_to_one_nat = OneToOneNat.objects.get(id=id_one_to_one_nat)

            if one_to_one_nat.rule_status:
                # Delete rule from system
                delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)

                one_to_one_nat.delete()

                for one_to_one_nat_rule in OneToOneNat.objects.filter(db_position__gt=one_to_one_nat.db_position).order_by("db_position"):
                    one_to_one_nat_rule.db_position -= 1
                    one_to_one_nat_rule.save()
            
            else:
                # delete rule from database
                one_to_one_nat.delete()
            list_responses.append({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_DELETING}", "status": 200})

        except CommandExecutionError:
            list_responses.append({"msg": f"{ERROR_MESSAGES_DELETING} {CONSTANT_ONE_TO_ONE_NAT_RULE}", "status": 400})
        except OneToOneNat.DoesNotExist:
            list_responses.append({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}", "status": 404})
    return JsonResponse(list_responses, safe=False)

@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'},
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    operation_summary="API TO CREATE A OneToOneNat RULE", 
    request_body=REQUEST_BODY_ONE_TO_ONE_NAT)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_one_to_one_nat(request, id):
    """Updating an OneToOneNat rule"""
    try:
        data = request.data
        # Check data validity
        if not check_payload(data):
            return JsonResponse({"error": ERROR_MESSAGES_INVALID_DATA}, status=400)
        # Apply correction for ipv4 addresses
        data["source_address"], data["destination_address"], data["translation_address"] = fix_ipv4_address(
            [data["source_address"], data["destination_address"], data["translation_address"]])

        one_to_one_nat = OneToOneNat.objects.get(id=id)

        serializer_one_to_one_nat = OneToOneNatSerializer(one_to_one_nat, data=data)
        if serializer_one_to_one_nat.is_valid():

            interface_ifname = None
            if data["interface"]:
                interface_ifname = Interface.objects.get(id=data["interface"]).ifname

            destination = "any"
            if data["destination_address"] != "":
                destination = data["destination_address"]

            # update the rule in system if the rule was started
            if one_to_one_nat.rule_status:
                # Get the rule handle of the next rule (by position)
                next_postrouting_handle = get_next_nat_handle(one_to_one_nat)
                rule_number, rule_content = update_one_to_one_nat_rule_in_system(
                    interface_ifname, data["source_address"], destination, data["translation_address"], 
                    one_to_one_nat.rule_number, next_postrouting_handle)
                data["rule_number"] = int(rule_number)
                data["rule_content"] = rule_content

                serializer_one_to_one_nat = OneToOneNatSerializer(one_to_one_nat, data=data)
                if serializer_one_to_one_nat.is_valid():

                    # Add the rule to the database
                    serializer_one_to_one_nat.save()
                    return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)
                return JsonResponse({"error": list(serializer_one_to_one_nat.errors.values())[0][0]}, status=400)

            serializer_one_to_one_nat.save()
            return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

        return JsonResponse({"error": list(serializer_one_to_one_nat.errors.values())[0][0]}, status=400)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'},
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO START A ONE TO ONE NAT RULE",)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_one_to_one_nat(_, id):
    """Start a OneToOneNat rule"""
    try:
        one_to_one_nat = OneToOneNat.objects.get(id=id)
        if not one_to_one_nat.rule_status:
            destination = input_create_one_to_one_nat(one_to_one_nat.destination_address)

            # Add the rule in system
            # Find the next activated rule handle to insert the started rule above
            list_next_one_to_one_nat = OneToOneNat.objects.filter(rule_status=True,
                                                                db_position__gt=one_to_one_nat.db_position)
            position_insert = 0
            if len(list_next_one_to_one_nat) > 0:
                next_one_to_one_nat = list_next_one_to_one_nat.order_by('db_position')[0]
                position_insert = next_one_to_one_nat.rule_number
            interface_name = None
            if one_to_one_nat.interface:
                interface_name = one_to_one_nat.interface.ifname
            rule_number, _ = create_one_to_one_nat_rule_in_system(
                interface_name, one_to_one_nat.source_address, destination,
                one_to_one_nat.translation_address, position_insert)
            one_to_one_nat.rule_number = int(rule_number)

            one_to_one_nat.rule_status = True
            one_to_one_nat.save()

        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_STARTING}"}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'},
                     manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
                     operation_summary="API TO STOP A ONE TO ONE NAT RULE",)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_one_to_one_nat(_, id):
    """Stop a OneToOneNat rule"""
    try:
        one_to_one_nat = OneToOneNat.objects.get(id=id)
        if one_to_one_nat.rule_status:
            # Delete rule from system
            try:
                delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
            except CommandExecutionError:
                pass

            one_to_one_nat.rule_status = False
            one_to_one_nat.rule_number = None
            one_to_one_nat.postrouting_position = None
            one_to_one_nat.save()

        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_STOPING}"}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    manual_parameters=[Parameter('id', IN_PATH, type=TYPE_INTEGER, required=True)],
    operation_summary="API TO CHANGE POSITION OF A One To One NAT RULE",
    request_body=Schema(
        type=TYPE_OBJECT, required=["new_position"], properties={
            "new_position": Schema(type=TYPE_INTEGER, example="4", description="New position of One To One NAT rule after changing its position")}))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_one_to_one_nat_position(request, id):
    """Change a rule position"""
    try:
        data = request.data
        new_position = data["new_position"]
        one_to_one_nat = OneToOneNat.objects.get(id=id)
        change_rule_one_to_one_nat_position_in_system(one_to_one_nat, new_position)
        change_position_rule(one_to_one_nat.pk, new_position, OneToOneNat)

        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE_POSITION} {SUCCESS_MESSAGES_CHANGE}"}, status=201)

    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CHANGING} {CONSTANT_ONE_TO_ONE_NAT_RULE_POSITION}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
