from django.shortcuts import render
from .models import ClamAV
from django.http import JsonResponse
import json
from django.http import JsonResponse
from backend.authentification.views import *
from .serializers import ClamavSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from django.db.models import Q
import re
from django.utils import timezone
import os
from backend.clamav.functions_sys import execute_cmd
from backend.clamav.constant_variables import SCAN_PATHS



###################################### Function to display list of clamav and freshclam configurations ##########################


def getclamavconfigurations():
        """list of congifurations of clamav and freshclam"""

        clamd_list = []
        # Get all configurations from database
        clamavconfig_from_db = ClamAV.objects.all()
        clamd = serializers.serialize("json", clamavconfig_from_db)
        res = json.loads(clamd)
        print(res)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            clamd_list.append(res[i]['fields'])

        # Return the list in json form 
        return json.dumps(clamd_list)
    

###################################### Function display the result of clamav scan ################################

def clamav_full_scan_result():
    """ result of scan and list of logs get it after the clamavscan"""
    try:

        aggregated_summary = {
            'known_viruses': None,
            'engine_version': None,
            'scanned_directories': 0,
            'scanned_files': 0,
            'infected_files': 0,
            'data_scanned': {'value': 0, 'unit': 'MBData'},
            'data_read': {'value': 0, 'unit': 'MBData'},
            'scan_time': {'value': 0, 'unit': 'sec'},
            'start_date': None,
            'end_date': None,
        }

        log_files = []

        for path in SCAN_PATHS:
            command_to_execute = f'clamscan -r  {path}'

            
            result, error = execute_cmd(command_to_execute)
            print(result)

            if error:
                raise Exception(f"Error executing the command: {error}")

            # Extract relevant data using string methods
            scan_summary_start = "----------- SCAN SUMMARY -----------"
            start_index = result.find(scan_summary_start)
            if start_index != -1:
                scan_summary = result[start_index + len(scan_summary_start):].strip().replace('\n', '')


                log_files_match = re.findall(r'(.+?): (.+)', result[:start_index])
                path_log_files = [{'file_name': os.path.basename(file_path), 'file_path': file_path, 'status': status}
                                  for file_path, status in log_files_match]
                log_files.extend(path_log_files)

                    # Aggregate scan results
                aggregated_summary = aggregate_scan_results(aggregated_summary,scan_summary)

            else:
                raise Exception(f"Scan summary not found in the result for path {path}")


            # Save or update data in the database
        #save_or_update_scan_result(aggregated_summary)
            
        return aggregated_summary, log_files
    
    except Exception as e:
        print(f"Error in clamavscanview: {e}")
        return JsonResponse({'error': 'An error occurred while processing the request.'}, status=500)
    


######################################### Function used by  clamav_full_scan_result function to calculate the somme of the results the scan of each paths ####################################################################


def aggregate_scan_results(aggregated_summary,scan_summary):

    """Calcul the result of scan of all paths"""

    known_viruses = int(re.search(r'Known viruses: (\d+)', scan_summary).group(1))
    engine_version = re.search(r'Engine version: (.+?)Scanned', scan_summary).group(1)
    scanned_directories = int(re.search(r'Scanned directories: (\d+)', scan_summary).group(1))
    scanned_files = int(re.search(r'Scanned files: (\d+)', scan_summary).group(1))
    infected_files = int(re.search(r'Infected files: (\d+)', scan_summary).group(1))

    data_scanned_match = re.search(r'Data scanned: ([\d.]+) (\w+)', scan_summary)
    data_scanned = {'value': float(data_scanned_match.group(1)), 'unit': data_scanned_match.group(2)}

    data_read_match = re.search(r'Data read: ([\d.]+) (\w+)', scan_summary)
    data_read = {'value': float(data_read_match.group(1)), 'unit': data_read_match.group(2)} if data_read_match else None

    scan_time_match = re.search(r'Time: ([\d.]+) (\w+)', scan_summary)
    scan_time = {'value': float(scan_time_match.group(1)), 'unit': scan_time_match.group(2)}

    start_date_match = re.search(r'Start Date: (\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2})', scan_summary)
    start_date_str = start_date_match.group(1) if start_date_match else None

    end_date_match = re.search(r'End Date:\s*(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2})', scan_summary)
    end_date_str = end_date_match.group(1) if end_date_match else start_date_str

   

    aggregated_summary['known_viruses'] = known_viruses
    aggregated_summary['engine_version'] = engine_version
    aggregated_summary['scanned_directories'] += scanned_directories
    aggregated_summary['scanned_files'] += scanned_files
    aggregated_summary['infected_files'] += infected_files
    aggregated_summary['data_scanned']['value'] += data_scanned['value']
    aggregated_summary['data_read']['value'] = (
        aggregated_summary['data_read']['value'] + data_read['value'] if data_read else None
    )
    aggregated_summary['scan_time']['value'] += scan_time['value']
    aggregated_summary['start_date'] = (
        timezone.make_aware(datetime.strptime(start_date_str, '%Y:%m:%d %H:%M:%S')) if start_date_str else None
    )
    aggregated_summary['end_date'] = (
        timezone.make_aware(datetime.strptime(end_date_str, '%Y:%m:%d %H:%M:%S')) if end_date_str else None
    )

    return aggregated_summary
        