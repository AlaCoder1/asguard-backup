import subprocess
import time
from openvpn.manage_errors import create_error
from openvpn.models import ServerOpenvpn
from openvpn.serializers import ServerOpenvpnSerializer


def execute_command_without_arguments(command, decode=True, shell=False):
    """Function that execute a command line without arguments"""
    print(f'command {command}')
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=decode, shell=shell)
    create_error(process, command)
    return process


def execute_list_commands_without_arguments(commands_list):
    """Function that execute a list of commands line without arguments"""
    for command in commands_list:
        execute_command_without_arguments(command)


def execute_command_with_arguments(command, arguments, time_sleep=0.5):
    """Function that execute a command line with arguments"""
    try:
        with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            print("Command: ", command)
            time.sleep(time_sleep)
            process.communicate(input=arguments)

            create_error(process, command)
    except subprocess.CalledProcessError as e:
        print(f'Command failed with error: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

def execute_list_commands_with_arguments(list_commands, time_sleep=0.5):
    """Function that execute a list of commands line with arguments"""
    for command in list_commands:
        execute_command_with_arguments(command=command['command'], arguments=command['arguments'],
                                       time_sleep=time_sleep)


def get_current_directory():
    """A function to get the current directory"""
    process = execute_command_without_arguments(['pwd'])
    current_directory = process.stdout
    current_directory = current_directory[:len(current_directory)-1]
    return current_directory


def create_tls_file(tls_auth, path_tls):
    """Create TLS file by importing tls key or generating it"""
    print("Creating tls file:")
    if tls_auth['generate']:
        command = ['openvpn', '--genkey', 'secret', f'{path_tls}']
        execute_command_without_arguments(command)
    else:
        tls_key = f'-----BEGIN OpenVPN Static key V1-----\n{tls_auth["tls_key"]}\n-----END OpenVPN Static key V1-----'
        with open(path_tls, 'w') as tls_file:
            tls_file.write(tls_key)


def change_status_server_openvpn(server_name, server_status):
    """Change the status of a server openvpn: start, restart or stop"""
    command = ['sudo', 'systemctl', f'{server_status}', f'openvpn-server@server_{server_name}']
    execute_command_without_arguments(command)


def openvpn_interfaces():
    """A function that return a list of openvpn activated servers"""
    command = ['sudo', 'ip', 'addr', 'show']
    process = execute_command_without_arguments(command)
    with open('list_interfaces.txt', 'w') as interfaces_file:
        interfaces_file.write(process.stdout)

    command = ['sudo', 'awk', '/^[0-9]+: tun[0-9]+:/ { iface = $2 } /inet / { print iface, $2}', 'list_interfaces.txt']
    process = execute_command_without_arguments(command)

    interfaces = process.stdout
    interfaces = list(interfaces.split("\n"))
    list_vpn_interfaces = []
    for interface in interfaces:
        if interface.startswith('tun'):
            list_vpn_interfaces.append({"ifname": interface[:interface.find(':')],
                                        "name_interface": "tun",
                                        "ip_address": interface[interface.find(':')+2:interface.find('/')],
                                        "netmask": interface[interface.find('/')+1:]})

    return list_vpn_interfaces


def delete_openvpn_interface(interfaces_before, interfaces):
    """Find the name of the deleted openvpn interface in system"""
    list_name_interfaces = [interface["ifname"] for interface in interfaces]
    for interface in interfaces_before:
        if interface["ifname"] not in list_name_interfaces:
            return interface["ifname"]


def prefix_to_masque(prefix):
    # Prefix must be between 0 and 32
    if not 0 <= prefix <= 32:
        return "Invalid Prefix"

    # Initialize an empty mask as a 4-byte list
    masque = [0, 0, 0, 0]

    # Calculate the number of complete bytes in the mask
    octets_complets = prefix // 8

    # Calculate the binary value of the mask in full bytes
    for i in range(octets_complets):
        masque[i] = 255

    # Calculate the last partial byte of the mask (if there is one)
    octet_partiel = prefix % 8
    if octet_partiel > 0:
        masque[octets_complets] = 256 - 2**(8 - octet_partiel)

    # Convert the mask list to a character string in the format xxx.xxx.xxx.xxx
    masque_formatte = ".".join(map(str, masque))

    return masque_formatte


def json_to_str_server(json_object):
    """Function to convert a json object to an input of server config file"""
    
    config_input = f'''port {json_object["local_port"]}
proto {json_object["protocol"]}
dev {json_object["device_mode"]}
topology subnet

ca /etc/certificates_{json_object["ca_name"]}/ca.crt
cert /etc/openvpn/certificates_{json_object["server_cert"]}/server.crt
key /etc/openvpn/certificates_{json_object["server_cert"]}/server.key
dh /etc/openvpn/server/dh_{json_object['name']}.pem
crl-verify /etc/certificates_{json_object["ca_name"]}/crl.pem

tls-server
tls-auth /etc/openvpn/server/static_{json_object["name"]}.key

#server server_tunnel
#mode server
#ifconfig-pool start_ip_address end_ip_address
#server-bridge server_interface server_start server_end

push "redirect-gateway def1"
push "route 192.168.0.0 255.255.255.0"
#push "route remote"
#push "dhcp-option DOMAIN server"
#push "dhcp-option DNS server1"
#push "dhcp-option DNS server1"
#push "register-dns"
#push "dhcp-option NTP server1"
#push "dhcp-option NTP c"
multihome

duplicate-cn
#max-clients
#client-to-client
#engine rdrand
#tun-ipv6

cipher {json_object["encryption_algorithm"]}

keepalive 20 60
#comp-lzo
#compress migrate
#passtos
persist-key
persist-tun
daemon
#float

#openvpn status log
#status /var/log/openvpn/status.log

#enable log
log-append /var/log/openvpn/openvpn.log

#Log Level
verb {json_object["verbosity_level"]}'''

    if json_object["interface"] != "any":
        config_input = config_input.replace("multihome", f"local {json_object['interface_address']}")

    if json_object["hardware_crypto"] != "No Hardware Crypto":
        config_input = config_input.replace("#engine rdrand", "engine rdrand")
    
    if json_object["bridge"]["bridge_select"]:
        bridge_interface_address = json_object["bridge_interface_address"]
        prefix = int(bridge_interface_address[bridge_interface_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace('#server-bridge server_interface server_start server_end', 
                                            f"""server-bridge {bridge_interface_address[:bridge_interface_address.find('/')]} {mask} {json_object["bridge"]["bridge_start_dhcp"]} {json_object["bridge"]["bridge_start_dhcp"]}""")
    elif json_object["address_pool"]["address_pool_select"]:
        config_input = config_input.replace('#ifconfig-pool start_ip_address end_ip_address',
                                            f'ifconfig-pool {json_object["address_pool"]["address_pool_start"]} {json_object["address_pool"]["address_pool_end"]}')
        config_input = config_input.replace('#mode server','mode server')
    else:
        tunnel_address = json_object["ipv4_tunnel_network"]
        prefix = int(tunnel_address[tunnel_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("#server server_tunnel", f"server {tunnel_address[:tunnel_address.find('/')]} {mask}")

    if json_object["ipv4_local_network"] != '':
        local_address = json_object["ipv4_local_network"]
        prefix = int(local_address[local_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("push \"route 192.168.0.0 255.255.255.0\"", 
                                            f"push \"route {local_address[:local_address.find('/')]} {mask}\"")
        
    if json_object["ipv4_remote_network"] != '':
        remote_address = json_object["ipv4_remote_network"]
        prefix = int(remote_address[remote_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("#push \"route remote\"", 
                                            f"push \"route {remote_address[:remote_address.find('/')]} {mask}\"")
    
    if json_object["concurrent_connections"] != '':
        config_input = config_input.replace("#max-clients", f"max-clients {json_object['concurrent_connections']}")
        
    if not json_object["gateway"]:
        config_input = config_input.replace("push \"redirect-gateway def1\"", "#push \"redirect-gateway def1\"")

    if json_object["compression"] == "disabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo no")
        config_input = config_input.replace("#compress migrate", "compress migrate")
    elif json_object["compression"] == "enabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo yes")
        config_input = config_input.replace("#compress migrate", "compress migrate")
    elif json_object["compression"] == "adaptive":
        config_input = config_input.replace("#comp-lzo", "comp-lzo adaptive")
        config_input = config_input.replace("#compress migrate", "compress migrate")

    if json_object["type_of_service"]:
        config_input = config_input.replace("#passtos", "passtos")

    if not json_object["duplicate_connections"]:
        config_input = config_input.replace("duplicate-cn", "#duplicate-cn")

    if json_object["ipv6"]:
        config_input = config_input.replace("#tun-ipv6", "tun-ipv6")

    if json_object["inter_clients"]:
        config_input = config_input.replace("#client-to-client", "client-to-client")

    if json_object["dynamic_ip"]:
        config_input = config_input.replace("#float", "float")

    if not json_object["topology"]:
        config_input = config_input.replace("topology subnet", "#topology subnet")

    if json_object["dns_default_domain"]["dns_default_domain_select"]:
        config_input = config_input.replace("#push \"dhcp-option DOMAIN server\"", f"push \"dhcp-option DOMAIN {json_object['dns_default_domain']['dns_default_domain_server']}\"")

    if json_object["dns_servers"]["dns_servers_select"]:
        config_input = config_input.replace("#push \"dhcp-option DNS server1\"", f"push \"dhcp-option DNS {json_object['dns_servers']['dns_server1']}\"")
        if json_object["dns_servers"]["dns_server2"] != '':
            config_input = config_input.replace("#push \"dhcp-option DNS server2\"", f"push \"dhcp-option DNS {json_object['dns_servers']['dns_server2']}\"")

    if json_object["force_dns"]:
        config_input = config_input.replace("#push \"register-dns\"", "push \"register-dns\"")

    if json_object["ntp_servers"]["ntp_servers_select"]:
        config_input = config_input.replace("#push \"dhcp-option NTP server1\"", f"push \"dhcp-option NTP {json_object['ntp_servers']['ntp_server1']}\"")
        if json_object["ntp_servers"]["ntp_server2"] != '':
            config_input = config_input.replace("#push \"dhcp-option NTP server2\"", f"push \"dhcp-option NTP {json_object['ntp_servers']['ntp_server2']}\"")

    return config_input


def json_to_str_client(json_object):
    """Function to convert a json object to input of client config file"""

    config_input = f'''client
remote {json_object["server_host"]} {json_object["server_port"]}
proto {json_object["protocol"]}
dev {json_object["device_mode"]}
multihome
#server server_tunnel

#resolv-retry infinite
#passtos
#comp-lzo
#compress migrate
#tun-ipv6
#engine rdrand
nobind
remote-cert-tls server
cipher {json_object["encryption_algorithm"]}
auth-nocache
script-security 2
persist-key
persist-tun
auth {json_object["auth_digest_algorithm"]}
verb {json_object["verbosity_level"]}
#lport

#ifconfig
#route remote

#pull
#auth-user-pass

#reneg-sec
#shaper

#proto tcp-client
#http-proxy

#route-nopull
#route-noexec

#Server Key and keep this is secret
ca /etc/certificates_{json_object["ca_name"]}/ca.crt
cert /etc/openvpn/client/certificates_{json_object["client_cert"]}/{json_object["client_cert"]}.crt
key /etc/openvpn/client/certificates_{json_object["client_cert"]}/{json_object["client_cert"]}.key
crl-verify /etc/certificates_{json_object["ca_name"]}/crl.pem

tls-client
tls-auth /etc/openvpn/client/static_{json_object["name"]}.key
'''

    if json_object["interface"] != "any":
        config_input = config_input.replace("multihome", f"local {json_object['interface_address']}")
        config_input = config_input.replace("nobind", "#nobind")
    
    if json_object["resolv_retry"]:
        config_input = config_input.replace("#resolv-retry", "resolv-retry")
    
    if json_object["proxy_host"] != '' and json_object["proxy_port"] != '':
        if json_object["proxy_authentication"]["option"] == 'none':
            config_input = config_input.replace("#proto tcp-client", "proto tcp-client")
            config_input = config_input.replace("#http-proxy",
                                                f"http-proxy {json_object['proxy_host']} {json_object['proxy_port']}")
        elif json_object["proxy_authentication"]["option"] == 'basic':
            # Create .pas file contains proxy username and password
            file_content = f'{json_object["proxy_authentication"]["username"]}\n{json_object["proxy_authentication"]["password"]}'
            with open(f'/etc/openvpn/client/client_{json_object["name"]}.pas', 'w') as proxy_auth_file:
                proxy_auth_file.write(file_content)
            config_input = config_input.replace("#proto tcp-client", "proto tcp-client")
            config_input = config_input.replace("#http-proxy", 
                                                f"http-proxy {json_object['proxy_host']} {json_object['proxy_port']} /etc/openvpn/client/client_{json_object['name']}.pas basic")
    
    if json_object["local_port"] != '':
        config_input = config_input.replace('#lport', f'lport {json_object["local_port"]}')
    
    if json_object["username"] != '' and json_object["password"] != '':
        # Create .up file contains username and password
        file_content = f'{json_object["username"]}\n{json_object["password"]}'
        with open(f'/etc/openvpn/client/client_{json_object["name"]}.up', 'w') as auth_file:
            auth_file.write(file_content)
        config_input = config_input.replace("#pull", "pull")
        config_input = config_input.replace("#auth-user-pass", f"auth-user-pass /etc/openvpn/client/client_{json_object['name']}.up")
        config_input = config_input.replace("client\n", "#client\n", 1)
        
    elif json_object["ipv4_tunnel_network"] != '':
        tunnel_address = json_object["ipv4_tunnel_network"]
        tunnel_address = tunnel_address[:tunnel_address.find('/')-1]
        config_input = config_input.replace("#ifconfig", f"ifconfig {tunnel_address}2 {tunnel_address}1")
        config_input = config_input.replace("client\n", "#client\n", 1)
        
    if json_object["renegotiate_time"] != '':
        config_input = config_input.replace("#reneg-sec", f"reneg-sec {json_object['renegotiate_time']}")

    if json_object["hardware_crypto"] != "No Hardware Crypto":
        config_input = config_input.replace("#engine rdrand", "engine rdrand")
    
    if json_object["ipv4_remote_network"] != '':
        remote_address = json_object["ipv4_remote_network"]
        prefix = int(remote_address[remote_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("#route remote", f"route {remote_address[:remote_address.find('/')]} {mask}")

    if json_object["limit_outgoing_bandwidth"] != '':
        config_input = config_input.replace("#shaper", f"shaper {json_object['limit_outgoing_bandwidth']}")
        
    if json_object["compression"] == "disabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo no")
        config_input = config_input.replace("#compress migrate", "compress migrate")
    elif json_object["compression"] == "enabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo yes")
        config_input = config_input.replace("#compress migrate", "compress migrate")
    elif json_object["compression"] == "adaptive":
        config_input = config_input.replace("#comp-lzo", "comp-lzo adaptive")
        config_input = config_input.replace("#compress migrate", "compress migrate")

    if json_object["type_of_service"]:
        config_input = config_input.replace("#passtos", "passtos")

    if json_object["ipv6"]:
        config_input = config_input.replace("#tun-ipv6", "tun-ipv6")

    if json_object["pull_routes"]:
        config_input = config_input.replace("#route-nopull", "route-nopull")

    if json_object["add_remove_routes"]:
        config_input = config_input.replace("#route-noexec", "route-noexec")

    return config_input


#function to update interface tables  
def update_openvpn_table(id,data):
    objectConfig=ServerOpenvpn.objects.get(id=id)
    # Set all attributes to None
    for field in objectConfig._meta.fields:
        if field.attname not in ["id"]: 
            setattr(objectConfig, field.attname, None)
    serializerServerOpenvpn= ServerOpenvpnSerializer(objectConfig,data=data)
    if serializerServerOpenvpn.is_valid():
            serializerServerOpenvpn.save()