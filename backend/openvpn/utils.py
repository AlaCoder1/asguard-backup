from backend.managementCertificates.constant_variables import PATH_CA_CRL_PEM, PATH_CA_CRT, PATH_CLIENT_CERT_CRT, PATH_CLIENT_CERT_KEY, PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY
from backend.openvpn.constant_variables import CONSTANT_COMP_LZO, CONSTANT_COMPRESS_MIGRATE, PATH_CLIENT_PAS, PATH_CLIENT_STATIC, PATH_CLIENT_UP, PATH_LOG_OPENVPN_LOG, PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD, PATH_SERVER_DH, PATH_SERVER_STATIC, PATH_STATUS_LOG
from utils.commands_utils import execute_command_without_arguments, write_file_from_system


def create_tls_file(tls_auth, path_tls):
    """Create TLS file by importing tls key or generating it"""
    if tls_auth['generate']:
        command = ['sudo', 'openvpn', '--genkey', 'secret', f'{path_tls}']
        execute_command_without_arguments(command)
    else:
        write_file_from_system(path_tls, f'{tls_auth["tls_key"]}\n')


def prefix_to_masque(prefix:int):
    """Convert address prefix to mask. For example: 24 will be 255.255.255.0"""
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
dev {json_object["device_mode"]}_{json_object["name"]}
topology subnet

ca {PATH_CA_CRT.format(json_object["ca_name"])}
cert {PATH_SERVER_CERT_CRT.format(json_object["server_cert"])}
key {PATH_SERVER_CERT_KEY.format(json_object["server_cert"])}
dh {PATH_SERVER_DH.format(json_object["name"])}
crl-verify {PATH_CA_CRL_PEM.format(json_object["ca_name"])}

tls-version-min 1.2
tls-server
tls-auth {PATH_SERVER_STATIC.format(json_object["name"])}

#server server_tunnel
#mode server
#ifconfig-pool start_ip_address end_ip_address
#server-bridge server_interface server_start server_end

push "redirect-gateway def1"
#push route local
#push route remote
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
#tun-ipv6

cipher {json_object["encryption_algorithm"]}
auth {json_object["auth_digest_algorithm"]}

keepalive 20 60
#{CONSTANT_COMP_LZO}
#{CONSTANT_COMPRESS_MIGRATE}
#passtos
persist-key
persist-tun
daemon
#float

#management localhost port path_password

#openvpn status log
#status {PATH_STATUS_LOG}

#enable log
log-append {PATH_LOG_OPENVPN_LOG}

