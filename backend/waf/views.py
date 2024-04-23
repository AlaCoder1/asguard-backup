from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from backend.waf.constant_variables import CONSTANT_WAF_CONFIG, CONSTANT_WAF_RULE
from backend.waf.list_waf import get_list_all_waf, get_one_waf, get_one_waf_config
from backend.waf.models import ConfigWaf
from backend.waf.serializers import ConfigWafSerializer, RulesWafSerializer
from backend.waf.utils import change_waf_config_file
from backend.waf.utils_system import create_rule_waf_in_system
from utils.constant_variables import ERROR_MESSAGES_CREATING, ERROR_MESSAGES_UPDATING, SUCCESS_MESSAGES_CREATING_ITEM, SUCCESS_MESSAGES_UPDATE
from utils.errors_utils import CommandExecutionError


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
                     operation_summary="API TO UPDATE THE WAF CONFIG", request_body=Schema(
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
    """Creating a new Route and adding it to the database"""
    try:
        data = request.data
        config_waf = ConfigWaf.objects.get(id=id)
        change_waf_config_file(data)
        config_waf_serializer = ConfigWafSerializer(config_waf, data=data)
        if config_waf_serializer.is_valid():
            config_waf_serializer.save()
            return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(CONSTANT_WAF_CONFIG)}, status=200)
        return JsonResponse({"error": list(config_waf_serializer.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_UPDATING.format(CONSTANT_WAF_CONFIG)}, status=400)


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
    list_snat = get_list_all_waf()
    return JsonResponse(list_snat, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A WAF RULE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_waf_rule(request, id):
    """Getting WAF by id from database"""
    snat = get_one_waf(id)
    return JsonResponse(snat, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE A WAF RULE", request_body=Schema(
                         type=TYPE_OBJECT, required=['interface'],
                         properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                     }
                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_waf_rule(request):
    """Creating a new WAF Rule and adding it to the database"""
    try:
        data = request.data
        
        serializer_rule_waf = RulesWafSerializer(data=data)
        if serializer_rule_waf.is_valid():

            rule_waf = create_rule_waf_in_system(data)
            data["rule_content"] = rule_waf
            serializer_rule_waf = RulesWafSerializer(data=data)
            if serializer_rule_waf.is_valid():

                # Add the rule to the database
                serializer_rule_waf.save()
                return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format(CONSTANT_WAF_RULE, "")}, status=201)

        return JsonResponse({"error": list(serializer_rule_waf.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_CREATING.format(CONSTANT_WAF_RULE)}, status=400)
