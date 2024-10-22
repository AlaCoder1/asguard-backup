from .functions import *
#############################################ipv4#############################################
################### None 
# convert  to None
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
    #lancer la fonction de "remove old config"
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
