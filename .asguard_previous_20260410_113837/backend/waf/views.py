from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from decouple import config

from backend.managementCertificates.models import Certificate
from backend.waf.list_waf import get_alerts, get_list_all_waf_rule, get_list_all_waf_application, get_one_waf_rule, get_one_waf_application, get_one_waf_config
from backend.waf.models import ApplicationWaf, ConfigWaf, RulesWaf
from backend.waf.serializers import ApplicationWafSerializer, ConfigWafSerializer, RulesWafSerializer
from backend.waf.utils import convert_waf_rule_payload, find_possible_id
from backend.waf.utils_application import create_application_waf_in_system, delete_application_waf_in_system, restore_previous_application, update_application_waf_in_system
from backend.waf.utils_config import update_waf_configuration_in_system
from backend.waf.utils_rules import create_rule_waf_in_system, create_rule_waf_str, delete_rule_waf_in_system, update_rule_waf_in_system
from utils.errors_utils import CommandExecutionError
from utils.utils_command_system import restart_nginx_in_system


# Constants
CONSTANT_WAF_CONFIG = _("WAF Config")
CONSTANT_WAF_RULE = _("WAF Rule")
CONSTANT_WAF_APPLICATION = _("WAF Application")
CONSTANT_WAF_ALERT = _("WAF Alert")
CONSTANT_CERTIFICATE = _("Certificate")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UPDATING = _("System error in updating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_MODSECURITY_RULE = _("Cannot deleting or updating one of the modsecurity rule")


########################################
########## WAF Configuration ###########
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET THE WAF CONFIG",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_waf_config(request):
    """Getting WAF Config from database"""
    waf_config = get_one_waf_config()
    return JsonResponse(waf_config, safe=False)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO UPDATE THE WAF CONFIG", 
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            "rule_engine_initialization", "access_request_bodies", "xml_request_body_parser",
            "json_request_body_parser", "maximum_request_body_size", 
            "request_body_size_files_excluded", "request_body_limit_action", 
            "maximum_parsing_depth_json", "maximum_number_args_request", "pcre_match_limit", 
            "pcre_match_limit_recursion", "response_body_access", "response_body_mimetype", 
            "response_body_limit", "response_body_limit_action"],
        properties={
            'rule_engine_initialization': Schema(type=TYPE_STRING, enum=["On", "Off", "DetectionOnly"]),
            'access_request_bodies':Schema(type=TYPE_BOOLEAN, default=False),
            'xml_request_body_parser':Schema(type=TYPE_BOOLEAN, default=False),
            'json_request_body_parser':Schema(type=TYPE_BOOLEAN, default=False),
            'maximum_request_body_size': Schema(type=TYPE_INTEGER, example=13107200),
            'request_body_size_files_excluded': Schema(type=TYPE_INTEGER, example=131072),
            'request_body_limit_action': Schema(type=TYPE_STRING, enum=["ProcessPartial", "Reject"]),
            'maximum_parsing_depth_json': Schema(type=TYPE_INTEGER, example=512),
            'maximum_number_args_request': Schema(type=TYPE_INTEGER, example=1000),
            'pcre_match_limit': Schema(type=TYPE_INTEGER, example=1000),
            'pcre_match_limit_recursion': Schema(type=TYPE_INTEGER, example=1000),
            'response_body_access':Schema(type=TYPE_BOOLEAN, default=True),
            'response_body_mimetype': Schema(type=TYPE_STRING, enum=["text/html", "text/xml", "text/plain", "text/*"]),
            'response_body_limit': Schema(type=TYPE_INTEGER, example=524288),
            'response_body_limit_action': Schema(type=TYPE_STRING, enum=["ProcessPartial", "Reject", "log", "log allow", "pass"]),
            }
            ))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_config_waf(request, id):
    """Updating WAF Configuration"""
    try:
        data = request.data
        config_waf = ConfigWaf.objects.get(id=id)
        config_waf_serializer = ConfigWafSerializer(config_waf, data=data)
        if config_waf_serializer.is_valid():
            update_waf_configuration_in_system(data)
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
@require_http_methods(['GET'])
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
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_waf_rule(request, id):
    """Getting WAF by id from database"""
    snat = get_one_waf_rule(id)
    return JsonResponse(snat, safe=False)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A WAF RULE", 
    request_body=Schema(
        type=TYPE_OBJECT, 
        required=['name', 'variables', 'operators', 'transformations', 'actions'],
        properties={
            'name': Schema(
                type=TYPE_STRING, example="rule_waf", description="Name of the rule"),
            'description': Schema(
                type=TYPE_STRING, example="Description of rule waf", description="Description of the rule"),
            'variables': Schema(
                type=TYPE_ARRAY, example=["INBOUND_DATA_ERROR", "REQUEST_METHOD"], 
                items=Schema(type=TYPE_STRING)),
            'operators': Schema(
                type=TYPE_ARRAY, 
                example=[{"type": "eq", "value": "1"}, {"type": "lt", "value": "45"}], 
                description= "If a transformation don't have a value then value will be an empty string", 
                items=Schema(
                    type=TYPE_OBJECT, required=['type', 'value'], 
                    properties={'type': Schema(type=TYPE_STRING), 
                                'value': Schema(type=TYPE_STRING)})),
            'transformations': Schema(
                type=TYPE_ARRAY, example=["sqlHexDecode", "base64DecodeExt"], 
                items=Schema(type=TYPE_STRING)),
            'actions': Schema(
                type=TYPE_ARRAY, 
                description= "id action is mandatory. If an action don't have a value like pass or log then value will be an empty string",
                example=[{"type": "phase", "value": "3"}, {"type": "id", "value": "30"}],
                items=Schema(
                    type=TYPE_OBJECT, required=['type', 'value'],
                    properties={'type': Schema(type=TYPE_STRING),
                                'value': Schema(type=TYPE_STRING)})),
            }
            ))
