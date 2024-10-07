import requests
import json

from backend.ztna.constant_variables import PATH_START_ZTNA_BASH, PATH_START_ZTNA_ROUTER_BASH, PATH_STATUS_ZTNA_BASH, PATH_STOP_ZTNA_BASH, PATH_STOP_ZTNA_ROUTER_BASH, PATH_ZTNA_ROUTER
from utils.commands_utils import execute_command_with_arguments, execute_command_without_arguments, get_current_directory


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


def change_status_router(router_name, router_status, token=""):
    """Change status of a ZTNA Router by starting or stoping it"""
    current_dir = get_current_directory()
    if router_status == "start":
        execute_command_with_arguments(["sudo", "bash", PATH_START_ZTNA_ROUTER_BASH.format(current_dir)], 
                                       f"{router_name}\n{token}\n", 3)
    else:
        execute_command_with_arguments(["sudo", "bash", PATH_STOP_ZTNA_ROUTER_BASH.format(current_dir)], f"{router_name}", 3)


def change_ports_yaml_file(router_name, link_port=10080, listeners_port=3022):
    """Change ports of link and listeners of router yaml file which is by default 10080 and 3022"""

    # Get contents of the yaml router file
    with open(f"{PATH_ZTNA_ROUTER}{router_name}.yaml") as router_yaml_file:
        router_yaml_content = router_yaml_file.read()
    
    # Change default ports by the unique ports of the router
    router_yaml_content = router_yaml_content.replace("tls:0.0.0.0:10080", f"tls:0.0.0.0:{link_port}")
    router_yaml_content = router_yaml_content.replace("tls:Asguard:10080", f"tls:Asguard:{link_port}")
    router_yaml_content = router_yaml_content.replace("tls:0.0.0.0:3022", f"tls:0.0.0.0:{listeners_port}")
    router_yaml_content = router_yaml_content.replace("Asguard:3022", f"Asguard:{listeners_port}")

    # Change contents of the yaml router file
    with open(f"{PATH_ZTNA_ROUTER}{router_name}.yaml", "w") as router_yaml_file:
        router_yaml_file.write(router_yaml_content)


def get_identities_from_ziti(id):
    endpoint = f"identities/{id}"
    return get_data(endpoint)


def get_routers_from_ziti(id):
    endpoint = f"edge-routers/{id}"
    return get_data(endpoint)
