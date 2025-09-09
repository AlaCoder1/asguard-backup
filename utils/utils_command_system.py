import os
from utils.commands_utils import execute_command_without_arguments, execute_list_commands_without_arguments


def restart_nginx_in_system():
    execute_command_without_arguments(["sudo", "systemctl", "restart", "nginx"])
def restart_uvicorn_in_system():
    execute_command_without_arguments(["sudo", "systemctl", "restart", "uvicorn"])


def check_exist_files_in_system(list_file_path: list[str]):
    """Check if the list of files exist in system"""
    for file_path in list_file_path:
        if not os.path.isfile(file_path):
            return False
    return True


def change_name_files_in_system(list_files : list[dict]):
    """Change the list of files name in system if exists"""
    list_file_path = [file_path["previous_file_path"] for file_path in list_files]
    if not check_exist_files_in_system(list_file_path):
        return False
    list_commands = []
    for file_path in list_files:
        list_commands.append(['sudo', 'mv', file_path["previous_file_path"], file_path["next_file_path"]])
    execute_list_commands_without_arguments(list_commands)
    return True
