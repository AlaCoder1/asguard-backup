import json
from backend.ztna.models import Identities,HostConfigs,InterceptConfigs, Relays, RelaysPolicy, Services, ServicesPolicy, ServicesRelaysPolicy
from backend.ztna.serializers import EnrollementsSerializer, IdentitiesSerializer, IdentitiesSerializerUpdate, InterceptConfigsSerializer,HostConfigsSerializer, RelaySerializerUpdate, RelaysPolicySerializer, RelaysSerializer, ServicesPolicySerializer, ServicesRelaysPolicySerializer, ServicesSerializer
from utils.errors_utils import CommandExecutionError
from .constant_variables import PATH_ZTNA_CONFIGS, PATH_ZTNA_EDGE_ROUTERS_POLICIES, PATH_ZTNA_ENROLLMENTS, PATH_ZTNA_IDENTITIES, PATH_ZTNA_ROUTERS, PATH_ZTNA_SERVICES, PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES, PATH_ZTNA_SERVICES_POLICIES, PATH_ZTNA_TERMINATORS
from .list_ztna import get_identities_from_ziti, get_routers_from_ziti, get_service_edge_router_policies, get_service_policies, get_services, get_terminators
from .utils import change_status_router, change_status_ztna_service, get_Zt_Token, get_status_ztna_service
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.forms.models import model_to_dict
from rest_framework.response import Response
from django.core import serializers


# Constants
CONSTANT_ZTNA = _('ZTNA')
CONSTANT_IDENTITIE = _('Identitie')
CONSTANT_ENROLLMENT = _('Enrollment')
CONSTANT_RELAY = _('Relay')
CONSTANT_CONFIGURATION = _('Configuration')
CONSTANT_SERVICE = _('Service')
CONSTANT_TERMINATOR = _('Terminator')
CONSTANT_EDGE_ROUTER_POLICIE = _('Edge Router Policy')
CONSTANT_SERVICE_POLICIE = _('Service Policy')
CONSTANT_SERVICE_EDGE_ROUTER_POLICIE = _('Service Edge Router Policy')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
SUCCESS_MESSAGES_STARTING = _("is started")
SUCCESS_MESSAGES_STOPING = _("is stoped")
# Error messages
ERROR_MESSAGES_CREATING = _("Error in creating")
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_STARTING = _("Error in starting")
ERROR_MESSAGES_STOPING = _("Error in stoping")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET ZTNA SERVICE STATUS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def status_ztna(request):
    """API to get ZTNA service status from a script bash"""
    try:
        status = get_status_ztna_service()
        if status:
            return JsonResponse({"data": True}, status=200)
        return JsonResponse({"data": False}, status=200)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_ZTNA}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO START ZTNA SERVICE",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_ztna(request):
    """API to start ZTNA service from a script bash"""
    try:
        change_status_ztna_service()
        return JsonResponse({"message": f"{CONSTANT_ZTNA} {SUCCESS_MESSAGES_STARTING}"}, status=200)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_ZTNA}"}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO STOP ZTNA SERVICE",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_ztna(request):
    """API to stop ZTNA service from a script bash"""
    try:
        change_status_ztna_service("stop")
        return JsonResponse({"message": f"{CONSTANT_ZTNA} {SUCCESS_MESSAGES_STOPING}"}, status=200)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_ZTNA}"}, status=400)


