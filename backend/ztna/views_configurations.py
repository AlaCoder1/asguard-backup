from django.forms import model_to_dict
import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import TYPE_ARRAY, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Schema
from datetime import datetime
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from backend.ztna.models import HostConfigs, InterceptConfigs
from backend.ztna.constant_variables import CONSTANT_CONTENT_TYPE, PATH_ZTNA_CONFIGS
from backend.ztna.serializers import HostConfigsSerializer, HostSerializerUpdate, InterceptConfigsSerializer, InterceptSerializerUpdate
from backend.ztna.utils import get_ztna_token_from_system


# Constants
CONSTANT_CONFIGURATION = _('Configuration')
CONSTANT_INTERCEPT_CONFIGURATION = _('Intercept Configuration')
CONSTANT_HOST_CONFIGURATION = _('Host Configuration')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UPDATING = _("System error in updating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_REQUIRED_START = _("Try to start the service")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA HOST CONFIGURATIONS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_host_configs(request):
    """Getting all configs from database"""
    try:
        if request.method == 'GET':
            host_configs = list(map(model_to_dict, HostConfigs.objects.all()))
            return JsonResponse(host_configs, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA INTERCEPT CONFIGURATIONS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_intercept_configs(request):
    """Getting list of all intercept configs from database"""
    try:
        intercept_configs = list(map(model_to_dict, InterceptConfigs.objects.all()))
        return JsonResponse(intercept_configs, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@swagger_auto_schema(
    'POST', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A ZTNA CONFIGURATIONS",
    request_body=Schema(
        type=TYPE_OBJECT, required=['name', 'configTypeId', 'data', 'description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="inter1", description="Name of the host configuration"),
            'configTypeId': Schema(type=TYPE_STRING, enum=["g7cIWbcGg", "NH5p4FpGR"],
                                   description="required for consuming openzit API and taking the id of the config type: g7cIWbcGg when using intercept config and NH5p4FpGR when using host config"),
            'data': Schema(type=TYPE_OBJECT, example={'addresses': ['addr.inter1'], 'portRanges': [{'high': 200, 'low': 100}], 'protocols': ['tcp']}, 
                           properties={
                               # Intercept configs
                               "addresses": Schema(type=TYPE_ARRAY, description="List of intercept addresses used for intercept configuration", items=Schema(type=TYPE_STRING)),
                               "portRanges": Schema(type=TYPE_ARRAY, description="List of intercept port ranges used for intercept configuration. It takes two fields: high and low", items=Schema(type=TYPE_OBJECT, properties={
                                   "high": Schema(type=TYPE_INTEGER),
                                   "low": Schema(type=TYPE_INTEGER),
                               })),
                               "protocols": Schema(type=TYPE_ARRAY, description="List of intercept protocols used for intercept configuration", items=Schema(type=TYPE_STRING, enum=['tcp', 'udp'])),
                               # Host configs
                               "address": Schema(type=TYPE_STRING, description="Address used for host configuration"),
                               "port": Schema(type=TYPE_INTEGER, description="Port used for host configuration"),
                               "protocol": Schema(type=TYPE_STRING, enum=["tcp", "udp"], description="List of intercept protocols used for intercept configuration")}),
            'description': Schema(type=TYPE_STRING, description="Description of identity"),
            }
            )
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_configs(request):
    """API to create an intercept or host configurations"""
    try:
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        response = requests.post(PATH_ZTNA_CONFIGS, headers=headers, json=data_without_description, 
                                 verify=False)
        response_dict = json.loads(response.text)
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M")
        if response.status_code == 201:
            payload={"name": data["name"],
                     "description": data.get('Description', None),
                     "date_creation": formatted_now}
            ############### intercept ###############
            if data["configTypeId"] == 'g7cIWbcGg':
                payload['ref_intercept'] = response_dict.get('data', {}).get('id')
                # Correctly accessing protocols from data['data']
                payload['protocol'] = data['data']['protocols'][0] # Fixed to access first protocol
                payload['address'] = data['data']["addresses"][0] # Fixed to access first address
                payload['low'] = data['data']["portRanges"][0]["low"]  # Fixed to access first low port range
                payload['high'] = data['data']["portRanges"][0]["high"]  # Fixed to access first high port range

                # Serialize and save the payload
                serializer_intercept = InterceptConfigsSerializer(data=payload,partial=True)
                if serializer_intercept.is_valid():
                    serializer_intercept.save()
                    return JsonResponse({"message": f"{CONSTANT_INTERCEPT_CONFIGURATION} {SUCCESS_MESSAGES_CREATING}"}, status=200)
                return JsonResponse({"error": serializer_intercept.errors}, status=400)

            ############### host ###############
            else :
                payload['ref_host'] = response_dict.get('data', {}).get('id')
                payload['protocol'] = data['data']['protocol']
                payload['address'] = data['data']["address"]
                payload['port'] = data['data']["port"]
                serializer_host = HostConfigsSerializer(data=payload,partial=True)
                if serializer_host.is_valid():
                    serializer_host.save()
                    return JsonResponse({"message": f"{CONSTANT_HOST_CONFIGURATION} {SUCCESS_MESSAGES_CREATING}"}, status=200)
                return JsonResponse({"error": serializer_host.errors}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_CONFIGURATION}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA INTERCEPT CONFIGURATION",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_intercept_configs(request, id):
    try:
        intercept_config = InterceptConfigs.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        response = requests.delete(f"{PATH_ZTNA_CONFIGS}/{intercept_config.ref_intercept}", headers=headers, verify=False)
        if response.status_code == 200:
            intercept_config.delete()
            return JsonResponse({"message": f"{CONSTANT_INTERCEPT_CONFIGURATION} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_INTERCEPT_CONFIGURATION}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except InterceptConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERCEPT_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA HOST CONFIGURATION",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_host_configs(request, id):
    try:
        host_config = HostConfigs.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        response = requests.delete(f"{PATH_ZTNA_CONFIGS}/{host_config.ref_host}", headers=headers, verify=False)
        if response.status_code == 200:
            host_config.delete()
            return JsonResponse({"message": f"{CONSTANT_HOST_CONFIGURATION} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_HOST_CONFIGURATION}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except HostConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_HOST_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE A ZTNA INTERCEPT CONFIGURATIONS",
    request_body=Schema(
        type=TYPE_OBJECT, required=['name', 'configTypeId', 'data', 'description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="inter1", description="Name of the host configuration"),
                        'configTypeId': Schema(type=TYPE_STRING, enum=["g7cIWbcGg"], 
                                               description="required for consuming openzit API and taking the id of the config type: g7cIWbcGg when using intercept config and NH5p4FpGR when using host config"),
            'data': Schema(type=TYPE_OBJECT, required=['addresses', 'portRanges', 'protocols'], 
                           example={'addresses': ['addr.inter1'], 'portRanges': [{'high': 200, 'low': 100}], 'protocols': ['tcp']}, 
                           properties={
                               "addresses": Schema(type=TYPE_ARRAY, description="List of intercept addresses used for intercept configuration", items=Schema(type=TYPE_STRING)),
                               "portRanges": Schema(type=TYPE_ARRAY, description="List of intercept port ranges used for intercept configuration. It takes two fields: high and low", items=Schema(type=TYPE_OBJECT, properties={
                                   "high": Schema(type=TYPE_INTEGER),
                                   "low": Schema(type=TYPE_INTEGER),
                               "protocols": Schema(type=TYPE_ARRAY, description="List of intercept protocols used for intercept configuration", items=Schema(type=TYPE_STRING, enum=['tcp', 'udp'])),
                               }))}),
            'description': Schema(type=TYPE_STRING, description="Description of identity"),
            }
            )
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_intercept_configs(request, id):
    """API to update an intercept configuration"""
    try:
        intercept = InterceptConfigs.objects.get(id=id)
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        if data["configTypeId"] == 'g7cIWbcGg':
            payload={
                "name": data['name'],
                "protocol": data['data']['protocols'][0],
                "address": data['data']['addresses'][0],
                "low": data['data']['portRanges'][0]["low"],
                "high": data['data']['portRanges'][0]["high"],
                "description": data.get('Description', None)}
            serializer_update_intercept = InterceptSerializerUpdate(intercept,data=payload, partial=True)
            if serializer_update_intercept.is_valid():
                response = requests.put(f"{PATH_ZTNA_CONFIGS}/{intercept}", headers=headers, json=data_without_description, verify=False)
                if response.status_code == 200:
                    serializer_update_intercept.save()
                    return JsonResponse({"message": f"{CONSTANT_INTERCEPT_CONFIGURATION} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
                return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_INTERCEPT_CONFIGURATION}"}, status=400)
            return JsonResponse({"error": list(serializer_update_intercept.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_INTERCEPT_CONFIGURATION}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except InterceptConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERCEPT_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE A ZTNA HOST CONFIGURATIONS",
    request_body=Schema(
        type=TYPE_OBJECT, required=['name', 'configTypeId', 'data', 'description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="inter1", description="Name of the host configuration"),
            'configTypeId': Schema(type=TYPE_STRING, enum=["NH5p4FpGR"], 
            description="required for consuming openzit API and taking the id of the config type: NH5p4FpGR when using host config"),
            'data': Schema(type=TYPE_OBJECT, example={'address': 'addr.host1', 'port': 53, 'protocol': 'tcp'}, 
                           properties={
                               "address": Schema(type=TYPE_STRING, description="Address used for host configuration"),
                               "port": Schema(type=TYPE_INTEGER, description="Port used for host configuration"),
                               "protocol": Schema(type=TYPE_STRING, enum=["tcp", "udp"], description="List of intercept protocols used for intercept configuration")}),
            'description': Schema(type=TYPE_STRING, description="Description of identity"),
            }
            )
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_host_configs(request, id):
    """API to update a host configuration"""
    try:
        host = HostConfigs.objects.get(id=id)
        data = request.data
        print("update host configs=", data)
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        payload={
            "name": data['name'],
            "protocol": data['data']['protocol'],
            "address": data['data']['address'],
            "port": data['data']['port'],
            "description": data.get('Description', None)}
        serializer_update_host = HostSerializerUpdate(host,data=payload, partial=True)
        if serializer_update_host.is_valid():
            response = requests.put(f"{PATH_ZTNA_CONFIGS}/{host}", headers=headers, json=data_without_description, verify=False)
            if response.status_code == 200:
                serializer_update_host.save()
                return JsonResponse({"message": f"{CONSTANT_HOST_CONFIGURATION} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
            return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_HOST_CONFIGURATION}"}, status=400)
        return JsonResponse({"error":  f"{ERROR_MESSAGES_UPDATING} {CONSTANT_HOST_CONFIGURATION}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except HostConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_HOST_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    