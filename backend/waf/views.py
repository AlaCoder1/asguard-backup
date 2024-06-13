from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from backend.waf.list_waf import get_list_all_waf_rule, get_list_all_waf_application, get_one_waf_rule, get_one_waf_application, get_one_waf_config
from backend.waf.models import ApplicationWaf, ConfigWaf, RulesWaf
from backend.waf.serializers import ApplicationWafSerializer, ConfigWafSerializer, RulesWafSerializer
from backend.waf.utils import convert_waf_rule_payload, find_possible_id
from backend.waf.utils_application import create_application_waf_in_system, delete_application_waf_in_system, update_application_waf_in_system
from backend.waf.utils_config import change_waf_config_file
from backend.waf.utils_rules import create_rule_waf_in_system, create_rule_waf_str, delete_rule_waf_in_system, update_rule_waf_in_system
from utils.errors_utils import CommandExecutionError


# Constants
CONSTANT_WAF_CONFIG = _("WAF Config")
CONSTANT_WAF_RULE = _("WAF Rule")
CONSTANT_WAF_APPLICATION = _("WAF Application")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("Error in creating")
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


########################################
########## WAF Configuration ###########
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET THE WAF CONFIG",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_waf_config(request):
    """Getting WAF Config from database"""
    waf_config = get_one_waf_config()
    return JsonResponse(waf_config, safe=False)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UPDATE THE WAF CONFIG", 
                     request_body=Schema(
                         type=TYPE_OBJECT,
                         required=["rule_engine_initialization", "access_request_bodies", "xml_request_body_parser", 
                                   "json_request_body_parser", "maximum_request_body_size", "request_body_size_files_excluded",
                                   "request_body_limit_action", "maximum_parsing_depth_json", "maximum_number_args_request", 
                                   "pcre_match_limit", "pcre_match_limit_recursion", "response_body_access", 
                                   "response_body_mimetype", "response_body_limit", "response_body_limit_action"],
                         properties={'rule_engine_initialization': Schema(type=TYPE_STRING, enum=["On", "Off", "Detection only"]),
                                     'access_request_bodies':Schema(type=TYPE_BOOLEAN),
                                     'xml_request_body_parser':Schema(type=TYPE_BOOLEAN),
                                     'json_request_body_parser':Schema(type=TYPE_BOOLEAN),
                                     'maximum_request_body_size': Schema(type=TYPE_INTEGER),
                                     'request_body_size_files_excluded': Schema(type=TYPE_INTEGER),
                                     'request_body_limit_action': Schema(type=TYPE_STRING, enum=["Accept", "Reject"]),
                                     'maximum_parsing_depth_json': Schema(type=TYPE_INTEGER),
                                     'maximum_number_args_request': Schema(type=TYPE_INTEGER),
                                     'pcre_match_limit': Schema(type=TYPE_INTEGER),
                                     'pcre_match_limit_recursion': Schema(type=TYPE_INTEGER),
                                     'response_body_access':Schema(type=TYPE_BOOLEAN),
                                     'response_body_mimetype': Schema(type=TYPE_STRING, enum=["text/html", "text/xml", "text/plain", "text/*"]),
                                     'response_body_limit': Schema(type=TYPE_INTEGER),
                                     'response_body_limit_action': Schema(type=TYPE_STRING, enum=["ProcessPartial", "Reject", "log", "log allow", "pass"]),
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_config_waf(request, id):
    """Updating WAF Configuration"""
    try:
        data = request.data
        config_waf = ConfigWaf.objects.get(id=id)
        change_waf_config_file(data)
        config_waf_serializer = ConfigWafSerializer(config_waf, data=data)
        if config_waf_serializer.is_valid():
            config_waf_serializer.save()
            return JsonResponse({"msg": f"{CONSTANT_WAF_CONFIG} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
        return JsonResponse({"error": list(config_waf_serializer.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_WAF_CONFIG}"}, status=400)


########################################
############## WAF Rules ###############
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL WAF RULES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_waf_rule(request):
    """Getting all WAF Rules from database"""
    list_snat = []
    list_snat = get_list_all_waf_rule()
    return JsonResponse(list_snat, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A WAF RULE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_waf_rule(request, id):
    """Getting WAF by id from database"""
    snat = get_one_waf_rule(id)
    return JsonResponse(snat, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE A WAF RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['name', 'variables', 'operators', 'transformations', 'actions'],
                         properties={'name': Schema(type=TYPE_STRING, description="Name of the rule"),
                                     'variables': Schema(type=TYPE_ARRAY, items=Schema(type=TYPE_STRING)),
                                     'operators': Schema(type=TYPE_ARRAY, description= "If a transformation don't have a value then value will be an empty string", 
                                                         items=Schema(type=TYPE_OBJECT, required=['type', 'value'], properties={
                                                             'type': Schema(type=TYPE_STRING),
                                                             'value': Schema(type=TYPE_STRING)})),
                                     'transformations': Schema(type=TYPE_ARRAY, items=Schema(type=TYPE_STRING)),
                                     'action': Schema(type=TYPE_ARRAY, description= "id action is mandatory. If an action don't have a value like pass or log then value will be an empty string", 
                                                      items=Schema(type=TYPE_OBJECT, required=['type', 'value'], properties={
                                                          'type': Schema(type=TYPE_STRING),
                                                          'value': Schema(type=TYPE_STRING)})),
                                     }
                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_waf_rule(request):
    """Creating a new WAF Rule and adding it to the database"""
    try:
        data = request.data
        data = convert_waf_rule_payload(data)
        
        serializer_rule_waf = RulesWafSerializer(data=data)
        if serializer_rule_waf.is_valid():
            # Create the rule waf in string format
            rule_waf = create_rule_waf_str(data)
            # Create the rule waf in system and reload the nginx
            create_rule_waf_in_system(rule_waf)
            data["rule_content"] = rule_waf
            serializer_rule_waf = RulesWafSerializer(data=data)
            if serializer_rule_waf.is_valid():

                # Add the rule to the database
                serializer_rule_waf.save()
                return JsonResponse({"msg": f"{CONSTANT_WAF_RULE} {SUCCESS_MESSAGES_CREATING}"}, status=201)

        return JsonResponse({"error": list(serializer_rule_waf.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        delete_rule_waf_in_system(rule_waf)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_WAF_RULE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A WAF RULE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_waf_rule(request, id):
    """Deleting a waf_rule from database"""
    try:
        waf_rule = RulesWaf.objects.get(id=id)

        # Delete rule from system
        delete_rule_waf_in_system(waf_rule.rule_content)

        # delete rule from database
        waf_rule.delete()
        return JsonResponse({"msg": f"{CONSTANT_WAF_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_WAF_RULE}"}, status=400)
    except RulesWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE A WAF RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['name', 'variables', 'operators', 'transformations', 'actions'],
                         properties={'name': Schema(type=TYPE_STRING, description="Name of the rule"),
                                     'variables': Schema(type=TYPE_ARRAY, items=Schema(type=TYPE_STRING)),
                                     'operators': Schema(type=TYPE_ARRAY, description= "If a transformation don't have a value then value will be an empty string", 
                                                         items=Schema(type=TYPE_OBJECT, required=['type', 'value'], properties={
                                                             'type': Schema(type=TYPE_STRING),
                                                             'value': Schema(type=TYPE_STRING)})),
                                     'transformations': Schema(type=TYPE_ARRAY, items=Schema(type=TYPE_STRING)),
                                     'action': Schema(type=TYPE_ARRAY, description= "id action is mandatory. If an action don't have a value like pass or log then value will be an empty string", 
                                                      items=Schema(type=TYPE_OBJECT, required=['type', 'value'], properties={
                                                          'type': Schema(type=TYPE_STRING),
                                                          'value': Schema(type=TYPE_STRING)})),
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_waf_rule(request, id):
    """Updating a WAF Rule"""
    try:
        waf_rule = RulesWaf.objects.get(id=id)
        data = request.data
        data = convert_waf_rule_payload(data)
        
        serializer_rule_waf = RulesWafSerializer(waf_rule, data=data)
        if serializer_rule_waf.is_valid():
            # Create the rule waf in string format
            rule_waf = create_rule_waf_str(data)
            # Update the rule waf in system and reload the nginx
            update_rule_waf_in_system(waf_rule.rule_content, rule_waf)
            data["rule_content"] = rule_waf
            serializer_rule_waf = RulesWafSerializer(waf_rule, data=data)
            if serializer_rule_waf.is_valid():

                # Add the rule to the database
                serializer_rule_waf.save()
                return JsonResponse({"msg": f"{CONSTANT_WAF_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

        return JsonResponse({"error": list(serializer_rule_waf.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        # Get back the previous rule in system
        delete_rule_waf_in_system(rule_waf)
        create_rule_waf_in_system(waf_rule.rule_content)
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_WAF_RULE}"}, status=400)
    except RulesWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


########################################
########### WAF Application ############
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL WAF APPLICATIONS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_waf_application(request):
    """Getting all waf applications from database"""
    list_waf_application = []
    list_waf_application = get_list_all_waf_application()
    return JsonResponse(list_waf_application, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A WAF APPLICATION",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_waf_application(request, id):
    """Getting waf application by id from database"""
    waf_application = get_one_waf_application(id)
    return JsonResponse(waf_application, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE A WAF APPLICATION", request_body=Schema(
                         type=TYPE_OBJECT, required=['name', 'application_type', 'application_value', 'description', 'rules'],
                         properties={'name': Schema(type=TYPE_STRING, description="Name of the application"),
                                     'application_type': Schema(type=TYPE_STRING, enum=['ip', 'domain']),
                                     'application_value': Schema(type=TYPE_STRING),
                                     'application_port': Schema(type=TYPE_INTEGER),
                                     'description': Schema(type=TYPE_STRING),
                                     'country': Schema(type=TYPE_ARRAY, description="List of country code", items=Schema(type=TYPE_STRING)),
                                     'rules': Schema(type=TYPE_ARRAY, description="List of rules object", 
                                                     items=Schema(type=TYPE_OBJECT, required=['rule_waf', 'rule_policy', 'rule_log'],
                                                                  properties={'rule_waf': Schema(type=TYPE_INTEGER, description="Id of the rule"),
                                                                              'rule_policy': Schema(type=TYPE_BOOLEAN, description="True if the user select this rule in Block"),
                                                                              'rule_log': Schema(type=TYPE_BOOLEAN)}))
                                     }
                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_waf_application(request):
    """Creating a new WAF Application and adding it to the database"""
    try:
        data = request.data

        # Create another object that make country as a string to be saved in database
        data_serializer = data.copy()
        data_serializer['country'] = ','.join(data_serializer['country'])

        # Give the GEOIP rule a unique id
        rule_geoip_id = find_possible_id()
        data["rule_geoip_id"] = rule_geoip_id
        data_serializer["rule_geoip_id"] = rule_geoip_id
        
        serializer_application_waf = ApplicationWafSerializer(data=data_serializer)
        if serializer_application_waf.is_valid():

            create_application_waf_in_system(data)

            serializer_application_waf.save()
            return JsonResponse({"msg": f"{CONSTANT_WAF_APPLICATION} {SUCCESS_MESSAGES_CREATING}"}, status=201)
        return JsonResponse({"error": list(serializer_application_waf.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_WAF_APPLICATION}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A WAF RULE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_waf_application(request, id):
    """Deleting a waf_application from database"""
    try:
        waf_application = ApplicationWaf.objects.get(id=id)

        # Delete application from system
        delete_application_waf_in_system(waf_application)

        # delete application from database
        waf_application.delete()
        return JsonResponse({"msg": f"{CONSTANT_WAF_APPLICATION} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_WAF_APPLICATION}"}, status=400)
    except ApplicationWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_APPLICATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UPDATE A WAF APPLICATION", request_body=Schema(
                         type=TYPE_OBJECT, required=['name', 'application_type', 'application_value', 'description', 'rules'],
                         properties={'name': Schema(type=TYPE_STRING, description="Name of the application"),
                                     'application_type': Schema(type=TYPE_STRING, enum=['ip', 'domain']),
                                     'application_value': Schema(type=TYPE_STRING),
                                     'application_port': Schema(type=TYPE_INTEGER),
                                     'description': Schema(type=TYPE_STRING),
                                     'country': Schema(type=TYPE_ARRAY, description="List of country code", items=Schema(type=TYPE_STRING)),
                                     'rules': Schema(type=TYPE_ARRAY, description="List of rules object", 
                                                     items=Schema(type=TYPE_OBJECT, required=['rule_waf', 'rule_policy', 'rule_log'],
                                                                  properties={'rule_waf': Schema(type=TYPE_INTEGER, description="Id of the rule"),
                                                                              'rule_policy': Schema(type=TYPE_BOOLEAN, description="True if the user select this rule in Block"),
                                                                              'rule_log': Schema(type=TYPE_BOOLEAN)}))
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_waf_application(request, id):
    """Updating a WAF Application"""
    try:
        waf_application = ApplicationWaf.objects.get(id=id)
        data = request.data

        # Create another object that make country as a string to be saved in database
        app_data = data
        app_data['country'] = ','.join(app_data['country'])

        # Give the GEOIP rule a unique id
        data["rule_geoip_id"] = waf_application.rule_geoip_id
        
        serializer_application_waf = ApplicationWafSerializer(waf_application, data=app_data)
        if serializer_application_waf.is_valid():

            update_application_waf_in_system(waf_application, data)

            serializer_application_waf.save()
            return JsonResponse({"msg": f"{CONSTANT_WAF_APPLICATION} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

        return JsonResponse({"error": list(serializer_application_waf.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_WAF_APPLICATION}"}, status=400)
    except ApplicationWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_APPLICATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
