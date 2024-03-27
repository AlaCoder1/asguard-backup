from backend.network.functions_ipv4 import convert_to_subnet_mask
from backend.network.models import Interface
from backend.rules.functions import calculate_subnet_address
import ipaddress
from backend.server_dhcp4.models import ServerDhcp4
from backend.server_dhcp4.serializers import DHCP4ServerSerializer
from backend.vlan.functions import execute_cmd
from django.db.models import Q


def customize_error_msg(serializer):
    """function to custom error message serializer"""
    error_messages = [
    f"{field}: {error}"
    for field, errors in serializer.errors.items()
    for error in errors
]
    concatenated_error_message = "\n".join(error_messages)
    concatenated_error_message+="!"
    return concatenated_error_message

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
        print(from_addrs[i])
        from_addr = ipaddress.ip_address(from_addrs[i]) if ipaddress.ip_address(from_addrs[i]) else None
        to_addr = ipaddress.ip_address(to_addrs[i]) if ipaddress.ip_address(to_addrs[i]) else None
        start_ip = ipaddress.ip_address(available_range.split("-")[0].strip())
        end_ip = ipaddress.ip_address(available_range.split("-")[1].strip())
        if start_ip is None or start_ip is None or (start_ip <= from_addr <= end_ip and start_ip <= to_addr <= end_ip is False):
            return False
    return True

def calculate_address_range(ip_address, subnet_mask):
    """"function to calculate address pool default"""
    network = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)
    return network.network_address + 1, network.network_address + network.num_addresses - 2

def prepare_conf_server(id_interface,ip_address4,netmask4):
    """function to prepare data to save"""
    subnet_prefix=calculate_subnet_address(str(ip_address4)+"/"+str(netmask4))
    # print(subnet_prefix)
    subnet_prefix=subnet_prefix+"/32" if netmask4==32 else subnet_prefix
    subnet_addr=subnet_prefix.split("/")[0]
    subnet_mask=convert_to_subnet_mask(subnet_prefix.split("/")[1])
    first_address, last_address=calculate_address_range(ip_address4, subnet_mask)
    available_range=f"{first_address} - {last_address}"
    data_save={
        "subnet_addr":subnet_addr,
        "subnet_mask":subnet_mask,
        "available_range":available_range,
        'interface':id_interface
        
    }
    return data_save,subnet_addr,subnet_addr
def create_dhcpv4_db(id_interface,ip_address4,netmask4):
    """"save server in database after config ipv4 static on interface if exist update it if not create new one"""
    data_save,subnet_addr,subnet_addr=prepare_conf_server(id_interface,ip_address4,netmask4)
    if not ServerDhcp4.objects.filter(Q(subnet_addr=subnet_addr)|Q(available_range=subnet_addr)).exists() :
        if ServerDhcp4.objects.filter(Q(interface_id=id_interface)).exists():
            server_object=ServerDhcp4.objects.get(interface_id=id_interface)
            # data_save['interface']=server_object.interface_id
            server_serializer=DHCP4ServerSerializer(server_object,data=data_save)
        else:
            server_serializer=DHCP4ServerSerializer(data=data_save)
        if server_serializer.is_valid():
            server_serializer.save()
            return True
        else:
            return customize_error_msg(server_serializer)
            # return str(next(iter(server_serializer.errors.values()))[0]).strip('.')+"!"
    return True

def delete_dhcp4_server(id_interface,ifname):
    """"delete server config from system and database """
    if ServerDhcp4.objects.filter(interface_id=id_interface).exists():
        server_object=ServerDhcp4.objects.get(interface_id=id_interface)
        commandes=[
            '[ -e "/etc/dhcp4_servers/{}/dhcpd.conf" ] && echo -n > /etc/dhcp4_servers/{}/dhcpd.conf '.format(ifname,ifname),
            "systemctl restart --quiet dhcpd4.service"
        ]
        
        for cmd in commandes:
            _, error = execute_cmd(cmd)
            if error!="":
                return error
        server_object.delete()  
    return True
        