################################
########## Identities ##########
################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA IDENTITIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_identities(request):
    list_identities = []
    if request.method == 'GET':
        identities = Identities.objects.all()
        identitie_dict = serializers.serialize("json", identities)
        res = json.loads(identitie_dict)
        for i in range(0, len(res)):
            res[i].pop('model')
            identitie_id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = identitie_id
            list_identities.append(res[i]['fields'])
        
        return JsonResponse(list_identities, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_identities(request):
    payload = {}
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_IDENTITIES, headers=headers, json=data, verify=False)
    response_dict = json.loads(response.text)
    identity_id = response_dict.get('data', {}).get('id')
    if response.status_code == 201:
        payload['ref_identitie'] = identity_id
        payload['name'] = data['name']
        if data['roleAttributes'][0] == "": 
            payload['attribute_identitie'] == None
        else:
            payload['attribute_identitie'] = data['roleAttributes'][0]
        payload['type'] = data['type']
        if 'description' in data:
            payload['description'] = data['description']
        else:
            payload['description'] = None
        payload['isAdmin'] = data['isAdmin']
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M")
        payload['date_creation'] = formatted_now
        serializer_identitie = IdentitiesSerializer(data=payload)
        if serializer_identitie.is_valid():
            serializer_identitie.save()
            return JsonResponse({"message": f"{CONSTANT_IDENTITIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
        return JsonResponse({"error":serializer_identitie.errors}, status=400)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_IDENTITIE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA IDENTITIE",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_identities(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_IDENTITIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_IDENTITIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_IDENTITIE}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_identities(request, id):
    session_id = get_Zt_Token()
    payload={}
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    payload['name'] = data['name']
    if data['roleAttributes'][0] == "": 
        payload['attribute_identitie'] == None
    else:
        payload['attribute_identitie'] = data['roleAttributes'][0]
    payload['type'] = data['type']
    if 'description' in data:
        payload['description'] = data['description']
    else:
        payload['description'] = None
    payload['is_admin'] = data['isAdmin']
    identitie = Identities.objects.get(ref_identitie=id)
    serializer_update_identity = IdentitiesSerializerUpdate(identitie, data=payload, partial=True) 
    if serializer_update_identity.is_valid():
        response = requests.put(f"{PATH_ZTNA_IDENTITIES}/{id}", headers=headers, json=data, verify=False)
        serializer_update_identity.save()
        return JsonResponse({"message": f"{CONSTANT_IDENTITIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_IDENTITIE}"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_enrollments(request):
    payload = {}
    payload_update_identity = {}
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    dt = datetime.fromisoformat(data['expiresAt'][:-1]) 
    date = dt.date()
    time = dt.time()
    payload['date']=date
    payload['time']=time
    payload['type']=data['method']
    identitie = Identities.objects.get(ref_identitie=data['identityId'])
    payload['identitie_id']=identitie.pk
    serializer_enrollement = EnrollementsSerializer(data=payload)
    if serializer_enrollement.is_valid():
        serializer_enrollement.save()
        response = requests.post(PATH_ZTNA_ENROLLMENTS, headers=headers, json=data, verify=False)
        if response.status_code == 201:
            identity_from_ziti = get_identities_from_ziti(identitie.ref_identitie)
            payload_update_identity['token'] = identity_from_ziti['enrollment'][f'{data['method']}']['jwt']
            combined_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
            payload_update_identity['date_expiration'] = combined_datetime
            serializer_update_identitie = IdentitiesSerializerUpdate(identitie, data=payload_update_identity, partial=True) 
            if serializer_update_identitie.is_valid():
                serializer_update_identitie.save()
                return JsonResponse({"message": f"{CONSTANT_ENROLLMENT} {SUCCESS_MESSAGES_CREATING}"}, status=200)
            return JsonResponse(serializer_update_identitie.errors, status=400)
        return JsonResponse({"error":serializer_enrollement.errors}, status=400)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_ENROLLMENT}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA ENROLLMENT",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_enrollments(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_ENROLLMENTS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_ENROLLMENT} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_ENROLLMENT}"}, status=400)


################################
############ Routers ###########
################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA ROUTERS",)
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
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_routers(request):
    payload={}
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_ROUTERS, headers=headers, json=data, verify=False)
    response_dict = json.loads(response.text)
    relay_id = response_dict.get('data', {}).get('id')
    if response.status_code == 201:
        relay_created=get_routers_from_ziti(relay_id)
        payload['ref_relay'] = relay_id
        payload['name'] = data['name']
        payload['online']=relay_created['isOnline']
        payload['verified']=relay_created['isVerified']
        payload['traversal']=data['noTraversal']
        payload['tunneler']=data['isTunnelerEnabled']
        payload['token']=relay_created['enrollmentJwt']
        if data['roleAttributes'][0] == "": 
            payload['attribute_relay'] == None
        else:
            payload['attribute_relay'] = data['roleAttributes'][0]
        if 'description' in data:
            payload['description'] = data['description']
        else:
            payload['description'] = None
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M")
        payload['date_creation'] = formatted_now
        serializer_relay = RelaysSerializer(data=payload)
        if serializer_relay.is_valid():
            serializer_relay.save()
        return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_CREATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_RELAY}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA ROUTERS",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_routers(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_ROUTERS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_RELAY}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_routers(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_ROUTERS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RELAY}"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_routers(request, id):
    try:
        payload={}
        data = request.data
        router_name = data.get("name")
        relay = Relays.objects.get(name=router_name)
        relay_created=get_routers_from_ziti(relay)
        token=''
        if 'enrollmentJwt' in relay_created:
            token = relay_created['enrollmentJwt']
        serializer = RelaySerializerUpdate(relay,data=payload, partial=True)
        if serializer.is_valid():
            change_status_router(router_name, "start", token)
            serializer.save()
            return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_STARTING}"}, status=200)
        return JsonResponse({"error": serializer.errors}, status=400)    
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STARTING} {CONSTANT_RELAY}"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_routers(request, id):
    try:
        payload={}
        data = request.data
        router_name = data.get("name")
        relay = Relays.objects.get(name=router_name)
        payload['online'] = False
        payload['verified'] = True
        serializer = RelaySerializerUpdate(relay,data=payload, partial=True)
        if serializer.is_valid():
            change_status_router(router_name, "stop")
            serializer.save()
            return JsonResponse({"message": f"{CONSTANT_RELAY} {SUCCESS_MESSAGES_STARTING}"}, status=200)
        return JsonResponse({"error": serializer.errors}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_STOPING} {CONSTANT_RELAY}"}, status=400)


