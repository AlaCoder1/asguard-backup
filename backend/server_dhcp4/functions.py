from backend.network.functions_ipv4 import convert_to_subnet_mask
from backend.rules.functions import calculate_subnet_address
import ipaddress
from backend.server_dhcp4.serializers import DHCP4ServerSerializer
from backend.vlan.functions import execute_cmd

def parse_server_info(data):
    """function to parse server info from data input"""
    enable_dhcpv4 = False if data.get('enable_dhcpv4', False) == "" else data.get('enable_dhcpv4', False)
    subnet_addr=None if data.get('subnet_addr', None) == "" else data.get('subnet_addr', None)
    subnet_mask=None if data.get('subnet_mask', None) == "" else data.get('subnet_mask', None)
    dns_servers=[] if data.get('dns_server', []) == "" else data.get('dns_server', [])
    gateway=None if data.get('gateway', None) == "" else data.get('gateway', None)
    domain_name=None if data.get('domain_name', None) == "" else data.get('domain_name', None)
    dns_server = ' , '.join(filter(None, dns_servers)) if len(dns_servers)!=0 else None
    data_server={
        "enable_dhcpv4":enable_dhcpv4,
        "subnet_addr":subnet_addr,
        "subnet_mask":subnet_mask,
        "dns_server":dns_server,
        "gateway":gateway,
        "domain_name":domain_name,
        }
    return data_server

def is_ip_in_range(from_addrs,to_addrs, available_range):
    """function to test from address and to address in available range"""
    for i in range(len(from_addrs)):
        from_addr = ipaddress.ip_address(from_addrs[i])
        to_addr = ipaddress.ip_address(to_addrs[i])
        start_ip = ipaddress.ip_address(available_range.split("-")[0].strip())
        end_ip = ipaddress.ip_address(available_range.split("-")[1].strip())
        if start_ip <= from_addr <= end_ip and start_ip <= to_addr <= end_ip is False:
            return False
    return True

def calculate_address_range(ip_address, subnet_mask):
    """"function to calculate address pool default"""
    network = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)
    return network.network_address + 1, network.network_address + network.num_addresses - 2

def create_dhcpv4_db(id_interface,ip_address4,netmask4):
    """"save server in database after config ipv4 static on interface"""
    subnet_prefix=calculate_subnet_address(str(ip_address4)+"/"+str(netmask4))
    # print(subnet_prefix)
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

def retur_config_file(subnet_address,subnet_mask,ranges_from,ranges_to,dns_server,gateway,domain_name):
    """function to prepare config to write in file"""
    list_config_server=[]
    list_config_server+=[(f'option domain-name"{domain_name}";')if domain_name is not None else []]
    list_config_server+=[
        'subnet ' + subnet_address + ' netmask ' + subnet_mask + ' {' if subnet_address is not None and subnet_mask is not None else None,]
    config_pool=''
    if len(ranges_from)!=0:
        for i in range(len(ranges_from)):
            if ranges_from[i] is not None and ranges_to[i]:
                config_pool='pool { \n'
                config_pool+=f'range {ranges_from[i]} {ranges_to[i]};\n '
                config_pool+='}'
        list_config_server.append(config_pool)     
    if gateway is not None:
        list_config_server.append(f'option routers {gateway};')
    if dns_server is not None:
        list_config_server.append(f'option domain-name-servers {dns_server};')
    list_config_server+='}' 
    print(list_config_server)
    list_config_server=[x for x in list_config_server if x is not None]
    return list_config_server
    
def init_file_dhcp4(ifname):
    """function to init file conf of dhcpd.conf"""
    include_files='include "/etc/dhcp4_servers/{}/dhcpd.conf";'.format(ifname)
    commandes=[ 'mkdir -p /dhcp4_servers/'
                'mkdir -p /etc/dhcp4_servers/{}'.format(ifname), 
                "grep -q '{}' /etc/dhcpd.conf|| echo '{}' | sudo tee -a /etc/dhcpd.conf".format(include_files,include_files)
    ]
    for cmd in commandes:
        _, error = execute_cmd(cmd)
        print(cmd)
        if error!="":
            return error
    return True

def save_config_in_system(list_config,ifname):
    """function to apply config on system"""
    commandes=[
    """cat <<EOF > /etc/dhcp4_servers/{}/dhcpd.conf
{} 
EOF""".format(ifname,'\n'.join(list_config)),
    "systemctl enable --quiet dhcpd4.service && systemctl restart dhcpd4.service"

    ]
    for cmd in commandes:
        _, error = execute_cmd(cmd)
        if error!="":
            return error
    return True
