import json
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.core import serializers
from backend.managementLogs.functions import get_logs_sys
from backend.managementLogs.models import LogrotateData, LogsData
from django.http import JsonResponse
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