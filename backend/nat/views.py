from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from .list_nat import get_list_all_dnat, get_list_all_one_to_one_nat, get_list_all_snat, get_one_dnat, get_one_one_to_one_nat, get_one_snat
from .models import DNat, OneToOneNat, SNat
from .serializers import DNatSerializer, OneToOneNatSerializer, SNatSerializer
from .utils import get_next_nat_handle, input_create_dnat, input_create_snat, update_position_nat
from .utils_dnat_system import create_dnat_rule_in_system, delete_dnat_rule_in_system, update_dnat_rule_in_system
from .utils_one_to_one_nat_system import create_one_to_one_nat_rule_in_system, delete_one_to_one_nat_rule_in_system, update_one_to_one_nat_rule_in_system
from .utils_snat_system import create_snat_rule_in_system, delete_snat_rule_in_system, update_snat_rule_in_system

from backend.network.models import Interface
from utils.errors_utils import CommandExecutionError
from utils.utils_functions import fix_ipv4_address


# Constants
CONSTANT_SNAT_RULE = _("SNAT rule")
CONSTANT_ONE_TO_ONE_NAT_RULE = _("OneToOneNat rule")
CONSTANT_DNAT_RULE = _("DNAT rule")
CONSTANT_SNAT_RULE_POSITION = _("SNAT rule position")
CONSTANT_ONE_TO_ONE_NAT_RULE_POSITION = _("OneToOneNat rule position")
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
ERROR_MESSAGES_DELETING_USED_ITEM = _("Unable to delete")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


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
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'source_port', 'destination_address', 
                                                     'destination_port', 'snat_type'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
                                     'protocol': Schema(type=TYPE_STRING, description="required when choosing Static"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'source_port': Schema(type=TYPE_STRING),
                                     'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'destination_port': Schema(type=TYPE_STRING),
                                     'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
                                     'translation_address_from': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.5"),
                                     'translation_address_to': Schema(type=TYPE_STRING, description="Optional when choosing Static, format of address like 51.32.100.10"),
                                     'translation_port': Schema(type=TYPE_STRING, description="Optional when choosing Static"),
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
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        data["destination_address"] = fix_ipv4_address(data["destination_address"])
        
        serializer_snat = SNatSerializer(data=data)
        if serializer_snat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname
            
            source = {"address": data["source_address"],
                      "port": data["source_port"]}
            destination = {"address": data["destination_address"],
                           "port": data["destination_port"]}
            
            masking = ["masquerade"]
            if data["snat_type"] == "Static":
                masking = data["translation_address_from"]
                if data["translation_address_to"] != "":
                    masking += f"""-{data["translation_address_to"]}"""
                if data["translation_port"] != "":
                    masking += f""":{data["translation_port"]}"""
                masking = ["snat", "ip", "to",  masking]

            # Add the rule in system
            rule_number, rule_content = create_snat_rule_in_system(interface_ifname, source, destination, data["protocol"], masking)
            data["rule_number"] = int(rule_number)
            data["rule_content"] = rule_content

            data["snat_position"] = 1
            for snat_rule in SNat.objects.all().order_by("-snat_position"):
                snat_rule.snat_position += 1
                snat_rule.save()

            serializer_snat = SNatSerializer(data=data)
            if serializer_snat.is_valid():

                # Add the rule to the database
                serializer_snat.save()
                update_position_nat()
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
            
            for snat_rule in SNat.objects.filter(snat_position__gt=snat.snat_position).order_by("snat_position"):
                snat_rule.snat_position -= 1
                snat_rule.save()
            return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

        # delete rule from database
        snat.delete()
        update_position_nat()
        return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SNAT_RULE}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UPDATE AN SNAT RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface', 'source_address', 'source_port', 'destination_address', 
                                                     'destination_port', 'snat_type'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
                                     'protocol': Schema(type=TYPE_STRING, description="required when choosing Static"),
                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'source_port': Schema(type=TYPE_STRING),
                                     'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'destination_port': Schema(type=TYPE_STRING),
                                     'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
                                     'translation_address_from': Schema(type=TYPE_STRING, description="required when choosing Static, format of address like 51.32.100.5"),
                                     'translation_address_to': Schema(type=TYPE_STRING, description="Optional when choosing Static, format of address like 51.32.100.10"),
                                     'translation_port': Schema(type=TYPE_STRING, description="Optional when choosing Static"),
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
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        data["destination_address"] = fix_ipv4_address(data["destination_address"])

        snat = SNat.objects.get(id=id)

        interface_ifname = Interface.objects.get(id=data["interface"]).ifname

        source = {"address": data["source_address"],
                  "port": data["source_port"]}
        destination = {"address": data["destination_address"],
                       "port": data["destination_port"]}
        masking = ["masquerade"]
        if data["snat_type"] == "Static":
            masking = data["translation_address_from"]
            if data["translation_address_to"] != "":
                masking += f"""-{data["translation_address_to"]}"""
            if data["translation_port"] != "":
                masking += f""":{data["translation_port"]}"""
            masking = ["snat", "ip", "to",  masking]
        else:
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
                    next_postrouting_handle, snat.postrouting_position-1)

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

        source, destination, masking = input_create_snat(snat)

        # Add the rule in system
        # Find the next activated rule handle to insert the started rule above
        list_next_snat = SNat.objects.filter(rule_status=True, snat_position__gt=snat.snat_position)
        position_insert = 0
        postrouting_position = 0
        if len(list_next_snat) > 0:
            next_snat = list_next_snat.order_by('snat_position')[0]
            postrouting_position = next_snat.postrouting_position - 1
            position_insert = next_snat.rule_number
        rule_number, _ = create_snat_rule_in_system(
            snat.interface.ifname, source, destination, snat.protocol, masking, position_insert, 
            postrouting_position)
        snat.rule_number = int(rule_number)

        snat.rule_status = True
        snat.save()
        update_position_nat()
        
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
        update_position_nat()
        
        return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE} {SUCCESS_MESSAGES_STOPING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_SNAT_RULE}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CHANGE POSITION OF AN SNAT RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=["new_position"],
                         properties={'new_position': Schema(type=TYPE_INTEGER)}
                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_snat_position(request, id):
    """Change an snat rule position"""
    try:
        data = request.data
        new_position = data["new_position"]
        snat = SNat.objects.get(id=id)
        previous_position = snat.snat_position
        
        # Up or down the rule position
        up_position = True
        # Inputs for changing position of the rule to UP
        # Get list of SNAT between previous and new position (DESC order).
        list_snat_in_interval = SNat.objects.filter(snat_position__gte=new_position, 
                                                    snat_position__lt=snat.snat_position).order_by("-snat_position")
        # Get list of activated SNAT between previous and new position.
        list_active_snat_in_interval = SNat.objects.filter(rule_status=True, 
                                                           snat_position__gte=new_position,
                                                           snat_position__lt=snat.snat_position)
        # Position offset
        position_offset = 1
        
        if new_position > previous_position:
            # Inputs for changing position of the rule to DOWN
            up_position = False
            # Get list of SNAT between previous and new position (ASC order).
            list_snat_in_interval = SNat.objects.filter(snat_position__gt=snat.snat_position, 
                                                        snat_position__lte=new_position).order_by("snat_position")
            # Get list of activated SNAT between previous and new position.
            list_active_snat_in_interval = SNat.objects.filter(rule_status=True, 
                                                               snat_position__gt=snat.snat_position,
                                                               snat_position__lte=new_position)
            # Position offset
            position_offset = -1
        
        # Change position in system if the rule is activated and there is at least one activated rule in this interval
        if snat.rule_status and len(list_active_snat_in_interval) > 0:
            source, destination, masking = input_create_snat(snat)
            
            if up_position:
                next_snat = list_active_snat_in_interval.order_by("snat_position")[0]
                delete_snat_rule_in_system(snat.rule_number)
                rule_number, _ = create_snat_rule_in_system(
                    snat.interface.ifname, source, destination, snat.protocol, masking, 
                    next_snat.rule_number, next_snat.postrouting_position-1)
            else:
                list_next_snat = SNat.objects.filter(rule_status=True, snat_position__gt=new_position)
                if len(list_next_snat) > 0:
                    next_snat = list_next_snat.order_by("snat_position")[0]
                    delete_snat_rule_in_system(snat.rule_number)
                    rule_number, _ = create_snat_rule_in_system(
                        snat.interface.ifname, source, destination, snat.protocol, masking, 
                        next_snat.rule_number, next_snat.postrouting_position-2)
                else:
                    new_position_in_system = len(SNat.objects.filter(rule_status=True)) + len(OneToOneNat.objects.filter(rule_status=True)) - 1
                    delete_snat_rule_in_system(snat.rule_number)
                    rule_number, _ = create_snat_rule_in_system(
                        snat.interface.ifname, source, destination, snat.protocol, masking, -1, 
                        new_position_in_system)
            snat.rule_number = int(rule_number)
            snat.save()
        
        # Update snat_position
        snat.snat_position = None
        snat.save()
        for snat_rule in list_snat_in_interval:
            snat_rule.snat_position += position_offset
            snat_rule.save()
        snat.snat_position = new_position
        snat.save()
        update_position_nat()
        
        return JsonResponse({"msg": f"{CONSTANT_SNAT_RULE_POSITION} {SUCCESS_MESSAGES_CHANGE}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CHANGING} {CONSTANT_SNAT_RULE_POSITION}"}, status=400)
    except SNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


