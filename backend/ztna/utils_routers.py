from backend.ztna.constant_variables import PATH_CREATE_ROUTER_BASH, PATH_DELETE_ROUTER_BASH, PATH_START_ZTNA_ROUTER_BASH, PATH_STATUS_ZTNA_ROUTER_BASH, PATH_STOP_ZTNA_ROUTER_BASH, PATH_UPDATE_ROUTER_BASH, PATH_ZTNA_ROUTER
from backend.ztna.utils import get_data
from utils.commands_utils import execute_command_with_arguments, get_current_directory


def get_router_from_ziti(id):
    """Get router data from openziti API"""
    endpoint = f"edge-routers/{id}"
    return get_data(endpoint)


def change_status_router(router_name, router_status):
    """Change status of a ZTNA Router by starting or stoping it"""
    current_dir = get_current_directory()
    if router_status == "start":
        execute_command_with_arguments(["sudo", "bash", PATH_START_ZTNA_ROUTER_BASH.format(current_dir)],
                                       f"{router_name}\n", 3)

    else:
        execute_command_with_arguments(["sudo", "bash", PATH_STOP_ZTNA_ROUTER_BASH.format(current_dir)], f"{router_name}", 3)


def change_ports_router_yaml_file(router_name, id):
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
