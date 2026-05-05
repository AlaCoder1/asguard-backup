import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import TYPE_ARRAY, TYPE_OBJECT, TYPE_STRING, Schema
from datetime import datetime
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from backend.ztna.list_ztna import get_edge_router_policies, get_service_edge_router_policies, get_service_policies
from backend.ztna.models import Identities, Relays, RelaysPolicy, Services, ServicesPolicy, ServicesRelaysPolicy
from backend.ztna.constant_variables import CONSTANT_CONTENT_TYPE, PATH_ZTNA_EDGE_ROUTERS_POLICIES, PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES, PATH_ZTNA_SERVICES_POLICIES
from backend.ztna.serializers import RelaysPolicySerializer, RelaysPolicySerializerUpdate, ServicesPolicySerializer, ServicesPolicySerializerUpdate, ServicesRelaysPolicySerializer, ServicesRelaysPolicySerializerUpdate
from backend.ztna.utils import get_ztna_token_from_system
from django.views.decorators.http import require_http_methods

from backend.ztna.utils_policies import get_router_policy_from_ziti, get_service_policy_from_ziti, get_services_router_policy_from_ziti

# Constants
CONSTANT_EDGE_ROUTER_POLICIE = _('Relay Policy')
CONSTANT_SERVICE_POLICIE = _('Service Policy')
CONSTANT_SERVICE_EDGE_ROUTER_POLICIE = _('Service Relay Policy')
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


# Edge routers policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA EDGE ROUTERS POLICIES FROM OPENZITI API",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_edge_routers_policies_from_openziti(_):
    """Getting all edge routers existing in system using openziti API"""
    try:
        list_router_policies_openziti = get_router_policy_from_ziti()
        return JsonResponse(list_router_policies_openziti, safe=False)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA EDGE ROUTERS POLICIES",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_edge_routers_policies(_):
    """Getting all edge routers from database"""
    list_relay_policy = get_edge_router_policies()
    return JsonResponse(list_relay_policy, safe=False)