################################
############ Configs ###########
################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA CONFIGURATIONS",)
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
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_intercept_configs(request):
    """Getting all configs from database"""
    try:
        if request.method == 'GET':
            intercept_configs = list(map(model_to_dict, InterceptConfigs.objects.all()))   
            return JsonResponse(intercept_configs, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_configs(request):
    payload={}
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_CONFIGS, headers=headers, json=data, verify=False)
    response_dict = json.loads(response.text)
    if response.status_code == 201:
        ############### intercept ###############
        if data["configTypeId"] == 'g7cIWbcGg':
            payload['ref_intercept'] = response_dict.get('data', {}).get('id')
            payload['name'] = data['name']
            
            # Correctly accessing protocols from data['data']
            payload['protocol'] = data['data']['protocols'][0]  # Changed here
            payload['address'] = data['data']["addresses"][0]
            payload['low'] = data['data']["portRanges"][0]["low"]  # Fixed to access first port range
            payload['high'] = data['data']["portRanges"][0]["high"]  # Fixed to access first port range

            # Optional field handling
            payload['description'] = data.get('description', None)
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            payload['date_creation'] = formatted_now
            # Serialize and save the payload
            serializer_intercept = InterceptConfigsSerializer(data=payload)
            if serializer_intercept.is_valid():
                serializer_intercept.save()
                return JsonResponse({"message": f"{CONSTANT_CONFIGURATION} {SUCCESS_MESSAGES_CREATING}"}, status=200)
            return JsonResponse({"error": serializer_intercept.errors}, status=400)

        ############### host ###############
        else :
            payload['ref_host'] = response_dict.get('data', {}).get('id')
            payload['name'] = data['name']
            payload['protocol'] = data['data']['protocol']  
            payload['address'] = data['data']["address"]
            payload['port'] = data['data']["port"] 
            payload['description'] = data.get('description', None)
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            payload['date_creation'] = formatted_now
            serializer_host = HostConfigsSerializer(data=payload)
            if serializer_host.is_valid():
                serializer_host.save()
                return JsonResponse({"message": f"{CONSTANT_CONFIGURATION} {SUCCESS_MESSAGES_CREATING}"}, status=200)
            return JsonResponse({"error": serializer_host.errors}, status=400)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_CONFIGURATION}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA CONFIGURATION",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_configs(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_CONFIGS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_CONFIGURATION} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_CONFIGURATION}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_configs(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_CONFIGS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_CONFIGURATION} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_CONFIGURATION}"}, status=400)