# def delete_dhcp4_server(id_interface,ifname):
#     """"delete server config from system and database """
#     if ServerDhcp4.objects.filter(interface_id=id_interface).exists():
#         server_object=ServerDhcp4.objects.get(interface_id=id_interface)
#         server_object.delete()
#         # config_server_interface=return_interfaces_server()
#         commandes=[
#             '[ -e "/etc/dhcp4_servers/{}/dhcpd.conf" ] && echo -n > /etc/dhcp4_servers/{}/dhcpd.conf '.format(ifname,ifname),
#             # 'echo -n > /etc/dhcp4_servers/{}/dhcpd.conf '.format(ifname),
#              """cat <<EOF > /etc/default/isc-dhcp-server
# {} 
# EOF""".format('\n'.join(config_server_interface)),
#             "systemctl restart dhcpd4.service"
#         ]
        
#         for cmd in commandes:
#             _, error = execute_cmd(cmd)
#             # print(cmd,error)
#             if error!="":
#                 return error
#     return True
        
def retur_config_file(subnet_address,subnet_mask,ranges_from,ranges_to,dns_server,gateway,domain_name):
    """function to prepare config to write in file"""
    list_config_server=[]
    list_config_server+=[(f'option domain-name"{domain_name}";')if domain_name is not None else None]
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
    # print(list_config_server)
    list_config_server=[x for x in list_config_server if x is not None ]
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
        # print(cmd)
        if error!="":
            return error
    return True

def return_interfaces_server():
    """function to return interfaces as server"""
    id_servers_interfaces=[server.interface_id for server in ServerDhcp4.objects.all()]
    all_interfaces = Interface.objects.filter(id__in=id_servers_interfaces)
    interface_names = [interface.ifname.split("@")[0] if interface.ifname.startswith("vlan") else interface.ifname for interface in all_interfaces ]
    interface_names=" ".join(interface_names)
    config_server_interface=[f'INTERFACES="{interface_names}";']
    return config_server_interface

def save_config_in_system(list_config,ifname):
    print(list_config)
    """function to apply config on system"""
    config_server_interface=return_interfaces_server()
    commandes=[
    """cat <<EOF > /etc/dhcp4_servers/{}/dhcpd.conf
{} 
EOF""".format(ifname,'\n'.join(list_config)),
    """cat <<EOF > /etc/default/isc-dhcp-server
{} 
EOF""".format('\n'.join(config_server_interface)),
    "systemctl enable --quiet dhcpd4.service && systemctl restart  --quiet dhcpd4.service"
    ]
    for cmd in commandes:
        _, error = execute_cmd(cmd)
        if error!="":
            return error
    return True

def parse_range_address(data_input):
    """parse list of addresses """
    available_range=None if data_input.get('available_range', None) == "" else data_input.get('available_range', None)
    ranges_address=[] if data_input.get("ranges_address",[]) == "" else data_input.get('ranges_address', [])
    ranges_from=[]
    ranges_to=[]
    if len(ranges_address)>0:
        for addr in ranges_address:
            ranges_from.append(addr['range_from'])
            ranges_to.append(addr['range_to'])
        
    return available_range,ranges_from,ranges_to

def save_server_db(data,ranges_from,ranges_to,server_object):
    """function to save changes of config server in database """
    range_from = ' , '.join(filter(None, ranges_from)) if len(ranges_from)!=0 else None
    range_to = ' , '.join(filter(None, ranges_to)) if len(ranges_to)!=0 else None
    data['range_from']=range_from
    data['range_to']=range_to
    data['interface']=server_object.interface_id
    serializer_server=DHCP4ServerSerializer(server_object,data=data)
    if serializer_server.is_valid():
        serializer_server.save()
        msg="Config server DHPV4 saved successfully!"
        status=200
    else:
        # msg=str(next(iter(serializer_server.errors.values()))[0]).strip('.')+"!"
        msg=customize_error_msg(serializer_server)
        status=400
    return msg,status