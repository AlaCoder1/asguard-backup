from utils.errors_utils import CommandExecutionError
from .utils import change_status_ztna_service, check_host_templates, get_local_domain_from_system, get_status_ztna_service, get_ztna_token_from_system
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated


# Constants
CONSTANT_ZTNA = _('ZTNA')
CONSTANT_ZTNA_TOKEN = _('ZTNA token')
# Success messages
SUCCESS_MESSAGES_STARTING = _("is started")
SUCCESS_MESSAGES_STOPING = _("is stoped")
# Error messages
ERROR_MESSAGES_STARTING = _("System error in starting")
ERROR_MESSAGES_STOPING = _("System error in stoping")
ERROR_MESSAGES_STATUS = _("System error in getting status")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_REQUIRED_START = _("Try to start the service")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET ZTNA TOKEN")
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_ztna_token(request):
    """API to get the ztna token"""
    try:
        token = get_ztna_token_from_system()
        if token:
            return JsonResponse({"data": token}, status=200)
        raise CommandExecutionError
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)
    except CommandExecutionError:
        return JsonResponse({"error": f"{CONSTANT_ZTNA_TOKEN} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET ZTNA SERVICE STATUS")
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def status_ztna(request):
    """API to get ZTNA service status from a script bash"""
    try:
        status = get_status_ztna_service()
        status_templates = check_host_templates()
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
        
    except CommandExecutionError as err:
        print("err= ", str(err))
        return JsonResponse({"error": f"{ERROR_MESSAGES_STATUS} {CONSTANT_ZTNA}"}, status=400)
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


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
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": ERROR_MESSAGES_REQUIRED_START,}, status=400)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET THE LOCAL DOMAIN FOR LINUX OS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_local_domain_linux(request):
    """API to get the local domain for Linux"""
    file_content = get_local_domain_from_system()

    if file_content:
        # Return the file content as a JSON response
        return JsonResponse({'os': 'linux', 'content': file_content})
    return JsonResponse({'error': 'Linux file not found or unreadable'}, status=404)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET THE LOCAL DOMAIN FOR LINUX WINDOWS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_local_domain_windows(request):
    """API to get the local domain for Windows"""

    file_content = get_local_domain_from_system("windows")

    if file_content is not None:
        # Return the file content as a JSON response
        return JsonResponse({'os': 'windows', 'content': file_content})
    return JsonResponse({'error': 'Windows file not found or unreadable'}, status=404)
