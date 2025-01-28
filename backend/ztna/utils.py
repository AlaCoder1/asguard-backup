import requests
import json

from backend.ztna.constant_variables import PATH_BASE_URL_ZTNA, CONSTANT_CONTENT_TYPE, PATH_CHECK_TEMPLATE_BASH, PATH_CREATE_ROUTER_BASH, PATH_DELETE_ROUTER_BASH, PATH_LINUX_TEMPLATE_BASH, PATH_START_ZTNA_BASH, PATH_START_ZTNA_ROUTER_BASH, PATH_STATUS_ZTNA_BASH, PATH_STATUS_ZTNA_ROUTER_BASH, PATH_STOP_ZTNA_BASH, PATH_STOP_ZTNA_ROUTER_BASH, PATH_UPDATE_ROUTER_BASH, PATH_WINDOWS_TEMPLATE_BASH, PATH_ZTNA_ROUTER
from utils.commands_utils import execute_command_with_arguments, execute_command_without_arguments, get_current_directory


def get_ztna_token_from_system():
    """Get the token to use openziti APIs"""
    try:
        url = f"{PATH_BASE_URL_ZTNA}authenticate?method=password"
        
        # Prepare the payload
        payload = {
            "username": "admin",
            "password": "admin"
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


def get_data(endpoint):
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


def change_status_router(router_name, router_status):
    """Change status of a ZTNA Router by starting or stoping it"""
    current_dir = get_current_directory()
    if router_status == "start":
        execute_command_with_arguments(["sudo", "bash", PATH_START_ZTNA_ROUTER_BASH.format(current_dir)], 
                                       f"{router_name}\n", 3)
        
    else:
        execute_command_with_arguments(["sudo", "bash", PATH_STOP_ZTNA_ROUTER_BASH.format(current_dir)], f"{router_name}", 3)


def change_ports_yaml_file(router_name, id):
    """Change ports of link and listeners of router yaml file which is by default 10080 and 3022"""
    link_port=10080+id
    listeners_port=3022+id
    current_dir = get_current_directory()
    file_path=PATH_ZTNA_ROUTER.format(current_dir)+f"{router_name}/{router_name}.yaml"
    # Get contents of the yaml router file
    with open(f"{file_path}") as router_yaml_file:
        router_yaml_content = router_yaml_file.read()
    
    # Change default ports by the unique ports of the router
    router_yaml_content = router_yaml_content.replace("tls:0.0.0.0:10080", f"tls:0.0.0.0:{link_port}")
    router_yaml_content = router_yaml_content.replace("tls:Asguard:10080", f"tls:Asguard:{link_port}")
    router_yaml_content = router_yaml_content.replace("tls:0.0.0.0:3022", f"tls:0.0.0.0:{listeners_port}")
    router_yaml_content = router_yaml_content.replace("Asguard:3022", f"Asguard:{listeners_port}")

    # Change contents of the yaml router file
    with open(f"{file_path}", "w") as router_yaml_file:
        router_yaml_file.write(router_yaml_content)


def get_identities_from_ziti(id):
    endpoint = f"identities/{id}"
    return get_data(endpoint)


def get_routers_from_ziti(id):
    endpoint = f"edge-routers/{id}"
    return get_data(endpoint)


def create_router(router_name,token=""):
    current_dir = get_current_directory()
    execute_command_with_arguments(["sudo", "bash", PATH_CREATE_ROUTER_BASH.format(current_dir)], 
                                       f"{router_name}\n{token}\n", 3)
    

def delete_router(router_name):
    current_dir = get_current_directory()
    execute_command_with_arguments(["sudo", "bash", PATH_DELETE_ROUTER_BASH.format(current_dir)], 
                                       f"{router_name}\n", 3)

    
def update_router_in_system(old_router_name, new_router_name):
    """Update a router name in system by changing all dependencies file names if the name is changed"""
    if old_router_name != new_router_name:
        current_dir = get_current_directory()
        execute_command_with_arguments(["sudo", "bash", PATH_UPDATE_ROUTER_BASH.format(current_dir)], 
                                       f"{old_router_name}\n{new_router_name}", 3)


def get_status_router_from_system(router_name):
    current_dir = get_current_directory()
    process, stdout, stderr = execute_command_with_arguments(["sudo", "bash", PATH_STATUS_ZTNA_ROUTER_BASH.format(current_dir)], f"{router_name}\n")
    if process is not None:
        print("status_router completed with exit code:", process.returncode)
        print("status_router output:", stdout)
        print("status_router error (if any):", stderr)
    else:
        print("Failed to execute the command.")
    return stdout


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


def local_domain_linux_name():
    try:
        current_dir = get_current_directory()
        file_path=PATH_LINUX_TEMPLATE_BASH.format(current_dir)
        with open(f"{file_path}") as host_append_shell:
            linux_host = host_append_shell.read()
            return linux_host
    except Exception:
        return None


def local_domain_windows_name():
    try:
        current_dir = get_current_directory()
        file_path=PATH_WINDOWS_TEMPLATE_BASH.format(current_dir)
        with open(f"{file_path}") as host_append_shell:
            windows_host = host_append_shell.read()
            return windows_host
    except Exception:
        return None


def check_host_templates():
   
    current_dir = get_current_directory()
    check_file_path=PATH_CHECK_TEMPLATE_BASH.format(current_dir)
    status = execute_command_without_arguments(["sudo", "bash", check_file_path])
    if status.stdout.find("IP address has not changed. Exiting.") >= 0:
        return True
    return False
