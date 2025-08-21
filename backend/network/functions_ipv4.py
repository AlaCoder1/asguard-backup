from django.http import JsonResponse
from backend.gateway.functions import get_gateway_dhcp, save_gateway_static_ip, save_gateways_database
from backend.network.validation import InvalidIPAddressException, InvalidNetmaskException, validate_ip_address, validate_netmask
from .functions import *
#############################################ipv4#############################################
################### None 
# convert  to None

def parse_static_ip4(data):
        ip_address4 =  None if data['value_setup_Ipv4'].get('ip_address4', None) == "" else  data['value_setup_Ipv4'].get('ip_address4', None)
        netmask4 =  None if data['value_setup_Ipv4'].get('netmask4', None) == "" else  data['value_setup_Ipv4'].get('netmask4', None)
        gateway4 =  None if data['value_setup_Ipv4']['gateway4'].get('value', None) == "" else  data['value_setup_Ipv4']['gateway4'].get('value', None)
        
        return ip_address4,netmask4,gateway4
  
###
def parse_dhcp_base_ip4(data):
    type_dhcp4 = data.get('value_setup_Ipv4')['typeDHCP4']
    alias_add =  None if data['value_setup_Ipv4'].get('alias_add', None) == "" else  data['value_setup_Ipv4'].get('alias_add', None)
    alias_mask =  None if data['value_setup_Ipv4'].get('alias_mask', None) == "" else  data['value_setup_Ipv4'].get('alias_mask', None)
    reject =  None if data['value_setup_Ipv4'].get('reject', None) == "" else  data['value_setup_Ipv4'].get('reject', None)
    hostname =  None if data['value_setup_Ipv4'].get('hostname', None) == "" else  data['value_setup_Ipv4'].get('hostname', None)
    data["alias_add"]=alias_add
    data["alias_mask"]=alias_mask
    data["reject"]=reject
    data["hostname"]=hostname
    return data,type_dhcp4,alias_add,alias_mask,reject,hostname

def parse_dhcp_advanced_ip4(data):
    timeout =  None if data['value_setup_Ipv4'].get('timeout', None) == "" else  data['value_setup_Ipv4'].get('timeout', None)
    retry =  None if data['value_setup_Ipv4'].get('retry', None) == "" else  data['value_setup_Ipv4'].get('retry', None)
    select_timeout =  None if data['value_setup_Ipv4'].get('select_timeout', None) == "" else  data['value_setup_Ipv4'].get('select_timeout', None)
    reboot =  None if data['value_setup_Ipv4'].get('reboot', None) == "" else  data['value_setup_Ipv4'].get('reboot', None)
    backoff =  None if data['value_setup_Ipv4'].get('backoff', None) == "" else  data['value_setup_Ipv4'].get('backoff', None)
    initial_interval =  None if data['value_setup_Ipv4'].get('initial_interval', None) == "" else  data['value_setup_Ipv4'].get('initial_interval', None)
    dhcp_client =  None if data['value_setup_Ipv4'].get('dhcp_client', None) == "" else  data['value_setup_Ipv4'].get('dhcp_client', None)
    lease_time  =  None if data['value_setup_Ipv4'].get('lease_time ', None) == "" else  data['value_setup_Ipv4'].get('lease_time', None)
    request =  None if data['value_setup_Ipv4'].get('request', None) == "" else  data['value_setup_Ipv4'].get('request', None)
    require =  None if data['value_setup_Ipv4'].get('require', None) == "" else  data['value_setup_Ipv4'].get('require', None)
    domain_name =  None if data['value_setup_Ipv4'].get('domain_name', None) == "" else  data['value_setup_Ipv4'].get('domain_name', None)
    domain_server =  None if data['value_setup_Ipv4'].get('domain_server', None) == "" else  data['value_setup_Ipv4'].get('domain_server', None)
    data["timeout"]=timeout
    data["retry"]=retry
    data["select_timeout"]=select_timeout
    data["reboot"]=reboot
    data["backoff"]=backoff
    data["initial_interval"]=initial_interval
    data["dhcp_client"]=dhcp_client
    data["lease_time"]=lease_time
    data["request"]=request
    data["require"]=require
    data["domain_name"]=domain_name
    data["domain_server"]=domain_server
    return data,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domain_name,domain_server,lease_time,request,require



