from utils.constant_variables import ERROR_MESSAGES_START, ERROR_MESSAGES_STOP, SUCCESS_MESSAGES_START, SUCCESS_MESSAGES_STOP
from utils.errors_utils import CommandExecutionError
from .constant_variables import CONSTANT_ZTNA, PATH_ZTNA_CONFIGS, PATH_ZTNA_EDGE_ROUTERS_POLICIES, PATH_ZTNA_ENROLLMENTS, PATH_ZTNA_IDENTITIES, PATH_ZTNA_ROUTERS, PATH_ZTNA_SERVICES, PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES, PATH_ZTNA_SERVICES_POLICIES, PATH_ZTNA_TERMINATORS
from .list_ztna import get_configs, get_edge_router_policies, get_identities, get_routers, get_service_edge_router_policies, get_service_policies, get_services, get_terminators
from .utils import change_status_ztna_service, get_Zt_Token, start_router, stop_router  
from django.http import JsonResponse
import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO START ZTNA SERVICE",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_ztna(request):
    """API to satrt ZTNA service from a script bash"""
    try:
        change_status_ztna_service()
        return JsonResponse({"message": SUCCESS_MESSAGES_START.format(CONSTANT_ZTNA, "")}, status=200)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_START.format(CONSTANT_ZTNA, "")}, status=400)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO STOP ZTNA SERVICE",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_ztna(request):
    """API to satrt ZTNA service from a script bash"""
    try:
        change_status_ztna_service("stop")
        return JsonResponse({"message": SUCCESS_MESSAGES_STOP.format(CONSTANT_ZTNA, "")}, status=200)
        
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STOP.format(CONSTANT_ZTNA, "")}, status=400)


################################
########## Identities ##########
################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA IDENTITIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_identities(request):
    """Getting all identities from database"""
    list_identities = []
    if (request.method == 'GET'):
        list_identities = get_identities()
    return JsonResponse(list_identities, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_identities(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_IDENTITIES, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA identities is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA identities"}, status=400)


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
        return JsonResponse({"message": "ZTNA identities is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA identities"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_identities(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_IDENTITIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA identities is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA identities"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_enrollments(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_ENROLLMENTS, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA enrollment is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA enrollment"}, status=400)


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
        return JsonResponse({"message": "ZTNA enrollment is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA enrollment"}, status=400)


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
    list_routers = []
    if (request.method == 'GET'):
        list_routers = get_routers()
    return JsonResponse(list_routers, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_routers(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_ROUTERS, headers=headers, json=data, verify=False)
    print(response.text)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA routers is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA routers"}, status=400)


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
        return JsonResponse({"message": "ZTNA routers is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA routers"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_routers(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_ROUTERS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA routers is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA routers"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_routers(request, id):
    try:
        session_id = get_Zt_Token()
        headers = {"zt-session": session_id, "Content-Type": "application/json"}
        data = request.data
        router_name = data.get("name")
        token = data.get("token")
        start_router(router_name, token)
        return JsonResponse({"message": "ZTNA Router is started"}, status=200)
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_START.format(CONSTANT_ZTNA, "Router")}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def stop_routers(request, id):
    try:
        session_id = get_Zt_Token()
        headers = {"zt-session": session_id, "Content-Type": "application/json"}
        data = request.data
        router_name = data.get("name")
        stop_router(router_name)
        return JsonResponse({"message": "ZTNA Router is stoped"}, status=200)
    except CommandExecutionError:
        return JsonResponse({"error": ERROR_MESSAGES_STOP.format(CONSTANT_ZTNA, "Router")}, status=400)


################################
############ Configs ###########
################################
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA CONFIGURATIONS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_configs(request):
    """Getting all configs from database"""
    list_configs = []
    if (request.method == 'GET'):
        list_configs = get_configs()
    return JsonResponse(list_configs, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_configs(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_CONFIGS, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA configs is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA configs"}, status=400)


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
        return JsonResponse({"message": "ZTNA configs is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA configs"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_configs(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_CONFIGS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA configs is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA configs"}, status=400)


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
    list_services = []
    if (request.method == 'GET'):
        list_services = get_services()
    return JsonResponse(list_services, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_SERVICES, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA services is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA services"}, status=400)


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
        return JsonResponse({"message": "ZTNA services is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA services"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_SERVICES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA services is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA services"}, status=400)


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
        return JsonResponse({"message": "ZTNA terminators is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA terminators"}, status=400)


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
        return JsonResponse({"message": "ZTNA terminators is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA terminators"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_terminators(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_TERMINATORS}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA terminators is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA terminators"}, status=400)


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
    list_edge_routers_policies = []
    if (request.method == 'GET'):
        list_edge_routers_policies = get_edge_router_policies()
    return JsonResponse(list_edge_routers_policies, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_edge_routers_policies(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_EDGE_ROUTERS_POLICIES, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA edge routers policies is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA edge routers policies"}, status=400)


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
        return JsonResponse({"message": "ZTNA edge routers policies is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA edge routers policies"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_edge_routers_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_EDGE_ROUTERS_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA edge routers policies is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA edge routers policies"}, status=400)


# Services policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES POLICIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services_policies(request):
    """Getting all services from database"""
    list_services_policies = []
    if (request.method == 'GET'):
        list_services_policies = get_service_policies()
    return JsonResponse(list_services_policies, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services_policies(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_SERVICES_POLICIES, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA services policies is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA services policies"}, status=400)


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
        return JsonResponse({"message": "ZTNA services policies is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA services policies"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_SERVICES_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA services policies is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA services policies"}, status=400)

# Services Edge routers policies
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES EDGE ROUTERS POLICIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services_edge_routers_policies(request):
    """Getting all services edge routers from database"""
    list_services_edge_routers_policies = []
    if (request.method == 'GET'):
        list_services_edge_routers_policies = get_service_edge_router_policies()
    return JsonResponse(list_services_edge_routers_policies, safe=False)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services_edge_routers_policies(request):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES, headers=headers, json=data, verify=False)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA services edge routers policies is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA services edge routers policies"}, status=400)


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
        return JsonResponse({"message": "ZTNA services edge routers policies is deleted"}, status=200)
    return JsonResponse({"error": "Error in deleting ZTNA services edge routers policies"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services_edge_routers_policies(request, id):
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.put(f"{PATH_ZTNA_SERVICES_EDGE_ROUTERS_POLICIES}/{id}", headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return JsonResponse({"message": "ZTNA services edge routers policies is updated"}, status=200)
    return JsonResponse({"error": "Error in updating ZTNA services edge routers policies"}, status=400)
