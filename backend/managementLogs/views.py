import json
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.core import serializers
from backend.managementLogs.functions import get_logs_sys
from backend.managementLogs.models import LogsData
from django.http import JsonResponse
# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_logs_data(request):
    """API to get the last 1000 logs from the database"""
    if request.method == 'GET':
        list_logs = []
        logs_object = LogsData.objects.all().order_by('-id')[:1000]
        print({'logs_object': logs_object})
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