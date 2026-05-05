import re

from backend.network.models import Interface
from backend.network.serializers import IP4ConfigSerializer, InterfaceOpenVPNSerializer
from utils.commands_utils import execute_command_without_arguments
from backend.openvpn.models import ServerOpenvpn


def synchronize_server_openvpn():
    """Synchronize the openvpn interfaces and the running servers with database"""
    # Initialization
    list_interfaces_tun_from_db, list_interfaces_tap_from_db, list_interfaces_tun, list_interfaces_tap = initialize_server_status()

    # Synchronize system with server_openvpn table
    synchronize_server_table(list_interfaces_tun)
    synchronize_server_table(list_interfaces_tap)

    # Delete the closed interfaces from database
    delete_closed_interfaces(list_interfaces_tun_from_db, list_interfaces_tun)
    delete_closed_interfaces(list_interfaces_tap_from_db, list_interfaces_tap, 'tap')

    # Add the opened interfaces to the database
    add_opened_interfaces(list_interfaces_tun)
    add_opened_interfaces(list_interfaces_tap, 'tap')


def change_status_server_openvpn(server_name, server_status):
    """Change the status of a server openvpn: start, restart or stop"""
    command = ['sudo', 'systemctl', f'{server_status}', f'openvpn-server@server_{server_name}']
    execute_command_without_arguments(command)


def initialize_server_status():
    """Initialize openvpn servers and interfaces. 
    This function set all server_status of all servers to False 
    and get all openvpn interfaces and ip4config from system and database"""

    # Delete previous openvpn interfaces and ip4config
    list_interfaces_tun_db = Interface.objects.filter(ifname__startswith='tun_')
    list_interfaces_tap_db = Interface.objects.filter(ifname__startswith='tap_')

    # Get the opened interfaces from system (TUN and TAP)
    list_interfaces_tun_system, list_interfaces_tap_system = openvpn_opening_interfaces()
    
    # All servers are stopped
    ServerOpenvpn.objects.all().update(server_status=False)
    return list_interfaces_tun_db, list_interfaces_tap_db, list_interfaces_tun_system, list_interfaces_tap_system


def openvpn_opening_interfaces():
    """A function that return a list of opening openvpn interfaces from system"""
    command = ['sudo', 'ip', '-o', 'link', 'show']
    process = execute_command_without_arguments(command)
    pattern_tun = re.compile(r'(\d+): tun_([^ ]+)')
    list_interfaces_tun = pattern_tun.findall(process.stdout)
    list_interfaces_tun = [interface[1][:len(interface[1])-1] for interface in list_interfaces_tun]
    pattern_tap = re.compile(r'(\d+): tap_([^ ]+)')
    list_interfaces_tap = pattern_tap.findall(process.stdout)
    list_interfaces_tap = [interface[1][:len(interface[1])-1] for interface in list_interfaces_tap]

    return list_interfaces_tun, list_interfaces_tap


def synchronize_server_table(list_vpn_interfaces):
    """Synchronize server table with system. 
    This function take list of opening openvpn interfaces and change server_status of running severs to True"""
    for vpn_interface in list_vpn_interfaces:
        # In case of existing another servers there names starts with this server name we take the server with this name
        # Example: 2 servers "server" and "server_copy" we take "server"
        list_vpn_server = ServerOpenvpn.objects.filter(name__startswith=vpn_interface)
        if len(list_vpn_server) > 1:
            vpn_server = ServerOpenvpn.objects.get(name=vpn_interface)
        else:
            vpn_server = list_vpn_server[0]
        vpn_server.server_status = True
        vpn_server.save()


def delete_closed_interfaces(list_interfaces_from_db, list_interfaces_from_system, device_mode='tun'):
    """Compare list of openvpn interfaces from database and from system and let only the interfaces opened in system"""
    list_interfaces_from_system = [f'{device_mode}_{interface}' for interface in list_interfaces_from_system]
    for interface in list_interfaces_from_db:
        if interface.ifname not in list_interfaces_from_system:
            interface.delete()


def add_opened_interfaces(list_interfaces_from_system, device_mode='tun'):
    """Compare list of openvpn interfaces from system with interface table in database 
    and add the new opened interfaces in system to the database"""
    for interface in list_interfaces_from_system:
        list_interface = Interface.objects.filter(ifname=f'{device_mode}_{interface}')
        if len(list_interface) == 0:
            # In case of existing another servers there names starts with this server name we take the server with this name
            # Example: 2 servers "server" and "server_copy" we take "server"
            list_vpn_server = ServerOpenvpn.objects.filter(name__startswith=interface)
            if len(list_vpn_server) > 1:
                server = ServerOpenvpn.objects.get(name=interface)
            else:
                server = list_vpn_server[0]
            interface_data = {"ifname": f'{device_mode}_{interface}',
                              "name_interface": server.name}
            interface_serializer = InterfaceOpenVPNSerializer(data=interface_data)
            if interface_serializer.is_valid():
                interface_serializer.save()
                new_interface = Interface.objects.get(name_interface=server.name)
                ipv4_data = {"typeip4": "static",
                             "interface": new_interface.pk
                             }
                if server.ipv4_tunnel_network:
                    ipv4_data['ip_address'] = server.ipv4_tunnel_network[:server.ipv4_tunnel_network.find('/')]
                    ipv4_data['netmask'] = server.ipv4_tunnel_network[server.ipv4_tunnel_network.find('/')+1:]
                ipv4_serializer = IP4ConfigSerializer(data=ipv4_data)
                if ipv4_serializer.is_valid():
                    ipv4_serializer.save()
