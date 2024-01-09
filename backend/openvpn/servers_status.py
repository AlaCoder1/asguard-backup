import re

from backend.network.models import Interface
from backend.network.serializers import IP4ConfigSerializer, InterfaceOpenVPNSerializer
from utils.commands_utils import execute_command_without_arguments
from backend.openvpn.models import ServerOpenvpn


def synchronize_server_openvpn():
    """Synchronize the openvpn interfaces and the running servers with database"""
    # Initialization
    initialize_server_status()

    # Get the opened interfaces from system (TUN and TAP)
    list_interfaces_tun, list_interfaces_tap = openvpn_opening_interfaces()

    # Synchronize system with server_openvpn table
    synchronize_server_table(list_interfaces_tun)
    synchronize_server_table(list_interfaces_tap)

    # Synchronize system with interface table
    synchronize_interface_table(list_interfaces_tun, 'tun')
    synchronize_interface_table(list_interfaces_tap, 'tap')


def change_status_server_openvpn(server_name, server_status):
    """Change the status of a server openvpn: start, restart or stop"""
    command = ['sudo', 'systemctl', f'{server_status}', f'openvpn-server@server_{server_name}']
    execute_command_without_arguments(command)


def initialize_server_status():
    """Initialize openvpn servers and interfaces. 
    This function set all server_status of all servers to False and delete all openvpn interfaces and ip4config from database"""

    # Delete previous openvpn interfaces and ip4config
    list_interfaces = Interface.objects.filter(ifname__startswith='tun_') | Interface.objects.filter(ifname__startswith='tap_')
    print("list_interfaces: ", list_interfaces)
    for interface in list_interfaces:
        interface.delete()
    
    # All servers are stopped
    ServerOpenvpn.objects.all().update(server_status=False)


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
    for vpn_interface_tun in list_vpn_interfaces:
        vpn_server = ServerOpenvpn.objects.get(name__startswith=vpn_interface_tun)
        vpn_server.server_status = True
        vpn_server.save()


def synchronize_interface_table(list_interfaces, device_mode):
    for interface in list_interfaces:
        server = ServerOpenvpn.objects.get(name__startswith=interface)
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
            else:
                print('error ip4config')
                print(ipv4_serializer.errors)
        else:
            print('error interface')
            print(interface_serializer.errors)