@api_view(['POST'])
@require_http_methods(['POST'])
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
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_waf_rule(request, id):
    """Deleting a waf_rule from database"""
    try:
        waf_rule = RulesWaf.objects.get(id=id)

        # Return an error when trying to delete one of the default modsecurity rules
        if not waf_rule.created:
            return JsonResponse({"error": ERROR_MESSAGES_MODSECURITY_RULE}, status=400)

        # Delete rule from system
        delete_rule_waf_in_system(waf_rule.rule_content)

        # delete rule from database
        waf_rule.delete()
        return JsonResponse({"msg": f"{CONSTANT_WAF_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_WAF_RULE}"}, status=400)
    except RulesWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A WAF RULE", 
    request_body=Schema(
        type=TYPE_OBJECT, 
        required=['name', 'variables', 'operators', 'transformations', 'actions'],
        properties={
            'name': Schema(
                type=TYPE_STRING, example="rule_waf", description="Name of the rule"),
            'description': Schema(
                type=TYPE_STRING, example="Description of rule waf", description="Description of the rule"),
            'variables': Schema(
                type=TYPE_ARRAY, example=["INBOUND_DATA_ERROR", "REQUEST_METHOD"], 
                items=Schema(type=TYPE_STRING)),
            'operators': Schema(
                type=TYPE_ARRAY, 
                example=[{"type": "eq", "value": 1}, {"type": "lt", "value": 45}], 
                description= "If a transformation don't have a value then value will be an empty string", 
                items=Schema(
                    type=TYPE_OBJECT, required=['type', 'value'], 
                    properties={'type': Schema(type=TYPE_STRING), 
                                'value': Schema(type=TYPE_STRING)})),
            'transformations': Schema(
                type=TYPE_ARRAY, example=["sqlHexDecode", "base64DecodeExt"], 
                items=Schema(type=TYPE_STRING)),
            'actions': Schema(
                type=TYPE_ARRAY, 
                description= "id action is mandatory. If an action don't have a value like pass or log then value will be an empty string",
                example=[{"type": "phase", "value": 3}, {"type": "id", "value": 30}],
                items=Schema(
                    type=TYPE_OBJECT, required=['type', 'value'],
                    properties={'type': Schema(type=TYPE_STRING),
                                'value': Schema(type=TYPE_STRING)})),
            }
            ))
