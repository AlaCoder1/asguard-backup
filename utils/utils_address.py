from ipaddress import AddressValueError, IPv4Address, IPv4Interface, NetmaskValueError, ip_address, ip_network


def is_valid_ipv4_with_mask(ip: str):
    """
    Validates whether the given string is a valid IPv4 address with a subnet mask.
    An address is considered valid if it is in the format 'x.x.x.x/mask' 
    and can be parsed as an IPv4 interface.
    """
    try:
        if ip != "":
            if len(ip.split("/")) == 1:
                return False
            IPv4Interface(ip)
        return True
    except (AddressValueError, NetmaskValueError) as err:
        print(err)
        return False


def is_valid_ipv4_without_mask(ip: str):
    """
    Validates whether the given string is a valid IPv4 address without a subnet mask.
    An address is considered valid if it is in the format 'x.x.x.x' 
    and can be parsed as an IPv4 Address.
    """
    try:
        if ip != "":
            IPv4Address(ip)
        return True
    except AddressValueError:
        return False


def fix_ipv4_address(list_ipv4_address: list[str]):
    """
    Takes a list of IPv4 addresses in the format 'x.x.x.x/mask', removes leading zeros from each octet, 
    and adjusts each address to its correct network address based on the subnet mask.

    Example:
        Input: ["10.01.01.85/24", "192.168.000.100/16", "192.168.000.100"]
        Output: ["10.1.1.0/24", "192.168.0.0/16", "192.168.0.100"]
    """
    adjust_list_ipv4_address = []
    for ipv4_address in list_ipv4_address:
        if ipv4_address != "":
            # Seperate network address from subnet mask if it exists
            ipv4_address_list = ipv4_address.split("/")
            ipv4_address = ipv4_address_list[0]
            # Removing leading zeros
            ipv4_address = '.'.join(str(int(octet)) for octet in ipv4_address.split('.'))
            # Get the subnet mask
            if len(ipv4_address_list) == 2:
                network_mask = ipv4_address_list[1]
                ipv4_address = f"{ipv4_address}/{network_mask}"
            # Fix the IPv4 address
            ipv4_address = str(IPv4Interface(ipv4_address).network.network_address)
            # Return the IPv4 address with its subnet mask if exist
            if len(ipv4_address_list) == 2:
                ipv4_address = f"{ipv4_address}/{network_mask}"
        adjust_list_ipv4_address.append(ipv4_address)
    return adjust_list_ipv4_address


def is_same_subnet(ip: str, subnet: str):
    """Function that check if an IP address in format of x.x.x.x belongs to the same subnet
      as another address with a subnet mask:"""
    try:
        network = ip_network(subnet, strict=False)
        return ip_address(ip) in network
    except ValueError:
        return False
