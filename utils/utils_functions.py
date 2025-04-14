from ipaddress import IPv4Interface, ip_address, ip_network


def fix_ipv4_address(ipv4_address: str):
    """Function that take an ipv4 address in format of x.x.x.x 
    and return it in correct format. 
    In example 10.1.1.85/24 will be returned as 10.1.1.0/24"""
    if ipv4_address != "":
        # Seperate network address from mask
        ipv4_address_list = ipv4_address.split("/")
        ipv4_address = ipv4_address_list[0]
        network_mask = ipv4_address_list[1]
        # Removing leading zeros
        ipv4_address = '.'.join(str(int(octet)) for octet in ipv4_address.split('.'))
        ipv4_address = f"{ipv4_address}/{network_mask}"
        # Fix the IPv4 address
        network_address = str(IPv4Interface(ipv4_address).network.network_address)
        ipv4_address = f"{network_address}/{network_mask}"
    return ipv4_address


def is_same_subnet(ip: str, subnet: str):
    """Function that check if an IP address in format of x.x.x.x belongs to the same subnet
      as another address with a subnet mask:"""
    try:
        network = ip_network(subnet, strict=False)
        return ip_address(ip) in network
    except ValueError:
        return False
