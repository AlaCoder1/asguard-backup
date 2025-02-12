import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import TYPE_ARRAY, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, Schema
from datetime import datetime
from django.core import serializers
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

from backend.ztna.models import Identities
from backend.ztna.constant_variables import CONSTANT_CONTENT_TYPE, PATH_ZTNA_ENROLLMENTS, PATH_ZTNA_IDENTITIES
from backend.ztna.serializers import EnrollementsSerializer, IdentitiesSerializer, IdentitiesSerializerUpdate
from backend.ztna.utils import get_ztna_token_from_system
from backend.ztna.utils_identities import get_identitie_from_ziti


# Constants
CONSTANT_IDENTITIE = _('Identity')
CONSTANT_ENROLLMENT = _('Enrollment')
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
                     operation_summary="API TO GET LIST OF ALL ZTNA IDENTITIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_identities(request):
    """API to get the ZTNA identites"""
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


@swagger_auto_schema(
    'POST', responses={201: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN IDENTITY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'type', 'isAdmin', 'roleAttributes', 'description', 'os'],
        properties={
            'name': Schema(type=TYPE_STRING, example="identity1", description="Name of the identity"),
            'type': Schema(type=TYPE_STRING, enum=["User"], description="required for consuming openzit API and taking only User"),
            'isAdmin': Schema(type=TYPE_BOOLEAN, default=False, description="required for consuming openzit API and taking only False"),
            'roleAttributes': Schema(type=TYPE_ARRAY, example=["attr ident1"],
                                     description="List of attributes. Actually it takes only 1 attribute",
                                     items=Schema(type=TYPE_STRING)),
            'description': Schema(type=TYPE_STRING, example="Description of identity"),
            'os': Schema(type=TYPE_STRING, enum=['windows', 'linux'], description="OS used for identity"),
            }
            )
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_identities(request):
    """API to create a ZTNA identity"""
    try:
        data = request.data
        datacopy = request.data.copy()
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data_without_description = {key: value for key, value in datacopy.items() if key not in ['Description', 'os']}
        response = requests.post(PATH_ZTNA_IDENTITIES, headers=headers, json=data_without_description, verify=False)
        response_dict = json.loads(response.text)
        identity_id = response_dict.get('data', {}).get('id')
        if response.status_code == 201:
            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M")
            payload = {"ref_identitie": identity_id,
                       "name": data["name"],
                       "attribute_identitie": None,
                       "description": None,
                       "type": data["type"],
                       "isAdmin": data["isAdmin"],
                       "os": data["os"],
                       "date_creation": formatted_now
                       }
            if data['roleAttributes'][0] != "":
                payload['attribute_identitie'] = data['roleAttributes'][0]
            if 'Description' in data:
                payload['description'] = data['Description']
            serializer_identitie = IdentitiesSerializer(data=payload, partial=True)
            if serializer_identitie.is_valid():
                serializer_identitie.save()
                return JsonResponse({"message": f"{CONSTANT_IDENTITIE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
            return JsonResponse({"error": list(serializer_identitie.errors.values())[0][0]}, status=400)
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_IDENTITIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'deleted', 400: 'Bad Request'},
                     operation_summary="API TO DELETE A ZTNA IDENTITIE",)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_identities(request, id):
    """API to delete a ZTNA identity"""
    try:
        identitie = Identities.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id}
        response = requests.delete(f"{PATH_ZTNA_IDENTITIES}/{identitie.ref_identitie}", headers=headers, verify=False)
        if response.status_code == 200:
            identitie.delete()
            return JsonResponse({"message": f"{CONSTANT_IDENTITIE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_IDENTITIE}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except Identities.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IDENTITIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PATCH', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE AN IDENTITY",
    request_body=Schema(
        type=TYPE_OBJECT, required=[
            'name', 'type', 'isAdmin', 'roleAttributes', 'description', 'os'],
        properties={
            'name': Schema(type=TYPE_STRING, example="identity1", description="Name of the identity"),
            'type': Schema(type=TYPE_STRING, enum=["User"], description="required for consuming openzit API and taking only User"),
            'isAdmin': Schema(type=TYPE_BOOLEAN, default=False, description="required for consuming openzit API and taking only False"),
            'roleAttributes': Schema(type=TYPE_ARRAY, example=["attr ident1"],
                                     description="List of attributes. Actually it takes only 1 attribute",
                                     items=Schema(type=TYPE_STRING)),
            'description': Schema(type=TYPE_STRING, example="Description of identity"),
            'os': Schema(type=TYPE_STRING, enum=['windows', 'linux'], description="OS used for identity"),
            }
            )
)
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_identities(request, id):
    """API to update a ZTNA identity"""
    try:
        identitie = Identities.objects.get(id=id)
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        data = request.data
        datacopy = request.data.copy()
        data_without_description = {key: value for key, value in datacopy.items() if key != 'Description'}
        payload = {"name": data["name"],
                   "attribute_identitie": None,
                   "description": None,
                   "type": data["type"],
                   "isAdmin": data["isAdmin"],
                   "os": data["os"],
                   }
        if data['roleAttributes'][0] != "":
            payload['attribute_identitie'] = data['roleAttributes'][0]
        if 'Description' in data:
            payload['description'] = data['Description']
        serializer_update_identity = IdentitiesSerializerUpdate(identitie, data=payload, partial=True)
        if serializer_update_identity.is_valid():
            response = requests.patch(f"{PATH_ZTNA_IDENTITIES}/{identitie}", headers=headers, json=data_without_description, verify=False)
            if response.status_code == 200:
                serializer_update_identity.save()
                return JsonResponse({"message": f"{CONSTANT_IDENTITIE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
            return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_IDENTITIE}"}, status=400)
        return JsonResponse({"error": list(serializer_update_identity.errors.values())[0][0]}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except Identities.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IDENTITIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN ENROLLMENT",
    request_body=Schema(
        type=TYPE_OBJECT, required=['expiresAt', 'method', 'identityId'],
        properties={
            'expiresAt': Schema(type=TYPE_STRING, example="2026-01-24T11:47:00Z", description="Expiration date in format of YYYY-MM-DDTHH:MM:SSZ"),
            'method': Schema(type=TYPE_STRING, enum=["ott"], description="required for consuming openzit API and taking only ott"),
            'identityId': Schema(type=TYPE_STRING, example="13A86xh-C", description="Openziti's identity id, mentionned with ref_identitie in our database"),
            }
            )
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_enrollments(request):
    """API to create an enrollment for a ZTNA identite"""
    try:
        data = request.data
        identitie = Identities.objects.get(ref_identitie=data['identityId'])
        session_id = get_ztna_token_from_system()
        headers = {"zt-session": session_id, "Content-Type": CONSTANT_CONTENT_TYPE}
        dt = datetime.fromisoformat(data['expiresAt'][:-1])
        date = dt.date()
        time = dt.time()
        payload = {"date": date, "time": time, "type": data['method'], "identitie_id": identitie.pk}
        payload_update_identity = {}
        serializer_enrollement = EnrollementsSerializer(data=payload)
        if serializer_enrollement.is_valid():
            serializer_enrollement.save()
            response = requests.post(PATH_ZTNA_ENROLLMENTS, headers=headers, json=data, verify=False)
            if response.status_code == 201:
                identity_from_ziti = get_identitie_from_ziti(identitie.ref_identitie)
                payload_update_identity['token'] = identity_from_ziti['enrollment'][f'{data['method']}']['jwt']
                combined_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
                payload_update_identity['date_expiration'] = combined_datetime
                serializer_update_identitie = IdentitiesSerializerUpdate(identitie, data=payload_update_identity, partial=True)
                if serializer_update_identitie.is_valid():
                    serializer_update_identitie.save()
                    return JsonResponse({"message": f"{CONSTANT_ENROLLMENT} {SUCCESS_MESSAGES_CREATING}"}, status=200)
                return JsonResponse({"error": list(serializer_update_identitie.errors.values())[0][0]}, status=400)
            return JsonResponse({"error":f"{ERROR_MESSAGES_CREATING} {CONSTANT_ENROLLMENT}"}, status=400)
        return JsonResponse({"error": list(serializer_enrollement.errors.values())[0][0]}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except Identities.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_IDENTITIE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