################################
########### Services ###########
################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services(request):
    """Getting all services from database"""
    try:
        if request.method == 'GET':
            services = Services.objects.all()
            return JsonResponse(list(services.values()), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services(request):
    payload={}
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_SERVICES, headers=headers, json=data, verify=False)
    response_dict = json.loads(response.text)
    service_id = response_dict.get('data', {}).get('id')
    if response.status_code == 201:
        payload['ref_service'] = service_id
        payload['name'] = data['name']
        if data['roleAttributes'][0] == "": 
            payload['attribute_service'] == None
        else:
            payload['attribute_service'] = data['roleAttributes'][0]
        payload['encryption'] = data['encryptionRequired']
        host = HostConfigs.objects.get(ref_host=data['configs'][1])
        payload['host_id']=host.pk
        intercept = InterceptConfigs.objects.get(ref_intercept=data['configs'][0])
        payload['intercept_id']=intercept.pk
        if 'description' in data:
            payload['description'] = data['description']
        else:
            payload['description'] = None
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M")
        payload['date_creation'] = formatted_now
        serializer_service = ServicesSerializer(data=payload)
        if serializer_service.is_valid():
            serializer_service.save()
            return JsonResponse({"message": f"{CONSTANT_SERVICE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
        return JsonResponse({"error":serializer_service.errors}, status=400)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_SERVICE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA SERVICE",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_services(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_SERVICES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_SERVICE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SERVICE}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_SERVICES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_SERVICE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE}"}, status=400)


################################
########## Terminators #########
################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA TERMINATORS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_terminators(request):
    """Getting all terminators from database"""
    list_terminators = []
    if (request.method == 'GET'):
        list_terminators = get_terminators()
    return JsonResponse(list_terminators, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_terminators(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_TERMINATORS, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": f"{CONSTANT_TERMINATOR} {SUCCESS_MESSAGES_CREATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_TERMINATOR}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA TERMINATOR",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_terminators(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_TERMINATORS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_TERMINATOR} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_TERMINATOR}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_terminators(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_TERMINATORS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_TERMINATOR} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_TERMINATOR}"}, status=400)


################################
########### Policies ###########
################################

# Edge routers policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA EDGE ROUTERS POLICIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_edge_routers_policies(request):
    """Getting all edge routers from database"""
    try:
        if request.method == 'GET':
            relay_policy = RelaysPolicy.objects.all()
            return JsonResponse(list(relay_policy.values()), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_edge_routers_policies(request):
    session_id = get_Zt_Token()
    payload={}
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_EDGE_ROUTERS_POLICIES, headers=headers, json=data, verify=False)
    response_dict = json.loads(response.text)
    relay_policy_id = response_dict.get('data', {}).get('id')
    if response.status_code == 201:
        payload['ref_relay_policy'] = relay_policy_id
        payload['name'] = data['name']
        payload['semantique'] = data['semantic']
        if 'description' in data:
            payload['description'] = data['description']
        else:
            payload['description'] = None
        relay_att=data['edgeRouterRoles'][0]
        identity_att=data['identityRoles'][0]
        if relay_att.startswith('#'):
            cleaned_relay_att= relay_att[1:]
        if identity_att.startswith('#'):
            cleaned_identity_att= identity_att[1:]
        payload['relay_attribute']=cleaned_relay_att
        payload['identity_attribute']=cleaned_identity_att
        relay = Relays.objects.get(attribute_relay=payload['relay_attribute'])
        identity = Identities.objects.get(attribute_identitie=payload['identity_attribute'])
        payload['identity_id']=identity.pk
        payload['relay_id']=relay.pk
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M")
        payload['date_creation'] = formatted_now
        serializer = RelaysPolicySerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
        return JsonResponse({"message": f"{CONSTANT_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_EDGE_ROUTER_POLICIE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA EDGE ROUTERS POLICIES",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_edge_routers_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_EDGE_ROUTERS_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_EDGE_ROUTER_POLICIE}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_edge_routers_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_EDGE_ROUTERS_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_EDGE_ROUTER_POLICIE}"}, status=400)


