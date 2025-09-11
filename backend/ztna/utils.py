import requests
import json

from backend.ztna.constant_variables import PATH_BASE_URL_ZTNA, CONSTANT_CONTENT_TYPE, PATH_CHECK_TEMPLATE_BASH, PATH_LINUX_TEMPLATE_BASH, PATH_START_ZTNA_BASH, PATH_STATUS_ZTNA_BASH, PATH_STOP_ZTNA_BASH, PATH_WINDOWS_TEMPLATE_BASH
from utils.commands_utils import execute_command_without_arguments, get_current_directory
from decouple import config


def get_ztna_token_from_system():
    """Get the token to use openziti APIs"""
    try:
        url = f"{PATH_BASE_URL_ZTNA}authenticate?method=password"
        
        # Prepare the payload
        payload = {
            "username": config("USERRNAME_ZTNA"),
            "password": config("PASSWORD_ZTNA")
        }
        
        # Convert the payload to JSON
        headers = {'Content-Type': CONSTANT_CONTENT_TYPE}
        
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


def get_data_from_openziti(endpoint):
    """Get data from openziti APIs: Identity, Enrollement, Configuration, Service, Router, and Policy"""
    try:
        url = PATH_BASE_URL_ZTNA + endpoint
        session_id = get_ztna_token_from_system()
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


def get_status_ztna_service():
    """Get Status of ZTNA service"""
    current_dir = get_current_directory()
    path_status_ztna = PATH_STATUS_ZTNA_BASH.format(current_dir)
    status = execute_command_without_arguments(["sudo", "bash", path_status_ztna])
    if status.stdout.find("ZTNA is not running") >= 0:
        return False
    return True


def change_status_ztna_service(service_status="start"):
    """Change status of ZTNA service by starting or stoping it"""
    current_dir = get_current_directory()
    path_change_status_ztna = PATH_START_ZTNA_BASH.format(current_dir)
    if service_status == "stop":
        path_change_status_ztna = PATH_STOP_ZTNA_BASH.format(current_dir)
    execute_command_without_arguments(["sudo", "bash", path_change_status_ztna])


def get_local_domain_from_system(os="linux"):
    """Get local domain for the current os from system"""
    try:
        current_dir = get_current_directory()
        file_path=PATH_LINUX_TEMPLATE_BASH.format(current_dir)
        if os == "windows":
            file_path=PATH_WINDOWS_TEMPLATE_BASH.format(current_dir)
        with open(f"{file_path}") as host_append_shell:
            host = host_append_shell.read()
            return host
    except Exception:
        return None


def check_host_templates():
   
    current_dir = get_current_directory()
    check_file_path=PATH_CHECK_TEMPLATE_BASH.format(current_dir)
    status = execute_command_without_arguments(["sudo", "bash", check_file_path])
    if status.stdout.find("IP address has not changed. Exiting.") >= 0:
        return True
    return False
