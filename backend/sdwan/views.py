from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from backend.sdwan.list_area import get_list_all_area, get_list_all_sdwan_rule, get_one_area, get_one_sdwan_rule
from backend.sdwan.models import Area, SdwanRules
from backend.sdwan.serializers import AreaSerializer, SdwanRulesSerializer
from backend.sdwan.utils import script_failover, start_sdwan_rule_system
from utils.constant_variables import ERROR_MESSAGES_INEXISTANT, SUCCESS_MESSAGES_CREATING_ITEM, SUCCESS_MESSAGES_DELETE, SUCCESS_MESSAGES_UPDATE


########################################
################# AREA #################
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL AREAS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_area(request):
    """Getting all servers from database"""
    list_area = []
    list_area = get_list_all_area()
    return JsonResponse(list_area, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN AREA",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_area(request, id):
    """Getting area by id from database"""
    area = get_one_area(id)
    return JsonResponse(area, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE AN AREA",
                     request_body=Schema(type=TYPE_OBJECT, required=['name', 'members'],
                                         properties={'name': Schema(type=TYPE_STRING),
                                                     'members': Schema(type=TYPE_ARRAY, description="list of interfaces name like ['LAN', 'WAN']",
                                                                       items=Schema(type=TYPE_STRING)),
                                                                       }
                                                                       ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_area(request):
    """Creating a new area and adding it to the database"""
    data = request.data

    data["members"] = ",".join(data["members"])

    serializer_server = AreaSerializer(data=data)
    if serializer_server.is_valid():

        # Add the server to the database
        serializer_server.save()
        return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('Area', data["name"])}, status=201)
    else:
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN AREA",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_area(request, id):
    """Deleting an area from database"""
    try:
        if (request.method == 'DELETE'):
            area = Area.objects.get(id=id)

            # delete from database
            area.delete()
            return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(area.name)}, status=201)
    except Area.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('Area')}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE AN AREA",
                     request_body=Schema(type=TYPE_OBJECT, required=['name', 'members'],
                                         properties={'name': Schema(type=TYPE_STRING),
                                                     'members': Schema(type=TYPE_ARRAY, 
                                                                       description="list of interfaces name like ['LAN', 'WAN']",
                                                                       items=Schema(type=TYPE_STRING)),
                                                                       }
                                                                       ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_area(request, id):
    """Updating area in database"""
    area = Area.objects.get(id=id)
    data = request.data
    data["members"] = ",".join(data["members"])

    serializer_server = AreaSerializer(area, data=data)
    if serializer_server.is_valid():

        # Add the server to the database
        serializer_server.save()
        return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format('Area', area.name)}, status=201)
    else:
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)


########################################
############# SDWAN RULES ##############
########################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL AREAS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_sdwan_rule(request):
    """Getting all servers from database"""
    list_sdwan_rule = []
    list_sdwan_rule = get_list_all_sdwan_rule()
    return JsonResponse(list_sdwan_rule, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET AN AREA",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_sdwan_rule(request, id):
    """Getting sdwan_rules by id from database"""
    sdwan_rule = get_one_sdwan_rule(id)
    return JsonResponse(sdwan_rule, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO CREATE AN SDWAN RULES",
                     request_body=Schema(type=TYPE_OBJECT, 
                                         required=['name', 'source_address', 'area', 'algorythme_type', 'destination_address', 
                                                   'health_check', 'health_check_target', 'primary_interface'],
                                         properties={'name': Schema(type=TYPE_STRING),
                                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask"),
                                                     'area':Schema(type=TYPE_INTEGER, description="When choosing failover algorithm you can choose only areas with 2 members"), 
                                                     'algorythme_type':Schema(type=TYPE_STRING, enum=["failover", "round_robin"]),
                                                     'destination_address':Schema(type=TYPE_STRING, description="format of address/mask"),
                                                     'health_check':Schema(type=TYPE_STRING),
                                                     'health_check_target':Schema(type=TYPE_STRING),
                                                     'primary_interface':Schema(type=TYPE_STRING, description="This is used when choosing failover algorithm")
                                                     }
                                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_sdwan_rule(request):
    """Creating a new SDWAN rule and adding it to the database"""
    data = request.data

    serializer_server = SdwanRulesSerializer(data=data)
    if serializer_server.is_valid():

        # Add the server to the database
        serializer_server.save()
        return JsonResponse({"msg": SUCCESS_MESSAGES_CREATING_ITEM.format('SDWAN Rule', data["name"])}, status=201)
    else:
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN SDWAN RULE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_sdwan_rule(request, id):
    """Deleting an sdwan_rule from database"""
    try:
        if (request.method == 'DELETE'):
            sdwan_rule = SdwanRules.objects.get(id=id)

            # delete from database
            sdwan_rule.delete()
            return JsonResponse({"msg": SUCCESS_MESSAGES_DELETE.format(sdwan_rule.name)}, status=201)
    except SdwanRules.DoesNotExist:
        return JsonResponse({"error": ERROR_MESSAGES_INEXISTANT.format('SdwanRules')}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE AN SDWAN RULES",
                     request_body=Schema(type=TYPE_OBJECT, 
                                         required=['name', 'source_address', 'area', 'algorythme_type', 'destination_address', 
                                                   'health_check', 'health_check_target', 'primary_interface'],
                                         properties={'name': Schema(type=TYPE_STRING),
                                                     'source_address': Schema(type=TYPE_STRING, description="format of address/mask"),
                                                     'area':Schema(type=TYPE_STRING, description="When choosing failover algorithm you can choose only areas with 2 members"), 
                                                     'algorythme_type':Schema(type=TYPE_STRING, enum=["failover", "round_robin"]),
                                                     'destination_address':Schema(type=TYPE_STRING, description="format of address/mask"),
                                                     'health_check':Schema(type=TYPE_STRING),
                                                     'health_check_target':Schema(type=TYPE_STRING),
                                                     'primary_interface':Schema(type=TYPE_STRING, description="This is used when choosing failover algorithm")
                                                     }
                                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_sdwan_rule(request, id):
    """Updating a new SDWAN rule"""
    data = request.data
    sdwan_rule = SdwanRules.objects.get(id=id)

    serializer_server = SdwanRulesSerializer(sdwan_rule, data=data)
    if serializer_server.is_valid():

        # Add the server to the database
        serializer_server.save()
        return JsonResponse({"msg": SUCCESS_MESSAGES_UPDATE.format(data["name"])}, status=201)
    else:
        return JsonResponse({"error": list(serializer_server.errors.values())[0][0]}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_sdwan_rule(request, id):
    sdwan_rule = SdwanRules.objects.get(id=id)
    start_sdwan_rule_system()
    
    return JsonResponse({"msg": f"Start SDWAN RULE {sdwan_rule.name}"}, status=201)