########################################
############ OneToOne NAT ##############
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
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        data["translation_address"] = fix_ipv4_address(data["translation_address"])
        data["destination_address"] = fix_ipv4_address(data["destination_address"])
        
        serializer_one_to_one_nat = OneToOneNatSerializer(data=data)
        if serializer_one_to_one_nat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname
            
            destination = "any"
            if data["destination_address"] != "":
                destination = data["destination_address"]
            
            # Add the rule in system
            rule_number, rule_content = create_one_to_one_nat_rule_in_system(
                interface_ifname, data["source_address"], destination, data["translation_address"])
            data["rule_number"] = int(rule_number)
            data["rule_content"] = rule_content

            data["one_to_one_nat_position"] = 1
            for one_to_one_nat_rule in OneToOneNat.objects.all().order_by("-one_to_one_nat_position"):
                one_to_one_nat_rule.one_to_one_nat_position += 1
                one_to_one_nat_rule.save()

            serializer_one_to_one_nat = OneToOneNatSerializer(data=data)
            if serializer_one_to_one_nat.is_valid():

                # Add the rule to the database
                serializer_one_to_one_nat.save()
                update_position_nat()
                return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_CREATING}"}, status=201)

        return JsonResponse({"error": list(serializer_one_to_one_nat.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)


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
            one_to_one_nat.delete()
            
            for one_to_one_nat_rule in OneToOneNat.objects.filter(one_to_one_nat_position__gt=one_to_one_nat.one_to_one_nat_position).order_by("one_to_one_nat_position"):
                one_to_one_nat_rule.one_to_one_nat_position -= 1
                one_to_one_nat_rule.save()
            return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

        # delete rule from database
        one_to_one_nat.delete()
        update_position_nat()
        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


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
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        data["translation_address"] = fix_ipv4_address(data["translation_address"])
        data["destination_address"] = fix_ipv4_address(data["destination_address"])
        
        one_to_one_nat = OneToOneNat.objects.get(id=id)
        
        serializer_one_to_one_nat = OneToOneNatSerializer(one_to_one_nat, data=data)
        if serializer_one_to_one_nat.is_valid():

            interface_ifname = Interface.objects.get(id=data["interface"]).ifname
            
            destination = "any"
            if data["destination_address"] != "":
                destination = data["destination_address"]
            
            # update the rule in system if the rule was started
            if one_to_one_nat.rule_status:
                # Get the rule handle of the next rule (by position)
                next_postrouting_handle = get_next_nat_handle(one_to_one_nat)
                rule_number = update_one_to_one_nat_rule_in_system(interface_ifname, data["source_address"], destination, 
                                                                   data["translation_address"], one_to_one_nat.rule_number, 
                                                                   next_postrouting_handle, one_to_one_nat.postrouting_position-1)
                data["rule_number"] = int(rule_number)

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


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO START A ONE TO ONE NAT RULE",)
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
        # Find the next activated rule handle to insert the started rule above
        list_next_one_to_one_nat = OneToOneNat.objects.filter(rule_status=True, 
                                                              one_to_one_nat_position__gt=one_to_one_nat.one_to_one_nat_position)
        position_insert = 0
        postrouting_position = 0
        if len(list_next_one_to_one_nat) > 0:
            next_one_to_one_nat = list_next_one_to_one_nat.order_by('one_to_one_nat_position')[0]
            postrouting_position = next_one_to_one_nat.postrouting_position - 1
            position_insert = next_one_to_one_nat.rule_number
        rule_number, _ = create_one_to_one_nat_rule_in_system(
            one_to_one_nat.interface.ifname, one_to_one_nat.source_address, destination,
            one_to_one_nat.translation_address, position_insert, postrouting_position)
        one_to_one_nat.rule_number = int(rule_number)

        one_to_one_nat.rule_status = True
        one_to_one_nat.save()
        update_position_nat()
        
        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_STARTING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO STOP A ONE TO ONE NAT RULE",)
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
        one_to_one_nat.postrouting_position = None
        one_to_one_nat.save()
        update_position_nat()
        
        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {SUCCESS_MESSAGES_STOPING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_ONE_TO_ONE_NAT_RULE}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CHANGE POSITION OF A OneToOneNAT RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=["new_position"],
                         properties={'new_position': Schema(type=TYPE_INTEGER)}))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_one_to_one_nat_position(request, id):
    """Change a rule position"""
    try:
        data = request.data
        new_position = data["new_position"]
        one_to_one_nat = OneToOneNat.objects.get(id=id)
        previous_position = one_to_one_nat.one_to_one_nat_position
        
        # Up or down the rule position
        up_position = True
        # Inputs for changing position of the rule to UP
        # Get list of OneToOneNat between previous and new position (DESC order).
        list_one_to_one_nat_in_interval = OneToOneNat.objects.filter(
            one_to_one_nat_position__gte=new_position, 
            one_to_one_nat_position__lt=one_to_one_nat.one_to_one_nat_position).order_by("-one_to_one_nat_position")
        # Get list of activated OneToOneNat between previous and new position.
        list_active_one_to_one_nat_in_interval = OneToOneNat.objects.filter(
            rule_status=True, one_to_one_nat_position__gte=new_position,
            one_to_one_nat_position__lt=one_to_one_nat.one_to_one_nat_position)
        # Position offset
        position_offset = 1
        
        if new_position > previous_position:
            # Inputs for changing position of the rule to DOWN
            up_position = False
            # Get list of OneToOneNat between previous and new position (ASC order).
            list_one_to_one_nat_in_interval = OneToOneNat.objects.filter(
                one_to_one_nat_position__gt=one_to_one_nat.one_to_one_nat_position,
                one_to_one_nat_position__lte=new_position).order_by("one_to_one_nat_position")
            # Get list of activated OneToOneNat between previous and new position.
            list_active_one_to_one_nat_in_interval = OneToOneNat.objects.filter(
                rule_status=True, one_to_one_nat_position__gt=one_to_one_nat.one_to_one_nat_position,
                one_to_one_nat_position__lte=new_position)
            # Position offset
            position_offset = -1
        
        # Change position in system if the rule is activated and there is at least one activated rule in this interval
        if one_to_one_nat.rule_status and len(list_active_one_to_one_nat_in_interval) > 0:
            
            destination = "any"
            if one_to_one_nat.destination_address != "":
                destination = one_to_one_nat.destination_address
            
            if up_position:
                next_one_to_one_nat = list_active_one_to_one_nat_in_interval.order_by("one_to_one_nat_position")[0]
                delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
                rule_number, _ = create_one_to_one_nat_rule_in_system(
                    one_to_one_nat.interface.ifname, one_to_one_nat.source_address, destination, 
                    one_to_one_nat.translation_address, next_one_to_one_nat.rule_number, 
                    next_one_to_one_nat.postrouting_position-1)
            else:
                list_next_one_to_one_nat = OneToOneNat.objects.filter(rule_status=True, one_to_one_nat_position__gt=new_position)
                if len(list_next_one_to_one_nat) > 0:
                    next_one_to_one_nat = list_next_one_to_one_nat.order_by("one_to_one_nat_position")[0]
                    delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
                    rule_number, _ = create_one_to_one_nat_rule_in_system(
                        one_to_one_nat.interface.ifname, one_to_one_nat.source_address, destination, 
                        one_to_one_nat.translation_address, next_one_to_one_nat.rule_number, 
                        next_one_to_one_nat.postrouting_position-2)
                else:
                    new_position_in_system = len(SNat.objects.filter(rule_status=True)) + len(OneToOneNat.objects.filter(rule_status=True)) - 1
                    delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
                    rule_number, _ = create_one_to_one_nat_rule_in_system(
                        one_to_one_nat.interface.ifname, one_to_one_nat.source_address, destination, 
                        one_to_one_nat.translation_address, -1, new_position_in_system)
            one_to_one_nat.rule_number = int(rule_number)
            one_to_one_nat.save()
        
        # Update one_to_one_nat_position
        one_to_one_nat.one_to_one_nat_position = None
        one_to_one_nat.save()
        for one_to_one_nat_rule in list_one_to_one_nat_in_interval:
            one_to_one_nat_rule.one_to_one_nat_position += position_offset
            one_to_one_nat_rule.save()
        one_to_one_nat.one_to_one_nat_position = new_position
        one_to_one_nat.save()
        update_position_nat()
        
        return JsonResponse({"msg": f"{CONSTANT_ONE_TO_ONE_NAT_RULE_POSITION} {SUCCESS_MESSAGES_CHANGE}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CHANGING} {CONSTANT_ONE_TO_ONE_NAT_RULE_POSITION}"}, status=400)
    except OneToOneNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ONE_TO_ONE_NAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


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
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        
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

            data["dnat_position"] = 1
            for dnat_rule in DNat.objects.all().order_by("-dnat_position"):
                dnat_rule.dnat_position += 1
                dnat_rule.save()

            serializer_dnat = DNatSerializer(data=data)
            if serializer_dnat.is_valid():

                # Add the rule to the database
                serializer_dnat.save()
                update_position_nat("prerouting")
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
            
            for dnat_rule in DNat.objects.filter(dnat_position__gt=dnat.dnat_position).order_by("dnat_position"):
                dnat_rule.dnat_position -= 1
                dnat_rule.save()
            return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)

        # delete rule from database
        dnat.delete()
        update_position_nat("prerouting")
        return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_DNAT_RULE}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UPDATE A DNAT RULE", request_body=Schema(
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
        # Apply correction for ipv4 addresses
        data["source_address"] = fix_ipv4_address(data["source_address"])
        
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
                    next_postrouting_handle, dnat.prerouting_position-1)
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
        list_next_dnat = DNat.objects.filter(rule_status=True, dnat_position__gt=dnat.dnat_position)
        position_insert = 0
        prerouting_position = 0
        if len(list_next_dnat) > 0:
            next_dnat = list_next_dnat.order_by('dnat_position')[0]
            prerouting_position = next_dnat.prerouting_position - 1
            position_insert = next_dnat.rule_number
        rule_number, _ = create_dnat_rule_in_system(
            dnat.interface.ifname, source, destination, dnat.protocol, position_insert, 
            prerouting_position)
        dnat.rule_number = int(rule_number)

        dnat.rule_status = True
        dnat.save()
        update_position_nat("prerouting")
        
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
        update_position_nat("prerouting")
        
        return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE} {SUCCESS_MESSAGES_STOPING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_DNAT_RULE}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CHANGE POSITION OF A DNAT RULE",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_dnat_position(request, id):
    """Change a rule position"""
    try:
        data = request.data
        new_position = data["new_position"]
        dnat = DNat.objects.get(id=id)
        previous_position = dnat.dnat_position
        
        # Up or down the rule position
        up_position = True
        # Inputs for changing position of the rule to UP
        # Get list of DNAT between previous and new position (DESC order).
        list_dnat_in_interval = DNat.objects.filter(dnat_position__gte=new_position, 
                                                    dnat_position__lt=dnat.dnat_position).order_by("-dnat_position")
        # Get list of activated DNAT between previous and new position.
        list_active_dnat_in_interval = DNat.objects.filter(rule_status=True, dnat_position__gte=new_position,
                                                           dnat_position__lt=dnat.dnat_position)
        # Position offset
        position_offset = 1
        
        if new_position > previous_position:
            # Inputs for changing position of the rule to DOWN
            up_position = False
            # Get list of DNAT between previous and new position (ASC order).
            list_dnat_in_interval = DNat.objects.filter(dnat_position__gt=dnat.dnat_position, 
                                                        dnat_position__lte=new_position).order_by("dnat_position")
            # Get list of activated DNAT between previous and new position.
            list_active_dnat_in_interval = DNat.objects.filter(rule_status=True, dnat_position__gt=dnat.dnat_position,
                                                               dnat_position__lte=new_position)
            # Position offset
            position_offset = -1
        
        # Change position in system if the rule is activated and there is at least one activated rule in this interval
        if dnat.rule_status and len(list_active_dnat_in_interval) > 0:

            source, destination = input_create_dnat(dnat)
            
            if up_position:
                next_dnat = list_active_dnat_in_interval.order_by("dnat_position")[0]
                delete_dnat_rule_in_system(dnat.rule_number)
                rule_number, _ = create_dnat_rule_in_system(
                    dnat.interface.ifname, source, destination, dnat.protocol, next_dnat.rule_number, 
                    next_dnat.prerouting_position-1)
            else:
                list_next_dnat = DNat.objects.filter(rule_status=True, dnat_position__gt=new_position)
                if len(list_next_dnat) > 0:
                    next_dnat = list_next_dnat.order_by("dnat_position")[0]
                    delete_dnat_rule_in_system(dnat.rule_number)
                    rule_number, _ = create_dnat_rule_in_system(
                        dnat.interface.ifname, source, destination, dnat.protocol, next_dnat.rule_number, 
                        next_dnat.prerouting_position-2)
                else:
                    new_position_in_system = len(DNat.objects.filter(rule_status=True)) - 1
                    delete_dnat_rule_in_system(dnat.rule_number)
                    rule_number, _ = create_dnat_rule_in_system(
                        dnat.interface.ifname, source, destination, dnat.protocol, -1, 
                        new_position_in_system)
            dnat.rule_number = int(rule_number)
            dnat.save()
        
        # Update dnat_position
        dnat.dnat_position = None
        dnat.save()
        for dnat_rule in list_dnat_in_interval:
            dnat_rule.dnat_position += position_offset
            dnat_rule.save()
        dnat.dnat_position = new_position
        dnat.save()
        update_position_nat("prerouting")
        
        return JsonResponse({"msg": f"{CONSTANT_DNAT_RULE_POSITION} {SUCCESS_MESSAGES_CHANGE}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CHANGING} {CONSTANT_DNAT_RULE_POSITION}"}, status=400)
    except DNat.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_DNAT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
