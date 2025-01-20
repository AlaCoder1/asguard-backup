import json
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.core import serializers
from backend.managementLogs.functions import get_logs_service, get_logs_sys
from backend.managementLogs.models import LogrotateData, LogsData
from django.http import JsonResponse
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
import gzip
import zipfile
from io import BytesIO
@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve log entry details.",
    responses={
        200: openapi.Response(
            description=(
                "Details of the log entry retrieved successfully. "
                "Each log entry contains the following attributes:\n"
                "- **date**: The date and time of the log event (e.g., 'Dec 11 08:10:35').\n"
                "- **process**: The process that generated the log entry, including its name and ID (e.g., 'Asguard sudo[1649]').\n"
                "- **message**: A detailed log message (e.g., 'pam_unix(sudo:session): session opened for user root(uid=0) by (uid=1001)').\n"
                "- **id**: The unique identifier for the log entry."
            ),

        ),
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_logs_data(request):
    """
    API to get the last 1000 logs from the database.

    This function retrieves the last 1000 log entries from the database and returns them as a JSON response.
    
    Parameters:
    request (HttpRequest): The incoming request object. 

    Returns:
    JsonResponse: A JSON response containing the log data. The response is formatted as {"data": logs_data},
    where logs_data is a list of log entries. 
    Each log entry is represented as a dictionary with the following keys:
    - date: The date and time of the log event.
    - process: The process that generated the log entry, including its name and ID.
    - message: A detailed log message.
    - id: The unique identifier for the log entry.

    """
    if request.method == 'GET':
        list_logs = []
        logs_object = LogsData.objects.all().order_by('-id')[:1000]
        logs = serializers.serialize("json", logs_object)
        res = json.loads(logs)
        for log in res:
            log['fields']['id'] = log["pk"]
            list_logs.append(log['fields'])
        return JsonResponse({"data": list_logs},status=200)
    
@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve and format log data for download.",
    responses={
        200: openapi.Response(
            description=(
                "Details of the log entry retrieved successfully. "
                "Each log entry contains the following attributes:\n"
                "- **date**: The date and time of the log event (e.g., 'Dec 11 08:10:35').\n"
                "- **process**: The process that generated the log entry, including its name and ID (e.g., 'Asguard sudo[1649]').\n"
                "- **message**: A detailed log message (e.g., 'pam_unix(sudo:session): session opened for user root(uid=0) by (uid=1001)').\n"
                "- **id**: The unique identifier for the log entry."
            ),

        ),
    }
)    
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def download_logs_data(request):
    """
    API to retrieve and format log data for download.

    This function is responsible for retrieving log data from a system-specific source,
    formatting it into a JSON response, and returning it as a downloadable file.

    Parameters:
    request (HttpRequest): The incoming request object. 

    Returns:
    JsonResponse: A JSON response containing the log data. The response is formatted as {"data": logs_data},
    where logs_data is a list of log entries. Each log entry is represented as a dictionary with the following keys:
    - date: The date and time of the log event.
    - process: The process that generated the log entry, including its name and ID.
    - message: A detailed log message.
    - id: The unique identifier for the log entry.

    Note: The actual implementation of retrieving log data from the system-specific source is not included in this docstring.
    """
    if request.method == 'GET':
        logs_data = get_logs_sys()
        return JsonResponse({"data": logs_data},status=200)
    
  
    
    
@swagger_auto_schema(
    method='get',
    operation_summary="API to retrieve logrotate data based on a specific service.",
    manual_parameters=[
        openapi.Parameter(
            'service',
            openapi.IN_PATH,
            description="The name of the service for which logrotate data is requested",
            type=openapi.TYPE_STRING,
            enum=['WAF','OpenVPN',"Squid"]
            
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
        return JsonResponse({"data": list_logs},status=200)
    
    

@swagger_auto_schema(
    method='get',
    operation_summary="API to retrieve all logrotate data",
    responses={
    200: openapi.Response(
            description=(
                "Details of the log files retrieved successfully. "
                "Each log file contains the following attributes:\n"
                "- **service**: The service associated with the log file (e.g., 'IDS/IPS').\n"
                "- **filename**: The name of the log file (e.g., 'suricata.log-2024-09-09-08:52:38.gz').\n"
                "- **original_path**: The original directory path of the log file (e.g., '/var/log/suricata/suricata.log').\n"
                "- **backup_path**: The directory path where backup logs are stored (e.g., '/var/log/suricata/backup_logs').\n"
                "- **date**: The timestamp indicating when the log file was created or modified (e.g., '2024-09-09-08:52:38').\n"
                "- **id**: The unique identifier of the log entry."
            ),
    )
    }
)    
    
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
        return JsonResponse({"data": list_logs},status=200)   



@swagger_auto_schema(
    method='POST',
    operation_summary="API to convert a .gz file to a .zip file and return it as a download.",
    responses={
    200: "File download successfully!",
    400: "Error in downloading file"
    }
)    
   
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
        return HttpResponse(f"Error: {str(e)}", status=400)     
        

@swagger_auto_schema(
    method='DELETE',
    manual_parameters=[
        openapi.Parameter(
            'file_id',
            openapi.IN_PATH,
            description="The ID of the logrotate file to delete",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={200:"File  deleted successfully .",
               404:"Error: File does not exist ",
               400: "Error in deleting"},
    operation_summary="API DELETE logrotate file ",
)
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
            return JsonResponse({"msg":f"Error: {str(e)}"}, status=400)

@swagger_auto_schema(
    method='get',
    operation_summary="API to retrieve logs data based on a specific service and download it.",
    manual_parameters=[
        openapi.Parameter(
            'service',
            openapi.IN_PATH,
            description="The path of the service for which logs data is requested",
            type=openapi.TYPE_STRING,
           example="/var/log/suricata/suricata.log"
            
        )
    ],
    responses={200: openapi.Response('Logrotate data retrieved successfully')}
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def download_logs_service(request,file_path):
    """API to get data to download it into file"""
    if request.method == 'GET':
        logs_data=get_logs_service(file_path)
        return JsonResponse({"data": logs_data},status=200)