# Services policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES POLICIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services_policies(request):
    """Getting all services from database"""
    try:
        if request.method == 'GET':
            service_policy = ServicesPolicy.objects.all()
            return JsonResponse(list(service_policy.values()), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services_policies(request):
    session_id = get_Zt_Token()
    payload={}
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_SERVICES_POLICIES, headers=headers, json=data, verify=False)
    response_dict = json.loads(response.text)
    service_policy_id = response_dict.get('data', {}).get('id')
    if response.status_code == 201:
        payload['ref_service_policy'] = service_policy_id
        payload['name'] = data['name']
        payload['semantique'] = data['semantic']
        payload['type'] = data['type']
        if 'description' in data:
            payload['description'] = data['description']
        else:
            payload['description'] = None
        Service_att=data['serviceRoles'][0]
        identity_att=data['identityRoles'][0]
        if Service_att.startswith('#'):
            cleaned_Service_att= Service_att[1:]
        if identity_att.startswith('#'):
            cleaned_identity_att= identity_att[1:]
        payload['service_attribute']=cleaned_Service_att
        payload['identity_attribute']=cleaned_identity_att
        service = Services.objects.get(attribute_service=payload['service_attribute'])
        identity = Identities.objects.get(attribute_identitie=payload['identity_attribute'])
        payload['identity_id']=identity.pk
        payload['service_id']=service.pk
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M")
        payload['date_creation'] = formatted_now
        serializer = ServicesPolicySerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
        return JsonResponse({"message":f"{CONSTANT_SERVICE_POLICIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_SERVICE_POLICIE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA ROUTERS POLICIES",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_services_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_SERVICES_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_SERVICE_POLICIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SERVICE_POLICIE}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_SERVICES_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_SERVICE_POLICIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE_POLICIE}"}, status=400)

# Services Edge routers policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES EDGE ROUTERS POLICIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services_edge_routers_policies(request):
    """Getting all services edge routers from database"""
    try:
        if request.method == 'GET':
            service_relay_policy = ServicesRelaysPolicy.objects.all()
            return JsonResponse(list(service_relay_policy.values()), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services_edge_routers_policies(request):
    session_id = get_Zt_Token()
    payload={}
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES, headers=headers, json=data, verify=False)
    response_dict = json.loads(response.text)
    relay_policy_id = response_dict.get('data', {}).get('id')
    if response.status_code == 201:
        payload['ref_service_relay_policy'] = relay_policy_id
        payload['name'] = data['name']
        payload['semantique'] = data['semantic']
        if 'description' in data:
            payload['description'] = data['description']
        else:
            payload['description'] = None
        relay_att=data['edgeRouterRoles'][0]
        Service_att=data['serviceRoles'][0]
        if relay_att.startswith('#'):
            cleaned_relay_att= relay_att[1:]
        if Service_att.startswith('#'):
            cleaned_Service_att= Service_att[1:]
        payload['relay_attribute']=cleaned_relay_att
        payload['service_attribute']=cleaned_Service_att
        relay = Relays.objects.get(attribute_relay=payload['relay_attribute'])
        service = Services.objects.get(attribute_service=payload['service_attribute'])
        payload['service_id']=service.pk
        payload['relay_id']=relay.pk
        now = datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M")
        payload['date_creation'] = formatted_now
        serializer = ServicesRelaysPolicySerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
        return JsonResponse({"message": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_SERVICE_EDGE_ROUTER_POLICIE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE A ZTNA SERVICES EDGE ROUTERS POLICIES",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_services_edge_routers_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}
    data = request.data
    response = requests.delete(f"{PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SERVICE_EDGE_ROUTER_POLICIE}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services_edge_routers_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": f"{CONSTANT_SERVICE_EDGE_ROUTER_POLICIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE_EDGE_ROUTER_POLICIE}"}, status=400)
