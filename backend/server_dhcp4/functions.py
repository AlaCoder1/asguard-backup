from backend.network.functions_ipv4 import convert_to_subnet_mask
from backend.rules.functions import calculate_subnet_address
import ipaddress

from backend.server_dhcp4.serializers import DHCP4ServerSerializer

def calculate_address_range(ip_address, subnet_mask):
    network = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)
    return network.network_address + 1, network.network_address + network.num_addresses - 2
def create_dhcpv4_db(id_interface,ip_address4,netmask4):
    subnet_prefix=calculate_subnet_address(ip_address4+"/"+netmask4)
    print(subnet_prefix)
    subnet_addr=subnet_prefix.split("/")[0]
    subnet_mask=convert_to_subnet_mask(subnet_prefix.split("/")[1])
    first_address, last_address=calculate_address_range(ip_address4, subnet_mask)
    available_range=f"{first_address} - {last_address}"
    data_save={
        "subnet_addr":subnet_addr,
        "subnet_mask":subnet_mask,
        "available_range":available_range,
        "interface":id_interface
    }
    server_serializer=DHCP4ServerSerializer(data=data_save)
    if server_serializer.is_valid():
        server_serializer.save()





