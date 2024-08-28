import json
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.core import serializers
from backend.managementLogs.functions import get_logs_sys
from backend.managementLogs.models import LogrotateData, LogsData
from django.http import JsonResponse
import gzip
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_logs_data(request):
    """API to get the last 1000 logs from the database"""
    if request.method == 'GET':
        list_logs = []
        logs_object = LogsData.objects.all().order_by('-id')[:1000]
        logs = serializers.serialize("json", logs_object)
        res = json.loads(logs)
        for log in res:
            log['fields']['id'] = log["pk"]
            list_logs.append(log['fields'])
        return JsonResponse({"data": list_logs})
    
    
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def download_logs_data(request):
    """API to get data to download it into file"""
    if request.method == 'GET':
        logs_data=get_logs_sys()
        return JsonResponse({"data": logs_data})
    
    
    
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'service',
            openapi.IN_PATH,
            description="The name of the service for which logrotate data is requested",
            type=openapi.TYPE_STRING
        )
    ],
    responses={200: openapi.Response('Logrotate data retrieved successfully')}
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_logrotate_by_service(request, service):
    """
    API to retrieve logrotate data based on a specific service.

    Parameters:
    request (HttpRequest): The incoming request object.
    service (str): The name of the service for which logrotate data is requested.

    Returns:
    JsonResponse: A JSON response containing the logrotate data for the specified service.
    
    """
    if request.method == 'GET':
        list_logs = []
        if LogrotateData.objects.filter(service=service).exists():
            logs_object = LogrotateData.objects.filter(service=service)
            logs = serializers.serialize("json", logs_object)
            res = json.loads(logs)
            for log in res:
                log['fields']['id'] = log["pk"]
                list_logs.append(log['fields'])
        return JsonResponse({"data": list_logs})
    
    
    
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_logrotate_data(request):
    """
    API to retrieve all logrotate data .

    Parameters:
    request (HttpRequest): The incoming request object.

    Returns:
    JsonResponse: A JSON response containing the logrotate data .
    
    """
    if request.method == 'GET':
        list_logs = []
        logs_object = LogrotateData.objects.all()
        logs = serializers.serialize("json", logs_object)
        res = json.loads(logs)
        for log in res:
            log['fields']['id'] = log["pk"]
            list_logs.append(log['fields'])
        return JsonResponse({"data": list_logs})   
@swagger_auto_schema(
    method='get',
    operation_description="API to download all logrotate data.",
    manual_parameters=[
        openapi.Parameter(
            'file_path',
            openapi.IN_QUERY,
            description="Path to the logrotate file to be downloaded.",
            type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: 'Logrotate file successfully downloaded.',
        500: 'Error: File does not exist or an unexpected error occurred.',
    }
)    
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def download_logrotate_data(request,file_path):
    """
    API to download all logrotate data .

    Parameters:
    request (HttpRequest): The incoming request object.

    Returns:
    JsonResponse: A JSON response containing the logrotate data .

    """
    if request.method == 'GET':
        try:
            with gzip.open(file_path, 'rb') as f:
                file_content = f.read()

            response = HttpResponse(file_content, content_type='application/gzip')
            response['Content-Disposition'] = f'attachment; filename={file_path.split("/")[-1]}'
            return response
        except Exception as e:
            return HttpResponse(f"Error:File not exist!", status=500)