from datetime import datetime
from .models import ClamAV,FreshclamDatabase
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from .serializers import ClamavSerializer,FreshclamDatabaseSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from drf_yasg.utils import swagger_auto_schema
from backend.clamav.functions_sys import update_clamav_config,execute_cmd
from backend.clamav.list_configurations import getclamavconfigurations,clamav_full_scan_result


# Constants
CONSTANT_CONFIG_FILE = _("Config file")
CONSTANT_FRESHCLAM = _("Freshclam")
# Success messages
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_SCANING = _("Error in scaning")


################ Get the clamav configurations data from the database #############

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF Clamav Configurations")
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def getconfiguratiosnfromdatabase(request):
    """Getting clamav configurations from database"""
    if (request.method == 'GET'):
        configurations_clamav = getclamavconfigurations()
        return JsonResponse(configurations_clamav, safe=False)


############### Update ApI to modify the file configuration system and saved the changes on database ##########################

@swagger_auto_schema(
    method='PUT',
    request_body=ClamavSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO update_Clamav_configuration",
    operation_description="API TO update_Clamav_configuration")  
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_clamav_configuration(request, id):
    if request.method=="PUT":
        """Update clamav configurations in config and freshclam file"""
        try:
            # Retrieve ClamAV object from the database using the id
            clamav_object = ClamAV.objects.get(pk=id)

            # Extract parameters from the request data
            logverbose = request.data.get('logverbose')
            tcpport = request.data.get('tcpport')
            tcpsocket = request.data.get('tcpsocket')
            maxqueue = request.data.get('maxqueue')
            maxthreads = request.data.get('maxthreads')
            idletimeout = request.data.get('idletimeout')
            maxdirectoryrecursion = request.data.get('maxdirectoryrecursion')
            followdirectorysymlinks = request.data.get('followdirectorysymlinks')
            followfilesymlinks = request.data.get('followfilesymlinks')
            disablecache = request.data.get('disablecache')
            alertbrokenexecutables = request.data.get('alertbrokenexecutables')
            alertencryptedarchive = request.data.get('alertencryptedarchive')
            alertole2macros = request.data.get('alertole2macros')
            scanpe = request.data.get('scanpe')
            scanelf = request.data.get('scanelf')
            scanole2 = request.data.get('scanole2')
            scanpdf = request.data.get('scanpdf')
            scanxmldocs = request.data.get('scanxmldocs')
            scanhwp3 = request.data.get('scanhwp3')
            scanmail = request.data.get('scanmail')
            scanhtml = request.data.get('scanhtml')
            scanarchive = request.data.get('scanarchive')
            maxscansize = request.data.get('maxscansize')
            maxfilesize = request.data.get('maxfilesize')
            maxrecursion = request.data.get('maxrecursion')
            maxfiles = request.data.get('maxfiles')
            freshclamdatabasemirror = request.data.get('freshclamdatabasemirror')
            freshclamconnectiontimeout = request.data.get('frechclamconnectiontimeout')
            proxyport = request.data.get('proxyport')
            clamd_enabled = request.data.get('clamd_enabled')
            freshclam_enabled = request.data.get('freshclam_enabled')

            # Call the update_clamav_config function
            result = update_clamav_config(maxfiles,maxfilesize,scanhtml,scanarchive,scanxmldocs,scanmail,scanhwp3,scanpdf,scanole2,disablecache,scanelf,scanpe,alertole2macros,alertencryptedarchive,alertbrokenexecutables,followdirectorysymlinks,followfilesymlinks,freshclamdatabasemirror,freshclamconnectiontimeout,tcpport,tcpsocket,maxqueue,maxrecursion,proxyport,maxscansize,maxdirectoryrecursion,idletimeout,clamd_enabled,freshclam_enabled,logverbose,maxthreads)
            

            if result:
            # Save the updated ClamAV object
                clamav_object.logverbose = logverbose
                clamav_object.tcpport = tcpport
                clamav_object.tcpsocket = tcpsocket
                clamav_object.maxthreads = maxthreads
                clamav_object.maxqueue = maxqueue
                clamav_object.idletimeout = idletimeout
                clamav_object.maxdirectoryrecursion = maxdirectoryrecursion
                clamav_object.followdirectorysymlinks = followdirectorysymlinks
                clamav_object.followfilesymlinks = followfilesymlinks
                clamav_object.disablecache = disablecache
                clamav_object.alertbrokenexecutables = alertbrokenexecutables
                clamav_object.alertencryptedarchive = alertencryptedarchive
                clamav_object.alertole2macros = alertole2macros
                clamav_object.scanpe = scanpe
                clamav_object.scanelf = scanelf
                clamav_object.scanole2 = scanole2
                clamav_object.scanpdf = scanpdf
                clamav_object.scanxmldocs = scanxmldocs
                clamav_object.scanhwp3 = scanhwp3
                clamav_object.scanmail = scanmail
                clamav_object.scanhtml = scanhtml
                clamav_object.scanarchive = scanarchive
                clamav_object.maxscansize = maxscansize
                clamav_object.maxfilesize = maxfilesize
                clamav_object.maxrecursion = maxrecursion
                clamav_object.maxfiles = maxfiles
                clamav_object.freshclamdatabasemirror = freshclamdatabasemirror
                clamav_object.frechclamconnectiontimeout = freshclamconnectiontimeout
                clamav_object.proxyport = proxyport
                clamav_object.clamd_enabled = clamd_enabled
                clamav_object.freshclam_enabled = freshclam_enabled
                clamav_object.save()
                
                return JsonResponse({'success': True, 'msg': f"{CONSTANT_CONFIG_FILE} {SUCCESS_MESSAGES_UPDATING}"},status=200)
            return JsonResponse({'success': False, 'msg': f"{ERROR_MESSAGES_UPDATING} {CONSTANT_CONFIG_FILE}"}, status=400)
                      
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


############################ API For Update the frechclam database ##################################

@swagger_auto_schema(
    method='POST',
    request_body=FreshclamDatabaseSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API Update Freshclam Database ",
    operation_description="API Update Freshclam Database ")  
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_freshclam_database(request):
    if request.method == 'POST':
        """Update the freshclam database"""
        clamav = ClamAV.objects.first()
        
        result = execute_cmd('freshclam')

        freshclam_entry = FreshclamDatabase.objects.first()

        if freshclam_entry:
            # Update the existing entry
            freshclam_entry.line = '\n'.join(result)
            freshclam_entry.date = datetime.now()
            freshclam_entry.save()
        else:
            # Create a new entry
            freshclam_data = FreshclamDatabase(clamav=clamav, process_type='Update', line='\n'.join(result), date=datetime.now())
            freshclam_data.save()

     
        # Retrieve all entries from FreshclamDatabase
        freshclam_entries = FreshclamDatabase.objects.all()

        serialized_data = [
            {
                'date': entry.date,
                'process_type': entry.process_type,
                'line': entry.line,
            }
            for entry in freshclam_entries
        ]

        return JsonResponse({'message': f"{CONSTANT_FRESHCLAM} {SUCCESS_MESSAGES_UPDATING}", 'data': serialized_data})
    
    return JsonResponse({'error': f"{ERROR_MESSAGES_UPDATING} {CONSTANT_FRESHCLAM}"})


############################ API Full scan clamav #################################

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def clamavscanview(request):
    """Getting Result of full scan"""
    if (request.method == 'GET'):
        try:
            aggregated_summary, log_files = clamav_full_scan_result()
            return JsonResponse({'result': aggregated_summary, 'log_files': log_files}, safe=False)
        except Exception:
                return JsonResponse({"message": ERROR_MESSAGES_SCANING}, status=400)
