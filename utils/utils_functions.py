from ipaddress import IPv4Interface


def fix_ipv4_address(ipv4_address: str):
    """Function that take an ipv4 address in format of x.x.x.x 
    and return it in correct format. 
    In example 10.1.1.85/24 will be returned as 10.1.1.0/24"""
    if ipv4_address != "":
        network_address = str(IPv4Interface(ipv4_address).network.network_address)
        network_mask = ipv4_address.split("/")
        network_mask = network_mask[1]
        ipv4_address = f"{network_address}/{network_mask}"
    return ipv4_address