def save_address_dhcp_ip4(setuptype_ip4,aux_main,ifname,name_interface,json_ipv4):
    ## for dhcp 4
    if setuptype_ip4 is None or setuptype_ip4.lower()=="static" or aux_main  :
        aux_gw_dhcp=True
    if setuptype_ip4.lower()=="dhcp" and not aux_main:
        #function to get dhcp address and mask
        ip_address4,netmask4=get_address_dhcp(ifname,"4")
        json_ipv4["ip_address"]=ip_address4
        json_ipv4["netmask"]=netmask4
        ###
        ##function to get gateway if typeIPV4 est DHCP Base or Advanced
        gwaddr4,metric,default_aux,far_aux,multiwan_aux=get_gateway_dhcp(ifname,"4")
        aux_gw_dhcp=save_gateways_database(gwaddr4,name_interface,default_aux,far_aux,multiwan_aux,metric,True,True)
    return aux_gw_dhcp,json_ipv4


def update_conn_None_IPV4(config,ifname):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP4Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 static
    commands=[
         "#Start IP4Config {}".format(ifname),
        "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
         "#End IP4Config {}".format(ifname)
    ]
    cmd_final=[ 
        "sudo ip addr flush dev {}".format(ifname),]
    return commands,config,cmd_final
################### Static 
###################
# convert  to static connexion 
def update_conn_static_IPV4(config,ifname,uuid,ipaddress,netmask,cmdgw,aux_main):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP4Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 static
    commands=[]
    cmd_final=[]
    if ipaddress is not None and netmask is not None and not aux_main:
        cmd_final.append("sudo nmcli connection modify {} ipv4.method manual ipv4.addresses {}/{}".format(uuid,ipaddress,netmask))
    if cmdgw is not  None:
        cmd_final+=[ 
            cmdgw,      
            ]
        
    return commands,config,cmd_final

################### Dhcp
####function to convert_to_subnet_mask 
def convert_to_subnet_mask(bits):
    
    cidr_bits = int(bits)
    if cidr_bits < 0 or cidr_bits > 32:
        return "Invalid CIDR bits"
    
    binary_mask = "1" * cidr_bits + "0" * (32 - cidr_bits)
    subnet_mask = ".".join([str(int(binary_mask[i:i+8], 2)) for i in range(0, 32, 8)])
    return subnet_mask
################
###return base config
def return_config_base_IPV4(ifname,reject,hostname,alias_add,alias_mask):
    configContenu=[]
    #contenu de fichier dhclient.conf "config base"
    if reject is not None:
        configContenu.append('reject {};'.format(reject))
    if hostname is not None:
        configContenu+=['interface "{}"'.format(ifname),
            '{',
        'send host-name "{}";'.format(hostname),
        '}']
    if alias_add is not None and alias_mask is not None:
         configContenu+=[ 'alias {',
        'interface "{}";'.format(ifname),
        'fixed-address {};'.format(alias_add),
        'option subnet-mask {};'.format(alias_mask),
        '}',]
        
    return configContenu

###return advanced config
def return_config_advanced_IPV4(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domaine_name,domain_server,lease_time,request,require):
    #contenu de fichier dhclient.conf "config advanced"
    config_settings = [
    (timeout, 'timeout {};'),
    (retry, 'retry {};'),
    (reboot, 'reboot {};'),
    (backoff, 'backoff-cutoff {};'),
    (select_timeout, 'select-timeout {};'),
    (initial_interval, 'initial-interval {};'),
    (reject, 'reject {};')
    ]

    configContenu = []
    for value, config_format in config_settings:
        if value is not None:
            configContenu.append(config_format.format(value))
    variables_to_check = [hostname, dhcp_client, domaine_name, domain_server, lease_time, request, require]

    if any(variable is not None for variable in variables_to_check):
        configContenu+=['interface "{}"'.format(ifname),
                '{',]
        if hostname is not None:
            configContenu.append('send host-name "{}";'.format(hostname))
        if dhcp_client is not None:
            configContenu.append('send dhcp-client-identifier {};'.format(dhcp_client))
        if domaine_name is not None:
            configContenu.append('supersede domain-name "{}";'.format(domaine_name)) 
        if  domain_server is not None:
            configContenu.append( 'prepend domain-name-servers {};'.format(domain_server)) 
        if lease_time is not None:
            configContenu.append( 'send dhcp-lease-time {};'.format(lease_time)) 
        if request is not None:
            configContenu.append( ' request {};'.format(request)) 
        if require is not None:
            configContenu.append( 'require {};'.format(require)) 
        configContenu.append("}")    
    if alias_add is not None and alias_mask is not None:
        configContenu+=[ 'alias {',
    'interface "{}";'.format(ifname),
    'fixed-address {};'.format(alias_add),
    'option subnet-mask {};'.format(alias_mask),
    '}',]        
         
 
    return configContenu

