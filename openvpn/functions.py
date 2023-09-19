import time
import paramiko
from openvpn.models import ServerOpenvpn
from openvpn.serializers import ServerOpenvpnSerializer


class CommandExecutionError(Exception):
    """a class error when execution a command line"""
    def __init__(self, command, message="Error executing command"):
        self.command = command
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.command}"


def connect_ssh():
    """A function to connect with SSH"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.1.12.104', username='root', password='root')
    return ssh


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


def execute_list_commands_without_arguments(ssh_connect, commands_list):
    for command_number, command in enumerate(commands_list):
        stdin, stdout, stderr = ssh_connect.exec_command(command)
        print(f'command {command}')
        print('Error: ', stderr.read().decode('utf-8'))
        print('Output: ', stdout.read().decode('utf-8'))
        if stderr.read().decode('utf-8') != '':
            raise CommandExecutionError(command=command, message=stderr.read().decode('utf-8'))


def execute_command_with_arguments(ssh_connect, command, arguments, time_sleep=0.5):
    """Function that execute a command line with arguments like passing a passphrase in building certificate"""
    print(f"Command: {command}")
    # Open a session
    channel = ssh_connect.invoke_shell()

    # Send the command
    channel.send(f'{command}\n')
    time.sleep(time_sleep)

    # Send the list of arguments
    for arg in arguments:
        channel.send(f'{arg}\n')
        time.sleep(time_sleep)
    
    output_command = channel.recv(4096).decode('utf-8')
    print(f"output_command: {output_command}")

    # Close the session
    channel.close()
    return output_command


def execute_list_of_commands(ssh_connect, list_commands, time_sleep=0.5):
    for command in list_commands:
        # print(f"Command: {command['command']}")
        output_command = execute_command_with_arguments(ssh_connect=ssh_connect, command=command['command'], arguments=command['arguments'],
                                                        time_sleep=time_sleep)
        # print(f"output_command: {output_command}")


def json_to_str_server(json_object):
    """Function to convert a json object to an input of server config file"""
    
    config_input = f'''port {json_object["local_port"]}
proto {json_object["protocol"]}
dev {json_object["device_mode"]}
topology subnet

#ca /etc/certificates_ca/ca.crt
#cert /etc/openvpn/certificates_server/server.crt
#key /etc/openvpn/certificates_server/server.key
#dh /etc/openvpn/certificates_server/dh.pem

#tls-server
#tls-auth /etc/openvpn/server/static_{json_object["name"]}.key

#secret /etc/openvpn/server/static_{json_object["name"]}.key

server 10.8.1.0 255.255.255.0

#server-bridge server_start server_end

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
#client-to-client
#engine rdrand
#tun-ipv6

cipher {json_object["encryption_algorithm"]}

keepalive 20 60
#comp-lzo
#passtos
persist-key
persist-tun
daemon
#float

#openvpn status log
#status /var/log/openvpn/status.log

#enable log
#log-append /var/log/openvpn/openvpn.log

#Log Level
verb {json_object["verbosity_level"]}'''

    if json_object["interface"] != "any":
        config_input = config_input.replace("multihome", f"local {json_object['interface_address']}")

    if json_object["cert_method"]["method_name"] == "cert":
        config_input = config_input.replace("#ca /etc/certificates_ca/ca.crt", f'ca /etc/certificates_{json_object["cert_method"]["ca_name"]}/ca.crt')
        config_input = config_input.replace("#cert /etc/openvpn/certificates_server/server.crt", f'cert /etc/openvpn/certificates_{json_object["cert_method"]["server_cert"]}/server.crt')
        config_input = config_input.replace("#key /etc/openvpn/certificates_server/server.key", f'key /etc/openvpn/certificates_{json_object["cert_method"]["server_cert"]}/server.key')
        config_input = config_input.replace("#dh /etc/openvpn/certificates_server/dh.pem", f'dh /etc/openvpn/server/dh_{json_object["name"]}.pem')
    else:
        config_input = config_input.replace("#secret /etc/openvpn/", "secret /etc/openvpn/")

    if json_object["hardware_crypto"] != "No Hardware Crypto":
        config_input = config_input.replace("#engine rdrand", "engine rdrand")

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
                                            f"push \"route {remote_address[:remote_address.find('/')+1]} {mask}\"")
        
    if not json_object["gateway"]:
        config_input = config_input.replace("push \"redirect-gateway def1\"", "#push \"redirect-gateway def1\"")

    if json_object["compression"] == "disabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo no")
    elif json_object["compression"] == "enabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo yes")
    elif json_object["compression"] == "adaptive":
        config_input = config_input.replace("#comp-lzo", "comp-lzo adaptive")

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

    print(config_input)
    return config_input


def json_to_str_client(json_object):
    """Function to convert a json object to input of client config file"""
    config_input = f'''client
remote {json_object["ipv4_remote"]} {json_object["local_port"]}
proto {json_object["protocol"]}
dev {json_object["device_mode"]}
#resolv-retry infinite
#passtos
#comp-lzo
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

#Server Key and keep this is secret
ca /etc/certificates_{json_object["cert_method"]["ca_name"]}/ca.crt
cert /etc/openvpn/client/certificates_{json_object["cert_method"]["client_cert"]}/{json_object["cert_method"]["client_cert"]}.crt
key /etc/openvpn/client/certificates_{json_object["cert_method"]["client_cert"]}/{json_object["cert_method"]["client_cert"]}.key
#secret
tls-version-min 1.2
tls-cipher TLS-DHE-RSA-WITH-AES-256-GCM-SHA384:TLS-DHE-RSA-WITH-AES-128-GCM-SHA256:TLS-DHE-RSA-WITH-AES-256-CBC-SHA256:TLS-DHE-RSA-WITH-AES-128-CBC-SHA256'''
    
    if json_object["hardware_crypto"] != "No Hardware Crypto":
        config_input = config_input.replace("#engine rdrand", "engine rdrand")
    if json_object["resolv_retry"]:
        config_input = config_input.replace("#resolv-retry", "resolv-retry")
    if json_object["compression"] == "disabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo no")
    elif json_object["compression"] == "enabled":
        config_input = config_input.replace("#comp-lzo", "comp-lzo yes")
    elif json_object["compression"] == "adaptive":
        config_input = config_input.replace("#comp-lzo", "comp-lzo adaptive")
    if json_object["type_of_service"]:
        config_input = config_input.replace("#passtos", "passtos")
    if json_object["ipv6"]:
        config_input = config_input.replace("#tun-ipv6", "tun-ipv6")
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