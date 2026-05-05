from decouple import config
from drf_yasg.openapi import TYPE_ARRAY, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Schema


CONSTANT_COMP_LZO = "comp-lzo"
CONSTANT_COMPRESS_MIGRATE = "compress migrate"
CONSTANT_BODY_OPENVPN_SERVER = Schema(
    type=TYPE_OBJECT, 
    required=[
        'name', 'server_mode', 'protocol', 'device_mode', 'interface', 'local_port', 'tls_auth',
        'ca_name', 'server_cert', 'dh_params_length', 'encryption_algorithm',
        'auth_digest_algorithm', 'gateway', 'bridge', 'compression', 'type_of_service',
        'duplicate_connections', 'ipv6', 'inter_clients', 'address_pool', 'dynamic_ip',
        'dns_default_domain', 'dns_servers', 'force_dns', 'ntp_servers'],
    properties={
        'name': Schema(type=TYPE_STRING, example="server_tun"),
        'description': Schema(type=TYPE_STRING, example="Description of server openvpn"),
        'server_mode': Schema(type=TYPE_OBJECT, required=['mode'],
                              properties={
                                  'mode': Schema(type=TYPE_STRING, enum=["remote_access", "peer_to_peer"])}),
        'protocol': Schema(type=TYPE_STRING, enum=["udp4", "udp6", "tcp4", "tcp6"]),
        'device_mode': Schema(type=TYPE_STRING, enum=["tun", "tap"]),
        'interface': Schema(type=TYPE_STRING, example="WAN", description="Interface name like LAN or WAN or Any"),
        'local_port': Schema(type=TYPE_STRING, example="1111", description="port number with 4 digits"),
        'tls_auth': Schema(type=TYPE_OBJECT, description="importing tls key or generating it", required=['generate'],
                           properties={
                               'generate': Schema(type=TYPE_BOOLEAN, default=True),
                               'tls_key': Schema(type=TYPE_STRING, example="096ed822f21f5a93b4fec867cf0a62be\n34804e5eba4068e75d5f35941cf7d729\n1d7cf01e363fa842928bc2fae30d8dd9\n70893ec134aa7390c24efdf1b6e3ec36\n8e08cc7fcb5714f5a1d11a905f250c90\n09616a0eb77557456a3cf1ea5d843255\n347a9288a290ea5532ee70a39b092079\n9252ab0808c836bc93a9dd4a7be39c7a\n09a29d1aa7c400d92d95edfeac228e50\nb4402d393c8f58f5f32fd805c21d511e\n5207b8a4f1fa47e9d65b24dee4a5a766\na3e26c7008ec4299f4eb798742c929ef\nfae2add7ac94effb8c81603c90478867\n9e48c6f8d1280b78d9c30a84da48c7e8\n64bd18ef83a40c3ac6e9bf71c4d67abf\n81ba92fbc2055eb9c7eba33d3807c9cf", description="tls_key only when generate is false")}),
        'ca_name': Schema(type=TYPE_STRING, example="ca_create", description="Certificate authority name"),
        'server_cert': Schema(type=TYPE_STRING, example="cert_server", description="Certificate name"),
        'dh_params_length': Schema(type=TYPE_STRING, enum=["2048", "4096"]),
        'encryption_algorithm': Schema(type=TYPE_STRING, example="AES-256-GCM"),
        'auth_digest_algorithm': Schema(type=TYPE_STRING, example="SHA256", pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
        'ipv4_tunnel_network': Schema(type=TYPE_STRING, example=config('IP_MASK'), description="Tunnel IPv4 address in format address/mask like 10.8.1.0/24"),
        'gateway': Schema(type=TYPE_BOOLEAN, default=True),
        'bridge': Schema(type=TYPE_OBJECT, description="Bridge block only appears if the device mode is TAP", required=['bridge_select'],
                         properties={
                             'bridge_select': Schema(type=TYPE_BOOLEAN, default=False),
                             'bridge_interface': Schema(type=TYPE_INTEGER, example=1, description="ID of the interface bridge, required when selecting bridge"),
                             'bridge_start_dhcp': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Address start of the interface bridge like 192.168.10.254, required when selecting bridge"),
                             'bridge_end_dhcp': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Address end of the interface bridge like 192.168.1.3, required when selecting bridge"),}),
        'ipv4_local_network': Schema(type=TYPE_STRING, example=config('IP_MASK'), description="IPv4 local network address in format address/mask like 192.168.10.0/24"),
        'ipv4_remote_network': Schema(type=TYPE_STRING, example=config('IP_MASK'), description="IPv4 remote network address in format address/mask like 192.168.10.0/24"),
        'concurrent_connections': Schema(type=TYPE_STRING, example="8", description="Number of concurrent connections"),
        'compression': Schema(type=TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
        'type_of_service': Schema(type=TYPE_BOOLEAN, default=False),
        'duplicate_connections': Schema(type=TYPE_BOOLEAN, default=False),
        'ipv6': Schema(type=TYPE_BOOLEAN, default=False),
        'inter_clients': Schema(type=TYPE_BOOLEAN, default=False),
        'address_pool': Schema(type=TYPE_OBJECT, description="Address pool block", required=['address_pool_select'],
                               properties={
                                   'address_pool_select': Schema(type=TYPE_BOOLEAN, default=False),
                                   'address_pool_start': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Address pool start required when selecting address pool"),
                                   'address_pool_end': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Address pool end required when selecting address pool"),}),
        'dynamic_ip': Schema(type=TYPE_BOOLEAN, default=False),
        'dns_default_domain': Schema(type=TYPE_OBJECT, description="DNS default domain block", required=['dns_default_domain_select'],
                                     properties={
                                        'dns_default_domain_select': Schema(type=TYPE_BOOLEAN, default=False),
                                        'dns_default_domain_server': Schema(type=TYPE_STRING, example=config('SERVER_DNS'), description="Address default domain server like 8.8.8.8, required when selecting DNS default domain")}),
        'dns_servers': Schema(type=TYPE_OBJECT, description="DNS servers block", required=['dns_servers_select'],
                              properties={
                                  'dns_servers_select': Schema(type=TYPE_BOOLEAN, default=False),
                                  'dns_server1': Schema(type=TYPE_STRING, example=config('SERVER_DNS'), description="Address of DNS server1 required when selecting DNS servers"),
                                  'dns_server2': Schema(type=TYPE_STRING, example=config('SERVER_DNS'), description="Address of DNS server2 Optionally you can set the second DNS server afer setting the first DNS server"),}),
        'force_dns_cache_update': Schema(type=TYPE_BOOLEAN, default=False),
        'ntp_servers': Schema(type=TYPE_OBJECT, description="NTP servers block", required=['ntp_servers_select'],
                              properties={
                                  'ntp_servers_select': Schema(type=TYPE_BOOLEAN, default=False),
                                  'ntp_server1': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Address of NTP server1 like 8.8.8.8, required when selecting NTP servers"),
                                  'ntp_server2': Schema(type=TYPE_STRING, example="", description="Address of NTP server2 like 8.8.4.4, Optionally you can set the second NTP server afer setting the first NTP server"),}),
        'client_management': Schema(type=TYPE_OBJECT, description="Client Management Port block", required=['client_management_select'],
                                    properties={
                                        "client_management_select": Schema(type=TYPE_BOOLEAN, default=False),
                                        "port": Schema(type=TYPE_STRING, example="585", description="Port number like 17562"),
                                        "password": Schema(type=TYPE_STRING, example="aaaaaAAAAAAAAAAA5452-1123-affdfdfsszhGJMGFKY")}),
        'verbosity_level': Schema(type=TYPE_STRING, pattern=r'\d', default="3", description="Set a number of verbosity level"),
        }
        )
CONSTANT_BODY_OPENVPN_CLIENT = Schema(type=TYPE_OBJECT, required=[
        'server_name', 'name', 'server_mode', 'protocol', 'device_mode', 'resolv_retry',
        'local_port', 'tls_auth', 'ca_name', 'client_cert', 'encryption_algorithm',
        'auth_digest_algorithm', 'compression', 'type_of_service', 'ipv6', 'pull_routes',
        'add_remove_routes'],
    properties={
        'name': Schema(type=TYPE_STRING, example="client_server_tun"),
        'description': Schema(type=TYPE_STRING, example="Description client openvpn"),
        'server_mode': Schema(type=TYPE_OBJECT, required=['mode'],
                              properties={'mode': Schema(type=TYPE_STRING, enum=["peer_to_peer"])}),
        'protocol': Schema(type=TYPE_STRING, enum=["udp4", "udp6", "tcp4", "tcp6"]),
        'device_mode': Schema(type=TYPE_STRING, enum=["tun", "tap"]),
        'resolv_retry': Schema(type=TYPE_BOOLEAN, default=False),
        'proxy_host': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="address of poxy like 10.1.12.249"),
        'proxy_port': Schema(type=TYPE_STRING, example="1195", pattern=r"\d\d\d\d", default="1194", desciption="port number of 4 digits"),
        'proxy_authentication': Schema(type=TYPE_OBJECT, description="Additional options for proxy authentication", required=['option'],
                                       properties={
                                            'option': Schema(type=TYPE_STRING, default="none", enum=["none", "basic", "ntlm"]),
                                            'username': Schema(type=TYPE_STRING, example="user_proxy", description="required when choosing basic in authentication method option"),
                                            'password': Schema(type=TYPE_STRING, example="bB8u6Tj60uJL2RKYR0OCyiGMdds9gaEUs9Q2d3bRTTVRKJ516CCc1LeSMChAI0rc", description="required when choosing basic in authentication method option"),}),
        'local_port': Schema(type=TYPE_STRING, example="2222", description="local port number with 4 digits"),
        'username': Schema(type=TYPE_STRING, example="user_numeryx"),
        'password': Schema(type=TYPE_STRING, example="bB8u6Tj60uJL2RKYR0OCyiGMdds9gaEUs9Q2d3bRTTVRKJ516CCc1LeSMChAI0rc"),
        'renegotiate_time': Schema(type=TYPE_STRING, example="300", description="Number of seconds to renogotiate"),
        'tls_auth': Schema(type=TYPE_OBJECT, description="importing tls key or generating it", required=['generate'],
                           properties={'generate': Schema(type=TYPE_BOOLEAN, default=False),
                                       'tls_key': Schema(type=TYPE_STRING, example="096ed822f21f5a93b4fec867cf0a62be\n34804e5eba4068e75d5f35941cf7d729\n1d7cf01e363fa842928bc2fae30d8dd9\n70893ec134aa7390c24efdf1b6e3ec36\n8e08cc7fcb5714f5a1d11a905f250c90\n09616a0eb77557456a3cf1ea5d843255\n347a9288a290ea5532ee70a39b092079\n9252ab0808c836bc93a9dd4a7be39c7a\n09a29d1aa7c400d92d95edfeac228e50\nb4402d393c8f58f5f32fd805c21d511e\n5207b8a4f1fa47e9d65b24dee4a5a766\na3e26c7008ec4299f4eb798742c929ef\nfae2add7ac94effb8c81603c90478867\n9e48c6f8d1280b78d9c30a84da48c7e8\n64bd18ef83a40c3ac6e9bf71c4d67abf\n81ba92fbc2055eb9c7eba33d3807c9cf", description="tls_key only when generate is false")}),
        'ca_name': Schema(type=TYPE_STRING, example="ca_create", description="Certificate authority name"),
        'client_cert': Schema(type=TYPE_STRING, example="cert_client", description="Certificate name from Certificates list with type client"),
        'dh_params_length': Schema(type=TYPE_STRING, enum=["2048", "4096"]),
        'encryption_algorithm': Schema(type=TYPE_STRING, example="AES-256-GCM"),
        'auth_digest_algorithm': Schema(type=TYPE_STRING, example="SHA256", pattern=r'\bSHA\d+', description="start with SHA like SHA256"),
        'ipv4_tunnel_network': Schema(type=TYPE_STRING, example=config('IP_MASK'), description="Tunnel IPv4 address in format address/mask"),
        'ipv4_remote_network': Schema(type=TYPE_STRING, example=config('IP_MASK'), description="IPv4 remote network address in format address/mask"),
        'limit_outgoing_bandwidth': Schema(type=TYPE_STRING, example="100", description="Number of limit outgoing bandwith"),
        'compression': Schema(type=TYPE_STRING, enum=["no_preference", "disabled", "enabled", "adaptive"]),
        'type_of_service': Schema(type=TYPE_BOOLEAN, default=False),
        'ipv6': Schema(type=TYPE_BOOLEAN, default=False),
        'pull_routes': Schema(type=TYPE_BOOLEAN, default=False),
        'add_remove_routes': Schema(type=TYPE_BOOLEAN, default=False),
        'verbosity_level': Schema(type=TYPE_STRING, example="3", pattern=r'\d', default="3", description="Set a number of verbosity level"),
        'server_remote': Schema(type=TYPE_ARRAY, description="Set the list of servers remote",
                                items=Schema(type=TYPE_OBJECT, required=['host', 'port'],
                                             properties={'host': Schema(type=TYPE_STRING, example=config('IP_ADDRESS')),
                                                         'port': Schema(type=TYPE_INTEGER, example=1194),
                                                        },)),
        }
        )

PATH_DH_FILES = '/asguard/asguard/DH_files/dh_{}.pem'
PATH_OPENVPN = '/etc/openvpn/'

# Server Path
PATH_SERVER = '/etc/openvpn/server/'
PATH_SERVER_CONF = '/etc/openvpn/server/server_{}.conf'
PATH_SERVER_DH = '/etc/openvpn/server/dh_{}.pem'
PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD = '/etc/openvpn/server/management_password_{}.txt'
PATH_SERVER_STATIC = '/etc/openvpn/server/static_{}.key'
PATH_LOG_OPENVPN = '/var/log/openvpn/'
PATH_LOG_OPENVPN_LOG = '/var/log/openvpn/openvpn.log'
PATH_SERVER_LOG = '/var/log/openvpn/status-server_{}.log'
PATH_STATUS_LOG = '/var/log/openvpn/status.log'

# Client path
PATH_CLIENT = '/etc/openvpn/client/'
PATH_CLIENT_OVPN = '/etc/openvpn/client/client_{}.ovpn'
PATH_CLIENT_STATIC = '/etc/openvpn/client/static_{}.key'
PATH_CLIENT_UP = '/etc/openvpn/client/client_{}.up'
PATH_CLIENT_PAS = '/etc/openvpn/client/client_{}.pas'