####create file
def create_file_IPV4(ifname,config_contenu,aux_main):
    #commandes pour créer un dossier et stocker le contenu dans dhclient.
    commands=[]
    if not aux_main:
        commands = ["""bash -c 'sudo mkdir -p /etc/Dhcp4Config/{} && sudo cat <<EOF > /etc/Dhcp4Config/{}/dhclient.conf
{}
EOF'""".format(ifname, ifname, '\n'.join(config_contenu))]
    return commands

# convert  to dhcp  connexion base and advanced
def update_conn_dhcp_IPV4(config,ifname,uuid,aux_main):
    
    commandes=[]
    cmd_final=[]
    if not aux_main:
        config=clean_old_config(config,"IP4Config {}".format(ifname))
        #la liste des commandes pour l'IPV4 dhcp
        commandes=[
        "#Start IP4Config {}".format(ifname),   
        "ExecStart=/usr/bin/dhclient -4 -cf  /etc/Dhcp4Config/{}/dhclient.conf  {} ".format(ifname,ifname),
        "#End IP4Config {}".format(ifname)
        ]
        cmd_final=[
            "sudo nmcli connection modify {} ipv4.method auto ipv4.addresses '' ipv4.gateway '' ipv4.route-metric '' ".format(uuid),
            "sudo dhclient -4 -v -cf  /etc/Dhcp4Config/{}/dhclient.conf".format(ifname),
    ]
    
    return commandes,config,cmd_final
### get address4 dhcp from system
def get_address_dhcp(ifname,aux_ip):
    cmd = "sudo ip -{} -o addr show dev {} | awk '{{split($4, a); print a[1]}}'".format(aux_ip,ifname)
    output, error = run_command(cmd)
    if error!="" or len(output)==0:
        return None,None
    else:
        output=output.split("\n")
        address=output[0].strip().split('/')[0]
        mask=output[0].strip().split('/')[1]
        return address,int(mask)

def configuration_ipv4(data,setuptype_ip4,uuid,ifname,name_interface,id_interface,aux_main,commandes_final,output_service):
    list_metric=[]
    json_ipv4={}
    commandes=[]
    cmd_final_ipv4=[]
    match setuptype_ip4.lower():
        case "none":
            #call function to convert address to None
            commandes,output_service,cmd_final_ipv4=update_conn_None_IPV4(output_service,ifname)
        case "static":
            type_dhcp4=''
            ip_address4,netmask4,gateway4=parse_static_ip4(data)
            cmdgw4=None
            cmdgw4,list_metric=save_gateway_static_ip(gateway4,uuid,name_interface,id_interface)
            commandes,output_service,cmd_final_ipv4=update_conn_static_IPV4(output_service,ifname,uuid,ip_address4,netmask4,cmdgw4,aux_main)
            json_ipv4={
            "name_interface":name_interface,"ifname":ifname,
            "ip_address":ip_address4,"netmask":netmask4,
            "typeip4":setuptype_ip4}
            
        case "dhcp" if not aux_main:
            data,type_dhcp4,alias_add,alias_mask,reject,hostname=parse_dhcp_base_ip4(data)
            alias_mask_converted=convert_to_subnet_mask(alias_mask)if alias_mask is not None else None
            ipv4_gw_interface=True
            if type_dhcp4.lower()=="base" :
                config_contenu=return_config_base_IPV4(ifname,reject,hostname,alias_add,alias_mask_converted)
                json_ipv4={
                "name_interface":name_interface,"ifname":ifname,
                "typeip4":setuptype_ip4,"typedhcp":type_dhcp4,
                "alias_add":alias_add,"alias_mask":alias_mask,
                "reject":reject,"hostname":hostname}
            if type_dhcp4.lower()=="advanced":
                data,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domain_name,domain_server,lease_time,request,require=parse_dhcp_advanced_ip4(data)
                config_contenu=return_config_advanced_IPV4(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domain_name,domain_server,lease_time,request,require)
                json_ipv4={
                "name_interface":name_interface,"ifname":ifname,
                "typeip4":setuptype_ip4,"typedhcp":type_dhcp4,
                "alias_add":alias_add,"alias_mask":alias_mask,
                "reject":reject,"hostname":hostname,
                "timeout":timeout,"retry":retry,
                "select_timeout":select_timeout,"reboot":reboot,
                "backoff":backoff,"initial_interval":initial_interval,
                "dhcp_client":dhcp_client,
                "lease_time":lease_time,
                "request":request,"require":require,
                "domain_name":domain_name,
                "domain_server":domain_server
        }
            commandes_final+=create_file_IPV4(ifname,config_contenu,aux_main)
            commandes,output_service,cmd_final_ipv4=update_conn_dhcp_IPV4(output_service,ifname,uuid,aux_main)
            
    return json_ipv4,commandes_final,commandes,cmd_final_ipv4,list_metric