@api_view(['PUT'])
@require_http_methods(['PUT'])
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
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_waf_application(request):
    """Getting all waf applications from database"""
    list_waf_application = get_list_all_waf_application()
    return JsonResponse(list_waf_application, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A WAF APPLICATION",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_waf_application(request, id):
    """Getting waf application by id from database"""
    waf_application = get_one_waf_application(id)
    return JsonResponse(waf_application, safe=False)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE A WAF APPLICATION", 
    request_body=Schema(
        type=TYPE_OBJECT, 
        required=['name', 'application_type', 'application_value', 'description', 'rules', 'config'],
        properties={'name': Schema(
                        type=TYPE_STRING, example="application_waf", 
                        description="Name of the application"),
                    'application_type': Schema(
                        type=TYPE_STRING, enum=['ip', 'domain']),
                    'application_protocol': Schema(
                        type=TYPE_STRING, enum=['http', 'https']),
                    'certificate_name': Schema(
                        type=TYPE_STRING, example="cert_server", 
                        description="Required when choosing HTTPS protocol"),
                    'application_value': Schema(
                        type=TYPE_STRING, example=config('IP_ADDRESS')),
                    'application_port': Schema(
                        type=TYPE_INTEGER, example=1443, 
                        description="When choosing HTTPS protocol the port must be compatible with ssl in format of *443"),
                    'description': Schema(
                        type=TYPE_STRING, example="Description of application waf"),
                    'country': Schema(
                        type=TYPE_ARRAY, example=["TN"], description="List of country code", 
                        items=Schema(type=TYPE_STRING)),
                    'rules': Schema(
                        type=TYPE_ARRAY, 
                        example=[{"rule_waf": 3, "rule_policy": True, "rule_log": False}], 
                        description="List of rules object",
                        items=Schema(
                            type=TYPE_OBJECT, required=['rule_waf', 'rule_policy', 'rule_log'],
                            properties={
                                'rule_waf': Schema(type=TYPE_INTEGER, 
                                                   description="Id of the rule"),
                                'rule_policy': Schema(type=TYPE_BOOLEAN, 
                                                      description="True if the user select this rule in Block"),
                                'rule_log': Schema(type=TYPE_BOOLEAN)})),
                    'config': Schema(
                        type=TYPE_OBJECT, required=[
                            "rule_engine_initialization", "access_request_bodies", "xml_request_body_parser",
                            "json_request_body_parser", "maximum_request_body_size", 
                            "request_body_size_files_excluded", "request_body_limit_action", 
                            "maximum_parsing_depth_json", "maximum_number_args_request", "pcre_match_limit", 
                            "pcre_match_limit_recursion", "response_body_access", "response_body_mimetype", 
                            "response_body_limit", "response_body_limit_action"],
                        properties={
                            'rule_engine_initialization': Schema(type=TYPE_STRING, enum=["On", "Off", "DetectionOnly"]),
                            'access_request_bodies':Schema(type=TYPE_BOOLEAN, default=False),
                            'xml_request_body_parser':Schema(type=TYPE_BOOLEAN, default=False),
                            'json_request_body_parser':Schema(type=TYPE_BOOLEAN, default=False),
                            'maximum_request_body_size': Schema(type=TYPE_INTEGER, example=13107200),
                            'request_body_size_files_excluded': Schema(type=TYPE_INTEGER, example=131072),
                            'request_body_limit_action': Schema(type=TYPE_STRING, enum=["ProcessPartial", "Reject"]),
                            'maximum_parsing_depth_json': Schema(type=TYPE_INTEGER, example=512),
                            'maximum_number_args_request': Schema(type=TYPE_INTEGER, example=1000),
                            'pcre_match_limit': Schema(type=TYPE_INTEGER, example=1000),
                            'pcre_match_limit_recursion': Schema(type=TYPE_INTEGER, example=1000),
                            'response_body_access':Schema(type=TYPE_BOOLEAN, default=True),
                            'response_body_mimetype': Schema(type=TYPE_STRING, enum=["text/html", "text/xml", "text/plain", "text/*"]),
                            'response_body_limit': Schema(type=TYPE_INTEGER, example=524288),
                            'response_body_limit_action': Schema(type=TYPE_STRING, enum=["ProcessPartial", "Reject", "log", "log allow", "pass"])}),
                    }
                    ))
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_waf_application(request):
    """Creating a new WAF Application and adding it to the database"""
    try:
        data = request.data

        # Raise an error in https protocol if the certificate does not exist
        if data.get("application_protocol") == "https":
            Certificate.objects.get(name=data["certificate_name"])

        # Create another object that make country as a string to be saved in database
        data_serializer = data.copy()
        data_serializer['country'] = ','.join(data_serializer['country'])

        # Give the GEOIP rule a unique id
        rule_geoip_id = find_possible_id()
        data["rule_geoip_id"] = rule_geoip_id
        data_serializer["rule_geoip_id"] = rule_geoip_id
        
        data_config = data_serializer.pop("config")
        config_serializer = ConfigWafSerializer(data=data_config)
        if config_serializer.is_valid():
            config_serializer.save()
            data_serializer["config"] = ConfigWaf.objects.last().pk
            serializer_application_waf = ApplicationWafSerializer(data=data_serializer)
            if serializer_application_waf.is_valid():

                create_application_waf_in_system(data)

                serializer_application_waf.save()
                return JsonResponse({"msg": f"{CONSTANT_WAF_APPLICATION} {SUCCESS_MESSAGES_CREATING}"}, status=201)

            return JsonResponse({"error": list(serializer_application_waf.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": list(config_serializer.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        # Delete application from system
        delete_application_waf_in_system(data["name"])
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_WAF_APPLICATION}"}, status=400)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERTIFICATE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)

@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A WAF RULE",)
@api_view(['Delete'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_waf_application(request, id):
    """Deleting a waf_application from database"""
    try:
        waf_application = ApplicationWaf.objects.get(id=id)

        # Delete application from system
        delete_application_waf_in_system(waf_application.name)

        # delete application from database
        waf_application.config.delete()
        waf_application.delete()
        return JsonResponse({"msg": f"{CONSTANT_WAF_APPLICATION} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_WAF_APPLICATION}"}, status=400)
    except ApplicationWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_APPLICATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except ConfigWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_CONFIG} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'}, 
    operation_summary="API TO CREATE A WAF APPLICATION", 
    request_body=Schema(
        type=TYPE_OBJECT, 
        required=['name', 'application_type', 'application_value', 'description', 'rules', 'config'],
        properties={'name': Schema(
                        type=TYPE_STRING, example="application_waf", 
                        description="Name of the application"),
                    'application_type': Schema(
                        type=TYPE_STRING, enum=['ip', 'domain']),
                    'application_protocol': Schema(
                        type=TYPE_STRING, enum=['http', 'https']),
                    'certificate_name': Schema(
                        type=TYPE_STRING, example="cert_server", 
                        description="Required when choosing HTTPS protocol"),
                    'application_value': Schema(
                        type=TYPE_STRING, example=config('IP_ADDRESS')),
                    'application_port': Schema(
                        type=TYPE_INTEGER, example=1443, 
                        description="When choosing HTTPS protocol the port must be compatible with ssl in format of *443"),
                    'description': Schema(
                        type=TYPE_STRING, example="Description of application waf"),
                    'country': Schema(
                        type=TYPE_ARRAY, example=["TN"], description="List of country code", 
                        items=Schema(type=TYPE_STRING)),
                    'rules': Schema(
                        type=TYPE_ARRAY, 
                        example=[{"rule_waf": 3, "rule_policy": True, "rule_log": False}], 
                        description="List of rules object",
                        items=Schema(
                            type=TYPE_OBJECT, required=['rule_waf', 'rule_policy', 'rule_log'],
                            properties={
                                'rule_waf': Schema(type=TYPE_INTEGER, 
                                                   description="Id of the rule"),
                                'rule_policy': Schema(type=TYPE_BOOLEAN, 
                                                      description="True if the user select this rule in Block"),
                                'rule_log': Schema(type=TYPE_BOOLEAN)})),
                    'config': Schema(
                        type=TYPE_OBJECT, required=[
                            "rule_engine_initialization", "access_request_bodies", "xml_request_body_parser",
                            "json_request_body_parser", "maximum_request_body_size", 
                            "request_body_size_files_excluded", "request_body_limit_action", 
                            "maximum_parsing_depth_json", "maximum_number_args_request", "pcre_match_limit", 
                            "pcre_match_limit_recursion", "response_body_access", "response_body_mimetype", 
                            "response_body_limit", "response_body_limit_action"],
                        properties={
                            'rule_engine_initialization': Schema(type=TYPE_STRING, enum=["On", "Off", "DetectionOnly"]),
                            'access_request_bodies':Schema(type=TYPE_BOOLEAN, default=False),
                            'xml_request_body_parser':Schema(type=TYPE_BOOLEAN, default=False),
                            'json_request_body_parser':Schema(type=TYPE_BOOLEAN, default=False),
                            'maximum_request_body_size': Schema(type=TYPE_INTEGER, example=13107200),
                            'request_body_size_files_excluded': Schema(type=TYPE_INTEGER, example=131072),
                            'request_body_limit_action': Schema(type=TYPE_STRING, enum=["ProcessPartial", "Reject"]),
                            'maximum_parsing_depth_json': Schema(type=TYPE_INTEGER, example=512),
                            'maximum_number_args_request': Schema(type=TYPE_INTEGER, example=1000),
                            'pcre_match_limit': Schema(type=TYPE_INTEGER, example=1000),
                            'pcre_match_limit_recursion': Schema(type=TYPE_INTEGER, example=1000),
                            'response_body_access':Schema(type=TYPE_BOOLEAN, default=True),
                            'response_body_mimetype': Schema(type=TYPE_STRING, enum=["text/html", "text/xml", "text/plain", "text/*"]),
                            'response_body_limit': Schema(type=TYPE_INTEGER, example=524288),
                            'response_body_limit_action': Schema(type=TYPE_STRING, enum=["ProcessPartial", "Reject", "log", "log allow", "pass"])}),
                    }
                    ))
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_waf_application(request, id):
    """Updating a WAF Application"""
    try:
        waf_application = ApplicationWaf.objects.get(id=id)
        config = waf_application.config
        data = request.data

        # Raise an error in https protocol if the certificate does not exist
        if data.get("application_protocol") == "https":
            Certificate.objects.get(name=data["certificate_name"])

        # Create another object that make country as a string to be saved in database
        data_serializer = data.copy()
        data_serializer['country'] = ','.join(data_serializer['country'])

        # Give the GEOIP rule a unique id by getting the same previous id or create a new one
        if waf_application.rule_geoip_id:
            data["rule_geoip_id"] = waf_application.rule_geoip_id
            data_serializer["rule_geoip_id"] = waf_application.rule_geoip_id
        else:
            # Give the GEOIP rule a unique id
            rule_geoip_id = find_possible_id()
            data["rule_geoip_id"] = rule_geoip_id
            data_serializer["rule_geoip_id"] = rule_geoip_id
        
        data_config = data_serializer.pop("config")
        config_serializer = ConfigWafSerializer(config, data=data_config)
        if config_serializer.is_valid():
            config_serializer.save()
            serializer_application_waf = ApplicationWafSerializer(waf_application, data=data_serializer)
            if serializer_application_waf.is_valid():
                # Update the application
                update_application_waf_in_system(waf_application, data)
                # Delete the backup of th previous application
                delete_application_waf_in_system(f"{waf_application.name}_copy")
                # Save the new data in database
                serializer_application_waf.save()
                return JsonResponse({"msg": f"{CONSTANT_WAF_APPLICATION} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

            return JsonResponse({"error": list(serializer_application_waf.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": list(config_serializer.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        delete_application_waf_in_system(data["name"])
        restore_previous_application(waf_application.name)
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_WAF_APPLICATION}"}, status=400)
    except ApplicationWaf.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_WAF_APPLICATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except Certificate.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_CERTIFICATE} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


########################################
############# WAF Alerts ###############
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL WAF ALERTS",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_waf_alerts(request):
    """Getting all waf alerts from database"""
    list_waf_alerts = get_alerts()
    return JsonResponse(list_waf_alerts, safe=False)
