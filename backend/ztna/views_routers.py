import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import TYPE_ARRAY, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, Schema
from datetime import datetime
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from backend.ztna.models import Relays
from backend.ztna.constant_variables import CONSTANT_CONTENT_TYPE, PATH_ZTNA_ROUTERS
from backend.ztna.serializers import RelaysSerializer, RelaysSerializerUpdate
from backend.ztna.utils import get_ztna_token_from_system, get_status_ztna_service
from backend.ztna.utils_routers import change_ports_router_yaml_file, change_status_router, create_router, delete_router, get_router_from_ziti, get_status_router_from_system, update_router_in_system
from utils.errors_utils import CommandExecutionError


# Constants
CONSTANT_RELAY = _('Relay')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
SUCCESS_MESSAGES_STARTING = _("is started")
SUCCESS_MESSAGES_STOPING = _("is stoped")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UPDATING = _("System error in updating")
ERROR_MESSAGES_STARTING = _("System error in starting")
ERROR_MESSAGES_STOPING = _("System error in stoping")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_REQUIRED_START = _("Try to start the service")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA ROUTERS")
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_routers(request):
    """Getting all routers from database"""
    try:
        if request.method == 'GET':
            relays = Relays.objects.all()
            return JsonResponse(list(relays.values()), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@swagger_auto_schema(
    'POST', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A ZTNA ROUTER",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'noTraversal', 'isTunnelerEnabled', 'roleAttributes', 'description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="router1.relay", description="Name of the router in format of router_name.relay"),
            'noTraversal': Schema(type=TYPE_BOOLEAN, default=False),
            'isTunnelerEnabled': Schema(type=TYPE_BOOLEAN, default=True, description="required for consuming openzit API and taking only True"),
            'roleAttributes': Schema(type=TYPE_ARRAY, example=["attr router1"],
                                     description="List of attributes. Actually it takes only 1 attribute",
                                     items=Schema(type=TYPE_STRING)),
            'description': Schema(type=TYPE_STRING, example="Description of Router"),
            }
            )
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_routers(request):
    """API to create a relay"""
    try:
        data = request.data
        print("data routers= ", data)
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        response = requests.post(PATH_ZTNA_ROUTERS, headers=headers, json=data_without_description, verify=False)
        response_dict = json.loads(response.text)
        relay_id = response_dict.get('data', {}).get('id')
        if response.status_code == 201:
            relay_created=get_router_from_ziti(relay_id)
            payload={
                "ref_relay": relay_id,
                "name": data['name'],
                "online": relay_created['isOnline'],
                "verified": relay_created['isVerified'],
                "traversal": data['noTraversal'],
                "tunneler": data['isTunnelerEnabled'],
                "token": relay_created['enrollmentJwt'],
                "attribute_relay": None,
                "description": None,
            }
            if data['roleAttributes'][0] != "":
                payload['attribute_relay'] = data['roleAttributes'][0]
            if 'Description' in data:
                payload['description'] = data['Description']
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            payload['date_creation'] = formatted_now
            serializer_relay = RelaysSerializer(data=payload,partial=True)
            if serializer_relay.is_valid():
                saved_instance=serializer_relay.save()
                create_router(payload['name'],payload['token'])
                created_id = saved_instance.id
                change_ports_router_yaml_file(payload['name'],created_id)
                return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_CREATING}"}, status=200)
            return JsonResponse({"error": list(serializer_relay.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_RELAY}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA RELAY",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_routers(request, id):
    """API to delete a relay"""
    try:
        relay = Relays.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        # Stop relay before deleting
        change_status_router(relay.name, "stop")
        response = requests.delete(f"{PATH_ZTNA_ROUTERS}/{relay.ref_relay}", headers=headers, 
                                   verify=False)
        if response.status_code == 200:
            relay.delete()
            delete_router(relay.name)
            return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_RELAY}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except Relays.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_RELAY} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE A ZTNA ROUTER",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'noTraversal', 'isTunnelerEnabled', 'roleAttributes', 'description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="router1.relay", description="Name of the router in format of router_name.relay"),
            'noTraversal': Schema(type=TYPE_BOOLEAN, default=False),
            'isTunnelerEnabled': Schema(type=TYPE_BOOLEAN, default=True, description="required for consuming openzit API and taking only True"),
            'roleAttributes': Schema(type=TYPE_ARRAY, example=["attr router1"],
                                     description="List of attributes. Actually it takes only 1 attribute",
                                     items=Schema(type=TYPE_STRING)),
            'description': Schema(type=TYPE_STRING, example="Description of Router"),
            }
            )
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_routers(request, id):
    """API to update a relay"""
    try:
        relay = Relays.objects.get(id=id)
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        payload={"name": data["name"],
                "traversal": data["noTraversal"],
                "tunneler": data["isTunnelerEnabled"],
                "attribute_relay": None,
                "description": None,
                }
        if data['roleAttributes'][0] != "":
            payload['attribute_relay'] = data['roleAttributes'][0]
        if 'Description' in data:
            payload['description'] = data['Description']
        serializer_update_relay = RelaysSerializerUpdate(relay, data=payload, partial=True)
        if serializer_update_relay.is_valid():
            response = requests.put(f"{PATH_ZTNA_ROUTERS}/{relay}", headers=headers, json=data_without_description, verify=False)
            if response.status_code == 200:
                update_router_in_system(relay.name, payload['name'])
                serializer_update_relay.save()
                return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
            return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RELAY}"}, status=400)
        return JsonResponse({"error": list(serializer_update_relay.errors.values())[0][0]}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RELAY}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START}, status=400)
    except Relays.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_RELAY} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO START A ZTNA ROUTER")
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_routers(request, id):
    try:
        relay = Relays.objects.get(id=id)
        router_status = get_status_router_from_system(relay.name)
        status = get_status_ztna_service()
        if ("Router is not running" in router_status) and (status):
            change_status_router(relay.name, "start")
            return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_STARTING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_RELAY}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_RELAY}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO STOP A ZTNA ROUTER")
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_routers(request, id):
    try:
        relay = Relays.objects.get(id=id)
        router_status = get_status_router_from_system(relay.name)
        status = get_status_ztna_service()
        if ("Router is not running" not in router_status) and (status):
            change_status_router(relay.name, "stop")
            return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_STOPING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_RELAY}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_RELAY}"}, status=400)
