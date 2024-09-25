import json
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.core import serializers
from backend.managementLogs.functions import get_logs_sys
from backend.managementLogs.models import LogrotateData, LogsData
from django.http import JsonResponse
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
import gzip
import zipfile
from io import BytesIO
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

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def download_logrotate_data(request):
    """
    API to convert a .gz file to a .zip file and return it as a download.
    
    Parameters:
    request (HttpRequest): The incoming request object.
    
    Returns:
    HttpResponse: The .zip file as an attachment or an error response.
    """
    try:
        file_path = request.data.get("file_path", None)
        if not file_path:
            return HttpResponse("Error: file_path is missing!", status=400)

        if not os.path.exists(file_path):
            return HttpResponse("Error: File does not exist!", status=404)

        with gzip.open(file_path, 'rb') as gz_file:
            file_content = gz_file.read()  

        zip_buffer = BytesIO()

        zip_filename = os.path.basename(file_path).replace('.gz', '.zip')
        file_inside_zip = os.path.basename(file_path).replace('.gz', '.txt')

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(file_inside_zip, file_content)  

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'

        return response

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)     
        


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_logrotate_file(request, file_id):
    """
    API to delete a logrotate file from both the file system and database.

    Parameters:
    request (HttpRequest): The incoming request object.
    file_id (int): ID of the logrotate file in the database.

    Returns:
    HttpResponse: A success message if the file is deleted or an error message.
    """
    if request.method == 'DELETE':
        try:
            log_file = LogrotateData.objects.get(id=file_id)

            # file_path = os.path.join(log_file.backup_path, log_file.filename)

            # if os.path.exists(file_path):
            #     os.remove(file_path)

            log_file.delete()

            return JsonResponse({"msg":"File  deleted successfully ." }, status=200)

        except LogrotateData.DoesNotExist:
            return JsonResponse({"msg":"Error: File does not exist "}, status=404)

        except Exception as e:
            return JsonResponse({"msg":f"Error: {str(e)}"}, status=500)
