from utils.commands_utils import execute_command_without_arguments


def restart_nginx_in_system():
    execute_command_without_arguments(["sudo", "systemctl", "restart", "nginx"])