#Log Level
#verb verbosity_level'''
    
    if json_object["protocol"].startswith("tcp"):
        config_input = config_input.replace(f'proto {json_object["protocol"]}', f'proto {json_object["protocol"]}-server')

    if json_object["interface"] != "Any":
        config_input = config_input.replace("multihome", f"local {json_object['interface_address']}")
    
    if json_object["bridge"]["bridge_select"]:  # When activating Bridge
        bridge_interface_address = json_object["bridge_interface_address"]
        prefix = int(bridge_interface_address[bridge_interface_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace('#server-bridge server_interface server_start server_end', 
                                            f"""server-bridge {bridge_interface_address[:bridge_interface_address.find('/')]} {mask} {json_object["bridge"]["bridge_start_dhcp"]} {json_object["bridge"]["bridge_end_dhcp"]}""")
    elif json_object["address_pool"]["address_pool_select"]:  # When activating Address Pool
        config_input = config_input.replace('#ifconfig-pool start_ip_address end_ip_address',
                                            f'ifconfig-pool {json_object["address_pool"]["address_pool_start"]} {json_object["address_pool"]["address_pool_end"]}')
        config_input = config_input.replace('#mode server','mode server')
    else:  # When Bridge and Address Pool are deactivated
        tunnel_address = json_object["ipv4_tunnel_network"]
        prefix = int(tunnel_address[tunnel_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("#server server_tunnel", f"server {tunnel_address[:tunnel_address.find('/')]} {mask}")

    if json_object["ipv4_local_network"] != '':
        local_address = json_object["ipv4_local_network"]
        prefix = int(local_address[local_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("#push route local", 
                                            f"push \"route {local_address[:local_address.find('/')]} {mask}\"")
        
    if json_object["ipv4_remote_network"] != '':
        remote_address = json_object["ipv4_remote_network"]
        prefix = int(remote_address[remote_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("#push route remote", 
                                            f"push \"route {remote_address[:remote_address.find('/')]} {mask}\"")
    
    if json_object["concurrent_connections"] != '':
        config_input = config_input.replace("#max-clients", f"max-clients {json_object['concurrent_connections']}")
        
    if not json_object["gateway"]:
        config_input = config_input.replace("push \"redirect-gateway def1\"", "#push \"redirect-gateway def1\"")

    if json_object["compression"] == "disabled":
        config_input = config_input.replace(f"#{CONSTANT_COMP_LZO}", f"{CONSTANT_COMP_LZO} no")
        config_input = config_input.replace(f"#{CONSTANT_COMPRESS_MIGRATE}", f"{CONSTANT_COMPRESS_MIGRATE}")
    elif json_object["compression"] == "enabled":
        config_input = config_input.replace(f"#{CONSTANT_COMP_LZO}", f"{CONSTANT_COMP_LZO} yes")
        config_input = config_input.replace(f"#{CONSTANT_COMPRESS_MIGRATE}", f"{CONSTANT_COMPRESS_MIGRATE}")
    elif json_object["compression"] == "adaptive":
        config_input = config_input.replace(f"#{CONSTANT_COMP_LZO}", f"{CONSTANT_COMP_LZO} adaptive")
        config_input = config_input.replace(f"#{CONSTANT_COMPRESS_MIGRATE}", f"{CONSTANT_COMPRESS_MIGRATE}")

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

    if json_object["dns_default_domain"]["dns_default_domain_select"]:
        config_input = config_input.replace("#push \"dhcp-option DOMAIN server\"", f"push \"dhcp-option DOMAIN {json_object['dns_default_domain']['dns_default_domain_server']}\"")

    if json_object["dns_servers"]["dns_servers_select"]:
        config_input = config_input.replace("#push \"dhcp-option DNS server1\"", f"push \"dhcp-option DNS {json_object['dns_servers']['dns_server1']}\"")
        if json_object["dns_servers"]["dns_server2"] != '':
            config_input = config_input.replace("#push \"dhcp-option DNS server2\"", f"push \"dhcp-option DNS {json_object['dns_servers']['dns_server2']}\"")

    if json_object["force_dns_cache_update"]:
        config_input = config_input.replace("#push \"register-dns\"", "push \"register-dns\"")

    if json_object["ntp_servers"]["ntp_servers_select"]:
        config_input = config_input.replace("#push \"dhcp-option NTP server1\"", f"push \"dhcp-option NTP {json_object['ntp_servers']['ntp_server1']}\"")
        if json_object["ntp_servers"]["ntp_server2"] != '':
            config_input = config_input.replace("#push \"dhcp-option NTP server2\"", f"push \"dhcp-option NTP {json_object['ntp_servers']['ntp_server2']}\"")

    if json_object["client_management"]["client_management_select"]:
        client_management_password = json_object["client_management"]["password"].replace("$", "\$")
        write_file_from_system(PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD.format(json_object["name"]),
                               client_management_password)
        config_input = config_input.replace("#management localhost port path_password", f"management localhost {json_object['client_management']['port']} {PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD.format(json_object['name'])}")

    if json_object["verbosity_level"] != '':
        config_input = config_input.replace("#verb verbosity_level", f"verb {json_object['verbosity_level']}")

    return config_input


def json_to_str_client(json_object):
    """Function to convert a json object to input of client config file"""

    config_input = f'''client
#remote server_host server_port
proto {json_object["protocol"]}
dev {json_object["device_mode"]}
nobind
#server server_tunnel

#resolv-retry infinite
#passtos
#{CONSTANT_COMP_LZO}
#{CONSTANT_COMPRESS_MIGRATE}
#tun-ipv6
remote-cert-tls server
cipher {json_object["encryption_algorithm"]}
auth-nocache
script-security 2
persist-key
persist-tun
auth {json_object["auth_digest_algorithm"]}
#verb verbosity_level
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
ca {PATH_CA_CRT.format(json_object["ca_name"])}
cert {PATH_CLIENT_CERT_CRT.format(json_object["client_cert"])}
key {PATH_CLIENT_CERT_KEY.format(json_object["client_cert"])}
crl-verify {PATH_CA_CRL_PEM.format(json_object["ca_name"])}

tls-version-min 1.2
tls-client
tls-auth {PATH_CLIENT_STATIC.format(json_object["name"])}
'''
    
    if json_object["protocol"].startswith("tcp"):
        config_input = config_input.replace(f'proto {json_object["protocol"]}', f'proto {json_object["protocol"]}-client')
    
    for server in json_object["server_remote"]:
        config_input = config_input.replace("#remote server_host server_port", f"#remote server_host server_port\nremote {server['host']} {server['port']}")

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
            write_file_from_system(f'/etc/openvpn/client/client_{json_object["name"]}.pas', file_content)
            config_input = config_input.replace("#proto tcp-client", "proto tcp-client")
            config_input = config_input.replace("#http-proxy", 
                                                f"http-proxy {json_object['proxy_host']} {json_object['proxy_port']} {PATH_CLIENT_PAS.format(json_object['name'])} basic")
    
    if json_object["local_port"] != '':
        config_input = config_input.replace('#lport', f'lport {json_object["local_port"]}')
    
    if json_object["username"] != '' and json_object["password"] != '':
        # Create .up file contains username and password
        file_content = f'{json_object["username"]}\n{json_object["password"]}'
        write_file_from_system(f'/etc/openvpn/client/client_{json_object["name"]}.up', file_content)
        config_input = config_input.replace("#pull", "pull")
        config_input = config_input.replace("#auth-user-pass", f"auth-user-pass {PATH_CLIENT_UP.format(json_object['name'])}")
        config_input = config_input.replace("client\n", "#client\n", 1)
        
    elif json_object["ipv4_tunnel_network"] != '':
        tunnel_address = json_object["ipv4_tunnel_network"]
        tunnel_address = tunnel_address[:tunnel_address.find('/')-1]
        config_input = config_input.replace("#ifconfig", f"ifconfig {tunnel_address}2 {tunnel_address}1")
        
    if json_object["renegotiate_time"] != '':
        config_input = config_input.replace("#reneg-sec", f"reneg-sec {json_object['renegotiate_time']}")
    
    if json_object["ipv4_remote_network"] != '':
        remote_address = json_object["ipv4_remote_network"]
        prefix = int(remote_address[remote_address.find("/")+1:])
        mask = prefix_to_masque(prefix)
        config_input = config_input.replace("#route remote", f"route {remote_address[:remote_address.find('/')]} {mask}")

    if json_object["limit_outgoing_bandwidth"] != '':
        config_input = config_input.replace("#shaper", f"shaper {json_object['limit_outgoing_bandwidth']}")
        
    if json_object["compression"] == "disabled":
        config_input = config_input.replace(f"#{CONSTANT_COMP_LZO}", f"{CONSTANT_COMP_LZO} no")
        config_input = config_input.replace(f"#{CONSTANT_COMPRESS_MIGRATE}", f"{CONSTANT_COMPRESS_MIGRATE}")
    elif json_object["compression"] == "enabled":
        config_input = config_input.replace(f"#{CONSTANT_COMP_LZO}", f"{CONSTANT_COMP_LZO} yes")
        config_input = config_input.replace(f"#{CONSTANT_COMPRESS_MIGRATE}", f"{CONSTANT_COMPRESS_MIGRATE}")
    elif json_object["compression"] == "adaptive":
        config_input = config_input.replace(f"#{CONSTANT_COMP_LZO}", f"{CONSTANT_COMP_LZO} adaptive")
        config_input = config_input.replace(f"#{CONSTANT_COMPRESS_MIGRATE}", f"{CONSTANT_COMPRESS_MIGRATE}")

    if json_object["type_of_service"]:
        config_input = config_input.replace("#passtos", "passtos")

    if json_object["ipv6"]:
        config_input = config_input.replace("#tun-ipv6", "tun-ipv6")

    if json_object["pull_routes"]:
        config_input = config_input.replace("#route-nopull", "route-nopull")

    if json_object["add_remove_routes"]:
        config_input = config_input.replace("#route-noexec", "route-noexec")
    
    if json_object["verbosity_level"] != '':
        config_input = config_input.replace("#verb verbosity_level", f"verb {json_object['verbosity_level']}")

    return config_input
