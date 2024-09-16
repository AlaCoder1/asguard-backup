import requests
import json

from backend.ztna.constant_variables import PATH_START_ZTNA_BASH, PATH_STOP_ZTNA_BASH
from utils.commands_utils import execute_command_without_arguments, get_current_directory


BASE_URL = "https://localhost:1280/edge/management/v1/"


def get_Zt_Token():
    try:
        url = "https://localhost:1280/edge/management/v1/authenticate?method=password"
        
        # Prepare the payload
        payload = {
            "username": "admin",
            "password": "admin"
        }
        
        # Convert the payload to JSON
        headers = {'Content-Type': 'application/json'}
        
        # Send the POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_json = response.json()
            token = response_json['data']['token']  
            return token
        return None
    except Exception:
        return None


def get_data(endpoint):
    try:
        url = BASE_URL + endpoint
        session_id = get_Zt_Token()
        headers = {"zt-session": session_id}

        params = {
            "limit": 100,
        }

        response = requests.get(url, headers=headers, params=params, verify=False)

        if response.status_code == 200:
            data = response.json()
            return data["data"]
        return []
    except Exception:
        return []


def change_status_ztna_service(service_status="start"):
    current_dir = get_current_directory()
    if service_status == "start":
        path_start_ztna = PATH_START_ZTNA_BASH.format(current_dir)
    else:
        path_start_ztna = PATH_STOP_ZTNA_BASH.format(current_dir)
    execute_command_without_arguments(["sudo", "bash", path_start_ztna])
