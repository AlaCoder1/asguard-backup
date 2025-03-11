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

from backend.ztna.models import HostConfigs, InterceptConfigs, Services
from backend.ztna.constant_variables import CONSTANT_CONTENT_TYPE, PATH_ZTNA_SERVICES
from backend.ztna.serializers import ServicesSerializer, ServicesSerializerUpdate
from backend.ztna.utils import get_ztna_token_from_system


# Constants
CONSTANT_SERVICE = _('Service')
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
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES FROM OPENZITI API",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_services_from_openziti(request):
    """Getting all services existing in system using openziti API"""
    try:
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        response = requests.get(PATH_ZTNA_SERVICES, headers=headers, verify=False)
        response_dict = json.loads(response.text)
        print(response_dict["data"])
        return JsonResponse(response_dict["data"], safe=False)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'},
                     operation_summary="API TO GET LIST OF ALL ZTNA SERVICES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_services(request):
    """Getting all services from database"""
    try:
        if request.method == 'GET':
            services = Services.objects.all().exclude(service_name="strongswan")
            return JsonResponse(list(services.values()), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@swagger_auto_schema(
    'POST', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE A ZTNA SERVICE",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'roleAttributes', 'encryptionRequired', 'configs', 'description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="service1", description="Name of the service"),
            'roleAttributes': Schema(type=TYPE_ARRAY, example=["attr service1"],
                                     description="List of attributes. Actually it takes only 1 attribute",
                                     items=Schema(type=TYPE_STRING)),
            'encryptionRequired': Schema(type=TYPE_BOOLEAN, default=False, description="Encryption requirement"),
            'configs': Schema(type=TYPE_ARRAY, example=["2FX2r0tEv7akrrNedMSQyd", "4t6v4vNkTV18x91wImu03l"],
                                     description="List of configurations: Host and Intercept. It takes the reference of choosed host and intercept configuration",
                                     items=Schema(type=TYPE_STRING)),
            'description': Schema(type=TYPE_STRING, description="Description of service"),
            }
            )
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_services(request):
    """API to create a ztna service"""
    try:
        data = request.data
        datacopy = request.data.copy()
        host = HostConfigs.objects.get(ref_host=data['configs'][1])
        intercept = InterceptConfigs.objects.get(ref_intercept=data['configs'][0])
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        response = requests.post(PATH_ZTNA_SERVICES, headers=headers, json=data_without_description, verify=False)
        response_dict = json.loads(response.text)
        service_id = response_dict.get('data', {}).get('id')
        if response.status_code == 201:
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            payload={"ref_service": service_id,
                     "name": data['name'],
                     "attribute_service": None,
                     "encryption": data['encryptionRequired'],
                     "host_id": host.pk,
                     "intercept_id": intercept.pk,
                     "description": None,
                     "date_creation": formatted_now}
            if data['roleAttributes'][0] != "":
                payload['attribute_service'] = data['roleAttributes'][0]
            if 'Description' in data:
                payload['description'] = data['Description']
            serializer_service = ServicesSerializer(data=payload,partial=True)
            if serializer_service.is_valid():
                serializer_service.save()
                return JsonResponse({"message": f"{CONSTANT_SERVICE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
            return JsonResponse({"error": list(serializer_service.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_SERVICE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except HostConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_HOST_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except InterceptConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERCEPT_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA SERVICE",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_services(request, id):
    """API to delete a ztna service"""
    try:
        service = Services.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        response = requests.delete(f"{PATH_ZTNA_SERVICES}/{service.ref_service}", headers=headers, verify=False)
        if response.status_code == 200:
            service.delete()
            return JsonResponse({"message": f"{CONSTANT_SERVICE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_SERVICE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except Services.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SERVICE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE A ZTNA SERVICE",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'roleAttributes', 'encryptionRequired', 'configs', 'description'],
        properties={
            'name': Schema(type=TYPE_STRING, example="service1", description="Name of the service"),
            'roleAttributes': Schema(type=TYPE_ARRAY, example=["attr service1"],
                                     description="List of attributes. Actually it takes only 1 attribute",
                                     items=Schema(type=TYPE_STRING)),
            'encryptionRequired': Schema(type=TYPE_BOOLEAN, default=False, description="Encryption requirement"),
            'configs': Schema(type=TYPE_ARRAY, example=["2FX2r0tEv7akrrNedMSQyd", "4t6v4vNkTV18x91wImu03l"],
                                     description="List of configurations: Host and Intercept. It takes the reference of choosed host and intercept configuration",
                                     items=Schema(type=TYPE_STRING)),
            'description': Schema(type=TYPE_STRING, description="Description of service"),
            }
            )
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_services(request, id):
    """API to update a ztna service"""
    try:
        services = Services.objects.get(id=id)
        data = request.data
        datacopy = request.data.copy()
        host = HostConfigs.objects.get(ref_host=data['configs'][1])
        intercept = InterceptConfigs.objects.get(ref_intercept=data['configs'][0])
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        payload={
            "name": data['name'],
            "attribute_service": None,
            "encryption": data['encryptionRequired'],
            "host_id": host.pk,
            "intercept_id": intercept.pk,
            "description": None}
        if data['roleAttributes'][0] != "":
            payload['attribute_service'] = data['roleAttributes'][0]
        if 'Description' in data:
            payload['description'] = data['Description']
        serializer_update_service = ServicesSerializerUpdate(services,data=payload, partial=True)
        if serializer_update_service.is_valid():
            response = requests.put(f"{PATH_ZTNA_SERVICES}/{services.ref_service}", headers=headers, json=data_without_description, verify=False)
            if response.status_code == 200:
                serializer_update_service.save()
                return JsonResponse({"message": f"{CONSTANT_SERVICE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
            return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_SERVICE}"}, status=400)
        return JsonResponse({"error": list(serializer_update_service.errors.values())[0][0]}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except Services.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_SERVICE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except HostConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_HOST_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except InterceptConfigs.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERCEPT_CONFIGURATION} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
