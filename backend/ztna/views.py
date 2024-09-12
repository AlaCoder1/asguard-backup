from backend.ztna.constant_variables import PATH_ZTNA_IDENTITIES
from.utils import get_Zt_Token  
from django.http import JsonResponse
import requests
import json
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated


BASE_URL = "https://localhost:1280/edge/management/v1/"


def get_data(request, endpoint):
    url = BASE_URL + endpoint
    session_id = get_Zt_Token()
    headers = {"zt-session": session_id}

    params = {
        "limit": 100,
    }
    
    response = requests.get(url, headers=headers, params=params,verify=False)

    if response.status_code == 200:
        data = response.json()
        corrected_data = json.dumps(data)
        return JsonResponse({"message": corrected_data}, status=201)
    return JsonResponse({"error": "Error in getting identites data"}, status=400)


########## Identities ##########
def get_identities(request):
    endpoint = "identities"
    return get_data(request, endpoint)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_identities(request):
    session_id = get_Zt_Token()
    print("session_id= ", session_id)
    headers = {"zt-session": session_id, "Content-Type": "application/json"}
    data = request.data
    response = requests.post(BASE_URL + "identities", headers=headers, json=data)
    print(response.status_code)
    print(response.text)
    if response.status_code == 201:
        return JsonResponse({"message": "ZTNA identities is added"}, status=200)
    return JsonResponse({"error": "Error in adding ZTNA identities"}, status=400)


def get_routers(request):
    endpoint = "edge-routers"
    return get_data(request, endpoint)


def get_configs(request):
    endpoint = "configs"
    return get_data(request, endpoint)


def get_services(request):
    endpoint = "services"
    return get_data(request, endpoint)


def get_terminators(request):
    endpoint = "terminators"
    return get_data(request, endpoint)


def get_edge_router_policies(request):
    endpoint = "edge-router-policies"
    return get_data(request, endpoint)


def get_service_policies(request):
    endpoint = "service-policies"
    return get_data(request, endpoint)


def get_service_edge_router_policies(request):
    endpoint = "service-edge-router-policies"
    return get_data(request, endpoint)
