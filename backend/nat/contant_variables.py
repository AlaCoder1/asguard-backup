from decouple import config
from drf_yasg.openapi import TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Schema


CONSTANT_SNAT_RULE = 'SNAT rule'
CONSTANT_ONE_TO_ONE_NAT_RULE = 'OneToOneNat rule'
CONSTANT_DNAT_RULE = 'DNAT rule'

INIT_NAT_FILE_CONTENT = """table ip nat {
        chain postrouting {
                type nat hook postrouting priority srcnat; policy accept;
        }
 
        chain prerouting {
                type nat hook prerouting priority 100; policy accept;
        }
}"""

REQUEST_BODY_SNAT = Schema(
        type=TYPE_OBJECT, required=[
            'source_address', 'source_port', 'destination_address', 'destination_port',
            'snat_type'],
        properties={
            'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface"),
            'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6"], description="required when choosing Static"),
            'protocol': Schema(type=TYPE_STRING, enum=["udp", "tcp"], description="required when choosing Static"),
            'source_address': Schema(type=TYPE_STRING, example=config('IP_MASK1'), description="format of address/mask or blank for Any"),
            'source_port': Schema(type=TYPE_STRING, example="80"),
            'destination_address': Schema(type=TYPE_STRING, example=config('IP_MASK2'), description="format of address/mask or blank for Any"),
            'destination_port': Schema(type=TYPE_STRING, example="443"),
            'snat_type': Schema(type=TYPE_STRING, enum=["MASQ", "static"]),
            'translation_address_from': Schema(type=TYPE_STRING, example=config('IP_ADDRESS1'), description="required when choosing Static, format of address like 51.32.100.5"),
            'translation_address_to': Schema(type=TYPE_STRING, example=config('IP_ADDRESS2'), description="Optional when choosing Static, format of address like 51.32.100.10"),
            'translation_port': Schema(type=TYPE_STRING, example="100", description="Optional when choosing Static"),
            'description': Schema(type=TYPE_STRING, example="Description of SNAT", description="description of SNAT rule"),
            }
            )
REQUEST_BODY_ONE_TO_ONE_NAT = Schema(
        type=TYPE_OBJECT, required=['source_address', 'translation_address', 'destination_address'],
        properties={'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface"),
                    'source_address': Schema(type=TYPE_STRING, example=config('IP_MASK1'), description="format of address/mask"),
                    'destination_address': Schema(type=TYPE_STRING, example=config('IP_MASK2'), description="format of address/mask or blank for Any"),
                    'translation_address': Schema(type=TYPE_STRING, example=config('IP_MASK3'), description="format of address/mask"),
                    'description': Schema(type=TYPE_STRING, example="Description of One To One NAT", description="description of OneToOneNat rule"),
                    }
                    )
REQUEST_BODY_DNAT = Schema(type=TYPE_OBJECT, required=[
        'interface', 'tcp_ip', 'protocol', 'source_address', 'source_port_from', 'source_port_to',
        'external_address', 'internal_address', 'port_forwarding'],
    properties={
        'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface, can take value null"),
        'tcp_ip': Schema(type=TYPE_STRING, enum=["ipv4", "ipv6", ""]),
        'protocol': Schema(type=TYPE_STRING, enum=["", "udp", "tcp"]),
        'source_address': Schema(type=TYPE_STRING, example=config('IP_MASK1'), description="Format of address/mask or blank for Any"),
        'source_protocol': Schema(type=TYPE_STRING, enum=["udp", "tcp", ""]),
        'source_port': Schema(type=TYPE_STRING, example="80", description="Can be blank"),
        'source_port_from': Schema(type=TYPE_STRING, example="80", description="Can be blank"),
        'source_port_to': Schema(type=TYPE_STRING, example="443", description="Can be blank"),
        'external_address': Schema(type=TYPE_STRING, example=config('IP_ADDRESS1'), description="Format of address or blank for Any"),
        'internal_address': Schema(type=TYPE_STRING, example=config('IP_ADDRESS2'), description="Format of address or blank for Any"),
        'port_forwarding': Schema(type=TYPE_BOOLEAN, default=False),
        'destination_protocol': Schema(type=TYPE_STRING, enum=["udp", "tcp", ""], description="used when selecting Port Forwarding"),
        'destination_port_forwarding': Schema(type=TYPE_STRING, example="80", description="used when selecting Port Forwarding"),
        'destination_port_from': Schema(type=TYPE_STRING, example="80", description="used when selecting Port Forwarding"),
        'destination_port_to': Schema(type=TYPE_STRING, example="443", description="used when selecting Port Forwarding"),
        'destination_port': Schema(type=TYPE_STRING, example="5000", description="used when selecting Port Forwarding"),
        'description': Schema(type=TYPE_STRING, example="Description DNAT", description="description of DNAT rule"),
        }
        )

PATH_NFTABLES_CONF = '/etc/nftables.conf'
PATH_RULESET_NAT_DIRECTORY = '/etc/rules/nat/'
PATH_RULESET_NFT = PATH_RULESET_NAT_DIRECTORY + 'nat.nft'
