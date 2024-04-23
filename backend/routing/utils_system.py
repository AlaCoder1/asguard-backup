from backend.routing.constant_variables import PATH_ROUTING
from utils.commands_utils import execute_command_without_arguments, get_current_directory


def routing_in_system(routing_method, destination_address, gateway_address, ifname, metric):
    """Create or delete a route in system and save all route list in a file routing.txt to assure the reproducibility"""
    current_dir = get_current_directory()
    command_route = f"sudo ip route {routing_method} {destination_address} via {gateway_address} dev {ifname}"
    if metric:
        command_route += f" metric {metric}"
    execute_command_without_arguments(list(command_route.split(" ")))

    if routing_method == "add":
        with open(PATH_ROUTING.format(current_dir), 'a') as routing_file:
            routing_file.write(f'\n{command_route}')
    else:
        command_route = command_route.replace("del", "add")
        with open(PATH_ROUTING.format(current_dir)) as routing_file:
            routing_content = routing_file.read()
        routing_content = routing_content.replace(command_route, "")
        with open(PATH_ROUTING.format(current_dir), 'w') as routing_file:
            routing_file.write(routing_content)