@swagger_auto_schema(
    'POST', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN EDGE ROUTER POLICY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'semantic', 'edgeRouterRoles', 'identityRoles', 'Description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="relay policy1", description="Name of the Edge router policy"),
            'semantic': Schema(type=TYPE_STRING, enum=["AllOf", "AnyOf"]),
            'edgeRouterRoles': Schema(type=TYPE_ARRAY, example=["#attr router1"],
                                     description="List of Routers. Actually it takes only 1 router. Every router must start with #",
                                     items=Schema(type=TYPE_STRING)),
            'identityRoles': Schema(type=TYPE_ARRAY, example=["#attr identity1"],
                                    description="List of attributes. Actually it takes only 1 attribute. Every attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'Description': Schema(type=TYPE_STRING, example="Description of Edge Router Policy"),
            }
            )
)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_edge_routers_policies(request):
    """API to create an edge router policie"""
    try:
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        response = requests.post(PATH_ZTNA_EDGE_ROUTERS_POLICIES, headers=headers, json=data_without_description, verify=False)
        response_dict = json.loads(response.text)
        relay_policy_id = response_dict.get('data', {}).get('id')
        if response.status_code == 201:
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            payload={"ref_relay_policy": relay_policy_id,
                     "name": data['name'],
                     "semantic": data['semantic'],
                     "description": None,
                     "relay_id": None,
                     "identity_id": None,
                     "date_creation": formatted_now,
                     }
            relay_att = data['edgeRouterRoles'][0]
            identity_att = data['identityRoles'][0]
            if relay_att.startswith('#'):
                relay_att = relay_att[1:]
                relay = Relays.objects.filter(attribute_relay=relay_att)
                if relay.exists():
                    payload["relay_id"] = relay[0].pk
            if identity_att.startswith('#'):
                identity_att = identity_att[1:]
                identity = Identities.objects.filter(attribute_identitie=identity_att)
                if identity.exists():
                    payload["identity_id"] = identity[0].pk
            if 'Description' in data:
                payload['description'] = data['Description']
            relay_policy_serializer = RelaysPolicySerializer(data=payload)
            if relay_policy_serializer.is_valid():
                relay_policy_serializer.save()
                return JsonResponse({"message": f"{CONSTANT_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
            return JsonResponse({"error": list(relay_policy_serializer.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_EDGE_ROUTER_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA EDGE ROUTER POLICY",)
@api_view(['DELETE'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_edge_routers_policies(_, id):
    try:
        relays_policy = RelaysPolicy.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        response = requests.delete(f"{PATH_ZTNA_EDGE_ROUTERS_POLICIES}/{relays_policy.ref_relay_policy}", headers=headers, verify=False)
        if response.status_code == 200:
            relays_policy.delete()
            return JsonResponse({"message": f"{CONSTANT_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_EDGE_ROUTER_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except RelaysPolicy.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_EDGE_ROUTER_POLICIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    "PUT", responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE AN EDGE ROUTER POLICY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'semantic', 'edgeRouterRoles', 'identityRoles', 'Description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="relay policy1", description="Name of the Edge router policy"),
            'semantic': Schema(type=TYPE_STRING, enum=["AllOf", "AnyOf"]),
            'edgeRouterRoles': Schema(type=TYPE_ARRAY, example=["#attr router1"],
                                     description="List of Routers. Actually it takes only 1 router. Every router must start with #",
                                     items=Schema(type=TYPE_STRING)),
            'identityRoles': Schema(type=TYPE_ARRAY, example=["#attr identity1"],
                                    description="List of attributes. Actually it takes only 1 attribute. Every attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'Description': Schema(type=TYPE_STRING, example="Description of Edge Router Policy"),
            }
            )
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_edge_routers_policies(request, id):
    try:
        relay_policy = RelaysPolicy.objects.get(id=id)
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        payload={"name": data["name"],
                 "semantic": data["semantic"],
                 "Description": None,
                 "relay_attribute": None,
                 "identity_attribute": None
                 }
        if 'Description' in data:
            payload['description'] = data['Description']
        relay_att = data['edgeRouterRoles'][0]
        identity_att = data['identityRoles'][0]
        if relay_att.startswith('#'):
            payload['relay_attribute'] = relay_att[1:]
        if identity_att.startswith('#'):
            payload['identity_attribute'] = identity_att[1:]
        relay = Relays.objects.filter(attribute_relay=payload['relay_attribute'])
        identity = Identities.objects.filter(attribute_identitie=payload['identity_attribute'])
        for ser in relay:
            for id in identity:
                payload['identity_id'] = id.pk
                payload['relay_id'] = ser.pk
                serializer_svc_policy_update = RelaysPolicySerializerUpdate(relay_policy, data=payload, partial=True)
                if serializer_svc_policy_update.is_valid():
                    response = requests.put(f"{PATH_ZTNA_EDGE_ROUTERS_POLICIES}/{relay_policy.ref_relay_policy}", headers=headers, json=data_without_description, verify=False)
                    if response.status_code == 200:
                        serializer_svc_policy_update.save()
                        return JsonResponse({"message": f"{CONSTANT_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
                    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_EDGE_ROUTER_POLICIE}"}, status=400)
                return JsonResponse({"error": list(serializer_svc_policy_update.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_EDGE_ROUTER_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except RelaysPolicy.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_EDGE_ROUTER_POLICIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


# Services policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES POLICIES FROM OPENZITI API",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_services_policies_from_openziti(_):
    """Getting all services policies existing in system using openziti API"""
    try:
        list_services_policies_openziti = get_service_policy_from_ziti()
        return JsonResponse(list_services_policies_openziti, safe=False)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES POLICIES",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services_policies(_):
    """Getting all services from database"""
    list_service_policy = get_service_policies()
    return JsonResponse(list_service_policy, safe=False)


@swagger_auto_schema(
    'POST', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A SERVICE POLICY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'type', 'semantic', 'identityRoles', 'serviceRoles', 'Description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="service policy1", description="Name of the Service policy"),
            'type': Schema(type=TYPE_STRING, enum=["Dial", "Bind"]),
            'semantic': Schema(type=TYPE_STRING, enum=["AllOf", "AnyOf"]),
            'identityRoles': Schema(type=TYPE_ARRAY, example=["#attr identity1"],
                                    description="List of identities attributes. Actually it takes only 1 attribute. Every identity attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'serviceRoles': Schema(type=TYPE_ARRAY, example=["#attr service1"],
                                    description="List of services attributes. Actually it takes only 1 attribute. Every service attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'Description': Schema(type=TYPE_STRING, example="Description of Service Policy"),
            }
            )
)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services_policies(request):
    try:
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        response = requests.post(PATH_ZTNA_SERVICES_POLICIES, headers=headers, json=data_without_description, verify=False)
        response_dict = json.loads(response.text)
        service_policy_id = response_dict.get('data', {}).get('id')
        if response.status_code == 201:
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            payload={"ref_service_policy": service_policy_id,
                     "name": data["name"],
                     "semantic": data["semantic"],
                     "type": data["type"],
                     "description": None,
                     "service_attribute": None,
                     "identity_attribute": None,
                     "date_creation": formatted_now}
            if 'Description' in data:
                payload['description'] = data['Description']
            service_att = data['serviceRoles'][0]
            identity_att = data['identityRoles'][0]
            if service_att.startswith('#'):
                payload['service_attribute'] = service_att[1:]
            if identity_att.startswith('#'):
                payload['identity_attribute'] = identity_att[1:]
            service = Services.objects.filter(attribute_service=payload['service_attribute'])
            identity = Identities.objects.filter(attribute_identitie=payload['identity_attribute'])
            for ser in service:
                for id in identity:
                    payload['service_id'] = ser.pk
                    payload['identity_id'] = id.pk
                    serializer = ServicesPolicySerializer(data=payload, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({"message":f"{CONSTANT_SERVICE_POLICIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
                    return JsonResponse({"error": serializer.errors}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_SERVICE_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA ROUTERS POLICIES",)
@api_view(['DELETE'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_services_policies(_, id):
    try:
        service_policy = ServicesPolicy.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        response = requests.delete(f"{PATH_ZTNA_SERVICES_POLICIES}/{service_policy.ref_service_policy}", headers=headers, verify=False)
        if response.status_code == 200:
            service_policy.delete()
            return JsonResponse({"message": f"{CONSTANT_SERVICE_POLICIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SERVICE_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except ServicesPolicy.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SERVICE_POLICIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    "PUT", responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE A SERVICE POLICY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'type', 'semantic', 'identityRoles', 'serviceRoles', 'Description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="service policy1", description="Name of the Edge router policy"),
            'type': Schema(type=TYPE_STRING, enum=["Dial", "Bind"]),
            'semantic': Schema(type=TYPE_STRING, enum=["AllOf", "AnyOf"]),
            'identityRoles': Schema(type=TYPE_ARRAY, example=["#attr identity1"],
                                    description="List of identities attributes. Actually it takes only 1 attribute. Every identity attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'serviceRoles': Schema(type=TYPE_ARRAY, example=["#attr service1"],
                                    description="List of services attributes. Actually it takes only 1 attribute. Every service attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'Description': Schema(type=TYPE_STRING, example="Description of Service Policy"),
            }
            )
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services_policies(request, id):
    try:
        service_policy = ServicesPolicy.objects.get(id=id)
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        payload={"name": data["name"],
                 "semantic": data["semantic"],
                 "type": data["type"],
                 "description": None,
                 "service_attribute": None,
                 "identity_attribute": None}
        service_att = data['serviceRoles'][0]
        identity_att = data['identityRoles'][0]
        if 'Description' in data:
            payload['description'] = data['Description']
        if service_att.startswith('#'):
            payload['service_attribute'] = service_att[1:]
        if identity_att.startswith('#'):
            payload['identity_attribute'] = identity_att[1:]
        service = Services.objects.filter(attribute_service=payload['service_attribute'])
        identity = Identities.objects.filter(attribute_identitie=payload['identity_attribute'])
        for ser in service:
            for id in identity:
                payload['identity_id'] = id.pk
                payload['service_id'] = ser.pk
                serializer_svc_policy_update = ServicesPolicySerializerUpdate(service_policy, data=payload, partial=True)
                if serializer_svc_policy_update.is_valid():
                    response = requests.put(f"{PATH_ZTNA_SERVICES_POLICIES}/{service_policy.ref_service_policy}", headers=headers, json=data_without_description, verify=False)
                    print("update")
                    print(response.status_code)
                    print(response.text)
                    if response.status_code == 200:
                        serializer_svc_policy_update.save()
                        return JsonResponse({"message": f"{CONSTANT_SERVICE_POLICIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
                    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE_POLICIE}"}, status=400)
                return JsonResponse({"error": list(serializer_svc_policy_update.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except ServicesPolicy.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SERVICE_POLICIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


# Services Edge routers policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES EDGE ROUTERS POLICIES FROM OPENZITI API",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_services_edge_routers_policies_from_openziti(_):
    """Getting all services existing in system using openziti API"""
    try:
        list_service_router_policies_openziti = get_services_router_policy_from_ziti()
        return JsonResponse(list_service_router_policies_openziti, safe=False)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES EDGE ROUTERS POLICIES",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services_edge_routers_policies(_):
    """Getting all services edge routers from database"""
    list_relay_policy = get_service_edge_router_policies()
    return JsonResponse(list_relay_policy, safe=False)


@swagger_auto_schema(
    'POST', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A SERVICE EDGE RELAY POLICY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'semantic', 'edgeRouterRoles', 'identityRoles', 'Description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="service relay policy1", description="Name of the Service Edge router policy"),
            'semantic': Schema(type=TYPE_STRING, enum=["AllOf", "AnyOf"]),
            'edgeRouterRoles': Schema(type=TYPE_ARRAY, example=["#attr router1"],
                                     description="List of Routers. Actually it takes only 1 router. Every router must start with #",
                                     items=Schema(type=TYPE_STRING)),
            'serviceRoles': Schema(type=TYPE_ARRAY, example=["#attr service1"],
                                    description="List of services attributes. Actually it takes only 1 attribute. Every service attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'Description': Schema(type=TYPE_STRING, example="Description of Service Edge Relay Policy"),
            }
            )
)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services_edge_routers_policies(request):
    try:
        data = request.data
        print("data service relay policy= ", data)
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        response = requests.post(PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES, headers=headers, json=data_without_description, verify=False)
        response_dict = json.loads(response.text)
        relay_policy_id = response_dict.get('data', {}).get('id')
        if response.status_code == 201:
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            relay_att = data['edgeRouterRoles'][0]
            service_att = data['serviceRoles'][0]
            payload={"ref_service_relay_policy": relay_policy_id,
                    "name": data["name"],
                    "semantic": data["semantic"],
                    "description": None,
                    "relay_attribute": None,
                    "service_attribute": None,
                    "date_creation": formatted_now}
            if 'Description' in data:
                payload['description'] = data['Description']
            if relay_att.startswith('#'):
                payload['relay_attribute']= relay_att[1:]
            if service_att.startswith('#'):
                payload['service_attribute'] = service_att[1:]
            relay = Relays.objects.filter(attribute_relay=payload['relay_attribute'])
            service = Services.objects.filter(attribute_service=payload['service_attribute'])
            for ser in service:
                for id in relay:
                    payload['service_id'] = ser.pk
                    payload['relay_id'] = id.pk
                    serializer = ServicesRelaysPolicySerializer(data=payload, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({"message": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
                    return JsonResponse({"error": serializer.errors}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_SERVICE_EDGE_ROUTER_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA SERVICES EDGE ROUTERS POLICIES",)
@api_view(['DELETE'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_services_edge_routers_policies(_, id):
    try:
        service_relay_policy = ServicesRelaysPolicy.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        response = requests.delete(f"{PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES}/{service_relay_policy.ref_service_relay_policy}", headers=headers, verify=False)
        if response.status_code == 200:
            service_relay_policy.delete()
            return JsonResponse({"message": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SERVICE_EDGE_ROUTER_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except ServicesRelaysPolicy.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    "PUT", responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE A SERVICE EDGE RELAY POLICY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'semantic', 'edgeRouterRoles', 'identityRoles', 'Description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="service relay policy1", description="Name of the Service Edge router policy"),
            'semantic': Schema(type=TYPE_STRING, enum=["AllOf", "AnyOf"]),
            'edgeRouterRoles': Schema(type=TYPE_ARRAY, example=["#attr router1"],
                                     description="List of Routers. Actually it takes only 1 router. Every router must start with #",
                                     items=Schema(type=TYPE_STRING)),
            'serviceRoles': Schema(type=TYPE_ARRAY, example=["#attr service1"],
                                    description="List of services attributes. Actually it takes only 1 attribute. Every service attribute must start with #",
                                    items=Schema(type=TYPE_STRING)),
            'Description': Schema(type=TYPE_STRING, example="Description of Service Edge Relay Policy"),
            }
            )
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services_edge_routers_policies(request, id):
    try:
        svc_relay_policy = ServicesRelaysPolicy.objects.get(id=id)
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        relay_att = data['edgeRouterRoles'][0]
        service_att = data['serviceRoles'][0]
        payload={"name": data["name"],
                "semantic": data["semantic"],
                "description": None,
                "relay_attribute": None,
                "service_attribute": None}
        if 'Description' in data:
            payload['description'] = data['Description']
        if relay_att.startswith('#'):
            payload['relay_attribute']= relay_att[1:]
        if service_att.startswith('#'):
            payload['service_attribute'] = service_att[1:]
        relay = Relays.objects.filter(attribute_relay=payload['relay_attribute'])
        service = Services.objects.filter(attribute_service=payload['service_attribute'])
        for ser in service:
            for id in relay:
                payload['relay_id']=id.pk
                payload['service_id']=ser.pk
                serializer_svc_policy_update = ServicesRelaysPolicySerializerUpdate(svc_relay_policy,data=payload, partial=True)
                if serializer_svc_policy_update.is_valid():
                    response = requests.put(f"{PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES}/{svc_relay_policy.ref_service_relay_policy}", headers=headers, json=data_without_description, verify=False)
                    if response.status_code == 200:
                        serializer_svc_policy_update.save()
                        return JsonResponse({"message": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
                    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE_EDGE_ROUTER_POLICIE}"}, status=400)
                return JsonResponse({"error": list(serializer_svc_policy_update.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE_EDGE_ROUTER_POLICIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except ServicesRelaysPolicy.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
