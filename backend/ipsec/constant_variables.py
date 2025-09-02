from decouple import config
from drf_yasg.openapi import TYPE_ARRAY, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, Schema


PATH_IPSEC_CONF = '/etc/ipsec.conf'
PATH_IPSEC_SECRETS = '/etc/ipsec.secrets'
PATH_IPSEC_D = '/etc/ipsec.d/'
PATH_IPSEC_D_PRIVATE = '/etc/ipsec.d/private/'
PATH_IPSEC_D_CACERTS = '/etc/ipsec.d/cacerts/'
PATH_IPSEC_D_CERTS = '/etc/ipsec.d/certs/'
PATH_IPSEC_D_FINGER_PRINTS = '/etc/ipsec.d/finger_prints/'

IPV4_CONFIG = 'IPv4 config'
CONSTANT_METHOD_PSK = "Mutual PSK"
CONSTANT_METHOD_RSA = "Mutual RSA"
CONSTANT_METHOD_PUBLIC_KEY = "Mutual Public key"
CONSTANT_REQUEST_BODY_IPSEC = {
            'conn_name': Schema(type=TYPE_STRING, example="tun_ipsec"),
            'connection_method': Schema(type=TYPE_STRING, enum=["default", "Respond Only", "Start on traffic", "Start immediate"]),
            'key_exchange': Schema(type=TYPE_OBJECT, required=['key_exchange_version'],
                                   properties={'key_exchange_version': Schema(type=TYPE_STRING, default="auto", enum=["auto", "V1", "V2"]),
                                               'negotiation_mode': Schema(type=TYPE_STRING, description="When Key version is V1", enum=["Main", "Aggressive"])}),
            'internet_protocol': Schema(type=TYPE_STRING, enum=["IPv4", "IPv6"]),
            'interface_name': Schema(type=TYPE_STRING, example="WAN", description="Interface name like LAN or WAN or any"),
            'remote_gateway': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Remote address in format of x.x.x.x"),
            'dynamic_gateway': Schema(type=TYPE_BOOLEAN, default=False),
            'description_ph1': Schema(type=TYPE_STRING, example="Description phase 1"),
            'authentication': Schema(type=TYPE_OBJECT, required=['authentication_method'],
                                     properties={'authentication_method': Schema(type=TYPE_STRING, default=CONSTANT_METHOD_PSK, enum=[CONSTANT_METHOD_PSK, CONSTANT_METHOD_PUBLIC_KEY, CONSTANT_METHOD_RSA]),
                                                 'pre_shared_key': Schema(type=TYPE_STRING, example="bB8u6Tj60uJL2RKYR0OCyiGMdds9gaEUs9Q2d3bRTTVRKJ516CCc1LeSMChAI0rc----", description="required when authentication_method is Mutual PSK"),
                                                 'local_key_pair': Schema(type=TYPE_STRING, example="local_public_key", description="required when authentication_method is Mutual Public Key"),
                                                 'peer_key_pair': Schema(type=TYPE_STRING, example="peer_public_key", description="required when authentication_method is Mutual Public Key"),
                                                 'cert': Schema(type=TYPE_STRING, example="cert_server", description="Certificate (has a private key) name from list of certificates, required when authentication_method is Mutual RSA"),
                                                 'remote_cert': Schema(type=TYPE_STRING, example="remote_cert_server", description="Certificate name from list of certificates, required when authentication_method is Mutual RSA")}),
            'encryption_algorithm_ph1': Schema(type=TYPE_STRING, enum=["128", "192", "256", "aes128", "aes192", "aes256"]),
            'hash_algorithm_ph1': Schema(type=TYPE_ARRAY, example=["sha384", "sha256"], items=Schema(type=TYPE_STRING, description="User can choose more than one.Every choosed algorithm should be",)),
            'dh_key_group': Schema(type=TYPE_ARRAY, example=["15:3072", "20:384"], description="User can choose more than one.Every choosed algorithm should be like group:key", items=Schema(type=TYPE_STRING)),
            'lifetime_ph1': Schema(type=TYPE_STRING, example="3600", description="set lifetime", pattern=r"(\d+)"),
            'policy': Schema(type=TYPE_BOOLEAN, default=True),
            'rekey': Schema(type=TYPE_BOOLEAN, default=False),
            'reauth': Schema(type=TYPE_BOOLEAN, default=False),
            'nat_traversal': Schema(type=TYPE_STRING, default="auto", enum=["Disable", "E,able", "Force"]),
            'mobike': Schema(type=TYPE_BOOLEAN, default=False),
            'deed_peer': Schema(type=TYPE_OBJECT, description="Deed Peer block", required=['disable'],
                                properties={'disable': Schema(type=TYPE_BOOLEAN, default=False),
                                            'deed_peer_delay': Schema(type=TYPE_STRING, example="10", pattern=r"(\d+)", description="set deed peer delay, required when selecting deed peer"),
                                            'deed_peer_timeout': Schema(type=TYPE_STRING, example="160", pattern=r"(\d+)", description="set deed peer timeout, required when selecting deed peer"),
                                            'deed_peer_action': Schema(type=TYPE_STRING, enum=["default", "Restart the tunnel", "Stop the tunnel"], default="default", description="set deed peer action, required when selecting deed peer")}),
            'inactivity_timeout': Schema(type=TYPE_STRING, example="10", description="set inactivity timeout", pattern=r"(\d+)"),
            'margin_time': Schema(type=TYPE_STRING, example="10", description="set margin time", pattern=r"(\d+)"),
            'rekey_fuzz': Schema(type=TYPE_STRING, example="10", description="set rekey_fuzz", pattern=r"(\d+)"),
            'mode_ph2': Schema(type=TYPE_OBJECT, description="General information of phase 2", required=['mode'],
                               properties={'mode': Schema(type=TYPE_STRING, default="Tunnel IPv4", enum=["Tunnel IPv4", "Tunnel IPv6", "Transport"], description="At this time only Tunnel IPv4 is working"),
                                           'local_address': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Local Address, required when selecting Route-based"),
                                           'remote_address': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Remote Address, required when selecting Route-based"),}),
            'description_ph2': Schema(type=TYPE_STRING, example="Description phase 2"),
            'local_network': Schema(type=TYPE_OBJECT, description="Local network block", required=['type_local_network'],
                                    properties={'type_local_network': Schema(type=TYPE_STRING, default="Address", enum=["Address", "Network", "WAN subnet", "LAN subnet"]),
                                                'address_local_network': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Public address of local network, required when selecting Address or Network"),
                                                'mask': Schema(type=TYPE_STRING, example="24", description="Public address mask, required when selecting Network"),}),
            'remote_network': Schema(type=TYPE_OBJECT, description="Remote network block", required=['type_remote_network', 'address_remote_network'],
                                     properties={'type_remote_network': Schema(type=TYPE_STRING, default="Address", enum=["Address", "Network"]),
                                                 'address_remote_network': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="Public address of remote network"),
                                                 'mask': Schema(type=TYPE_STRING, example="24", description="Public address mask, required when selecting Network"),}),
            'sa_key_exchange': Schema(type=TYPE_OBJECT, description="Key Exchange block", required=['protocol', 'hash_algorithm_ph2', 'pfs_key_group'],
                                      properties={'protocol': Schema(type=TYPE_STRING, default="ESP", enum=["ESP", "AH"]),
                                                  'encryption_algorithm_ph2': Schema(type=TYPE_ARRAY, example=["256", "128"], items=Schema(type=TYPE_STRING), description="User can choose more than one"),
                                                  'hash_algorithm_ph2': Schema(type=TYPE_ARRAY, example=["sha256", "sha512"], items=Schema(type=TYPE_STRING), description="User can choose more than one.Every choosed algorithm should be like sha256"),
                                                  'pfs_key_group': Schema(type=TYPE_STRING, example="15:3072", description="If not off should be group:key")}),
            'lifetime_ph2': Schema(type=TYPE_STRING, example="3600", description="set lifetime in seconds", pattern=r"(\d+)"),}
