from .models import *
from authentification.views import *
from network.address import *
####background task to execute it 
from django.conf import settings
import re
import time
import threading
from .models import *
from gateway.models import *
from gateway.serializers import *
###############################################################
####update in Database functions

#function to update config tables
def update_DB(id,data,model,IP4serializer):
    data={key: value for key, value in data.items() if value is not None}
    data['interface']=id
    if model.objects.filter(interface_id=id).exists():
        objectConfig=model.objects.get(interface_id=id)
        # Set all attributes to None
        for field in objectConfig._meta.fields:
            if field.attname not in ["id", "interface_id",'ifname','created_at','updated_at','created_by','updated_by']: 
                setattr(objectConfig, field.attname, None)
        setattr(objectConfig, 'updated_by', settings.CurrentUserId)
        serializerIP4Config = IP4serializer(objectConfig,data=data)
    else:
        serializerIP4Config = IP4serializer(data=data)
    if (serializerIP4Config.is_valid()):
        serializerIP4Config.save()
        return True
    return serializerIP4Config.errors
   

#function to update interface tables  
def update_interface_table(name_interface,data,InterfaceSerializer):
    data={key: value for key, value in data.items() if value is not None}
    objectConfig=Interface.objects.get(name_interface=name_interface)
    # Set all attributes to None
    for field in objectConfig._meta.fields:
        if field.attname not in ["id",'ifname','created_at','updated_at','name_interface','description','private_aux','bogon_aux']: 
            setattr(objectConfig, field.attname, None)
    serializerInterface= InterfaceSerializer(objectConfig,data=data)
    if serializerInterface.is_valid():
            serializerInterface.save()     
            return True
    return serializerInterface.errors 
############################################################  
def get_conn_name(ifname):
    cmd = "sudo nmcli connection show | awk '$NF == \"{}\" {{print}}'".format(ifname)
      ##executer cette commande
    stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
    output = stdout.read().decode('utf-8').split('  ')
    if len(output)==0:
        return None
    else:
        output=[value for value in output if value]
        uuid=output[1]
        return uuid
##get old configuration in service
def get_old_config():
    cmd = "cat /etc/systemd/system/Asguard-Networking.service"
    ssh.exec_command(cmd)
    stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
    error = stderr.read().decode('utf-8')
    output = stdout.read().decode('utf-8').split('\n')
    return output,error
   
##add requirement
def add_requirement(ifname,output):
    index=output.index('[Service]')
    values_to_add=['BindsTo=sys-subsystem-net-devices-{}.device'.format(ifname),
                    'After=sys-subsystem-net-devices-{}.device'.format(ifname)]
    values_to_add = [x for x in values_to_add if x not in output]
    output = output[:index] + values_to_add + output[index:]
    return output

###################    
##add exec_cmd
def add_cmd(output,commandes):
    index_cmd=output.index('[Install]') 
    
    output = output[:index_cmd] + commandes + output[index_cmd:]
    return output
################################# Function to execute command with timeout
def run_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def run_remote_command_with_timeout(type, typeDHCP4, ssh_client, command, timeout_seconds):
    def run_command_thread():
        nonlocal output, error
        output, error = run_command(ssh_client, command)

    start_time = time.time()
    output = None
    error = None

    command_thread = threading.Thread(target=run_command_thread)
    command_thread.start()
    command_thread.join(timeout=timeout_seconds)
    elapsed_time = time.time() - start_time

    # Create a new instance of your model
    new_entry = tempsExucution(type=type, cmd=command, temps=elapsed_time)
    # Save the instance to the database
    new_entry.save()
    if  (command.find("sudo dhclient")==-1) and error!="" and (error is not None and not error.startwith("Warning")) :
        # print("error::::",error)
        return error
    elif command_thread.is_alive():
        print(f"Command took too long ({elapsed_time:.2f} seconds). Sending Ctrl+C... {command}")
        stdin, stdout, stderr = ssh_client.exec_command('\x03')
        # interrupt_command = "sudo pkill -INT -f 'some_long_running_command'"
        # output,error=run_command(ssh_client, interrupt_command)
        print("Ctrl+C sent.")
        return "Command took too long ({elapsed_time:.2f} seconds). Sending Ctrl+C... {command}"
        
    else:
        print(f"Command not too long ({elapsed_time:.2f} seconds). {command}")
        return True
        
#function to run all commandes
def run_all_commands(commandes,setuptypeIP4,typeDHCP4,timeout):
    for cmd in commandes:
        out=run_remote_command_with_timeout(setuptypeIP4,typeDHCP4,ssh, cmd, timeout)
        if  out is not True :
            return out
    return True

#################################
###################
##désactiver interface dans le système
def desactiver_interface_remote(ifname,output):
    #la liste des commandes pour la désactivation de l'interface dans Asguard Service
    commands=[
         "#Start IP4Config {}".format(ifname),
         "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
         "ExecStart=/usr/bin/ip link set dev {} down".format(ifname),        
         "#End IP4Config {}".format(ifname)
    ]
    output=add_requirement(ifname,output)
    output=add_cmd(output,commands)
    #la liste des commandes à executer pour désactiver l'interface
    cmd_final=[ 
        "sudo sed -i '/{}/d' /etc/systemd/system/Asguard-Networking.service".format(ifname),
        "sudo sed -i '/{}/d' /etc/ConfigInterfaces".format(ifname),
        "sudo ip addr flush dev {}".format(ifname),
        "sudo ip link set dev {} down".format(ifname),
        """sudo cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output))
        
        ]
    for cmd in cmd_final:
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')
        if error:
            msg=error,"    :"+cmd
            return False
    return True

    # return commands,cmd_final
   
        
################### 
###################
##clean old config
def clean_old_config(config,typeConf):
    #test si les commentaires #start et #end exists
    if "#Start {}".format(typeConf) in config and "#End {}".format(typeConf) in config: 
        #indice #start
        i=config.index("#Start {}".format(typeConf))
        #indice #end
        j=config.index("#End {}".format(typeConf))
        #remove old config
        config=config[:i]+config[j+1:]
    return config
 
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
def update_conn_static_IPV4(config,ifname,uuid,ipaddress,netmask,cmdgw,IP4ConfigObject):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP4Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 static
    commands=[]
    cmd_final=[]
    if ipaddress is not None and ipaddress!=IP4ConfigObject.ip_address:
        cmd_final.append("sudo nmcli connection modify {} ipv4.method manual ipv4.addresses {}/{}".format(uuid,ipaddress,netmask))
    cmd_final+=[ 
         cmdgw,      
        "sudo nmcli conn down {} && sudo nmcli conn up {}".format(uuid, uuid),]
    
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
def create_file_IPV4(ifname,config_contenu):
    #commandes pour créer un dossier et stocker le contenu dans dhclient.conf
    commands = ["""bash -c 'sudo mkdir -p /etc/Dhcp4Config/{} && sudo cat <<EOF > /etc/Dhcp4Config/{}/dhclient.conf
{}
EOF'""".format(ifname, ifname, '\n'.join(config_contenu))]
    return commands

# convert  to dhcp  connexion base and advanced
def update_conn_dhcp_IPV4(config,ifname,uuid):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP4Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 dhcp
    commandes=[
     "#Start IP4Config {}".format(ifname),   
     "ExecStart=/usr/bin/dhclient -4 -cf  /etc/Dhcp4Config/{}/dhclient.conf  {} ".format(ifname,ifname),
     "#End IP4Config {}".format(ifname)
    ]
    cmd_final=[
        "sudo nmcli connection modify {} ipv4.method auto ipv4.addresses '' ipv4.gateway '' ipv4.route-metric '' ".format(uuid),
        "sudo nmcli conn down {} && sudo nmcli conn up {}".format(uuid, uuid),
        "sudo dhclient -4 -v -cf  /etc/Dhcp4Config/{}/dhclient.conf".format(ifname),
    ]
    
    return commandes,config,cmd_final

def get_address_dhcp(ifname,ssh):
    cmd = "ip -4 -o addr show dev {} | awk '{{split($4, a); print a[1]}}'".format(ifname)
    output, error = run_command(ssh, cmd)
    if error!="" or len(output)==0:
        return None,None
    else:
        output=output.split("\n")
        address=output[0].strip().split('/')[0]
        mask=output[0].strip().split('/')[1]
        return address,int(mask)
###################generic configuration

def generic_config(config,ifname,speed_duplex,addmac,mtuV,mssV,genericConfigObject):
    commandes=[]
    cmd_final=[]
    #traiter le speed_duplex
    match speed_duplex:
        case '100baseTx-FD':
            speedV=100
            duplexV='full'
        case '100baseTx-HD':
            speedV=100
            duplexV='half'
        case '10baseT-FD':
            speedV=10
            duplexV='full'
        case '10baseT-HD':
            speedV=10
            duplexV='half'
   #tester si addmac is not None
    if addmac is not None and (genericConfigObject!="" and genericConfigObject.addmac!=addmac):
            #lancer la fonction de "remove old config"
            config=clean_old_config(config,"addmac config {}".format(ifname))
             #la liste des commandes pour l'address mac
            commandes+=[
            "#Start addmac config {}".format(ifname),
            'ExecStart=/usr/bin/ip link set dev {} address {}'.format(ifname,addmac),
            "#End addmac config {}".format(ifname)
            ]
            cmd_final+=[
                'sudo ip link set dev {} address {}'.format(ifname,addmac),
            ]
    #tester si mtu is not None
    if mtuV is not None and (genericConfigObject!="" and mtuV!=genericConfigObject.mtuV!=mtuV):
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"mtu config {}".format(ifname))
        #la liste des commandes pour mtu
        commandes+=[
        "#Start mtu config {}".format(ifname),
        'ExecStart=/usr/bin/ip link set dev {} mtu {}'.format(ifname,mtuV),
        "#End mtu config {}".format(ifname)
            ]
        cmd_final+=[
        'sudo ip link set dev {} mtu {}'.format(ifname,mtuV),
         ]
    #tester si mtu is not None
    if mssV is not None and (genericConfigObject!="" and  mssV!=genericConfigObject.mssV):
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"mss config {}".format(ifname))
         #la liste des commandes pour mss
        commandes+=[
        "#Start mss config {}".format(ifname),
        'ExecStart=/usr/bin/iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -o {} -j TCPMSS --set-mss {}'.format(ifname,mssV),
        "#End mss config {}".format(ifname),
            ]
        cmd_final+=[
        'sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -o {} -j TCPMSS --set-mss {}'.format(ifname,mssV),
         ]
    #tester si speed_duplex is not None
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"speed duplex config {}".format(ifname))
    if speed_duplex is not None and (genericConfigObject!="" and speed_duplex!=genericConfigObject.speed_duplex):
        #la liste des commandes pour speed duplex
        commandes+=[
        "#Start speed duplex config {}".format(ifname),
        'ExecStart=/usr/bin/ethtool -s {} speed {} duplex {}'.format(ifname,speedV,duplexV),
        "#End speed duplex config {}".format(ifname),
                    ]
        cmd_final+=[
        'sudo ethtool -s {} speed {} duplex {}'.format(ifname,speedV,duplexV),
         ]
    elif speed_duplex is not None:
         cmd_final+=[
        'sudo ethtool -s {} autoneg on'.format(ifname),
         ]
    return commandes,config,cmd_final
#####################################################################################
#################Blockage address
####add all addresse 
def create_rule(address):
    #concatener tous les addresses à bloquer
    block=''
    for i in range(len(address)-1):
        block+=address[i]+','
    block+=address[-1]
    block='{ '+block+' } drop'
    return block


####create file
def create_file_nftables(ifname,rules):
    commands = [
        #cmd pour supprimer la configuration ancienne
        'if nft list tables | grep -q "filter_{}"; then sudo nft delete table inet filter_{} ; fi'.format(ifname,ifname),
        #cmd ajouter un dossier contenant le fichier config
        """bash -c 'sudo mkdir -p /etc/rulesNetwork/{} && cat <<EOF > /etc/rulesNetwork/{}/nftables.conf
{}
EOF' """.format(ifname, ifname, '\n'.join(rules))
      ]
    return commands

###Function to block private or bogons address
def block_address_commandes(config,ifname,bogon_aux,private_aux,interfaceObject):
    rule=''
    commandes=[]
    configuration=[]
    cmd_final=[]
    #tester si on bloque les addresses bogons ou private
    if bogon_aux or private_aux:
        #tester si on bloque les addresses bogons and private
        if bogon_aux and private_aux:
            #rules pour les adresses ipv4
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(bogon_address_ip4))
            #rules pour les adresses IPV6
            rule+='\n iifname {} ip6 saddr {}'.format(ifname,create_rule(bogon_address_ip6))    
        #tester si on bloque les addresses bogons seulement
        elif bogon_aux and not private_aux:
            #rules pour les adresses ipv4
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(bogon_address_ip4))
            #rules pour les adresses IPV6
            rule+='\n iifname {} ip6 saddr {}'.format(ifname,create_rule(bogon_address_ip6))
         #tester si on bloque les addresses privées seulement   
        elif private_aux and not bogon_aux:
            #rules pour les adresses ipv4
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(private_address))
        #le contenu de fichier config nftables.conf    
        rules=[
            'table inet filter_'+ifname+' {',
                    'chain input {',
                            'type filter hook input priority filter; policy accept;',
                            '{}'.format(rule),
            '        }',
            '}'
        ]  
        #call function to create file nftables.conf
        configuration=create_file_nftables(ifname,rules)
        ##cmd to block address
        commandes=[
            "#Start nftables config {}".format(ifname),
            'ExecStart=/usr/bin/nft -f /etc/rulesNetwork/{}/nftables.conf'.format(ifname),
            "#End nftables config {}".format(ifname)
            ]
        if interfaceObject !="" and private_aux!=interfaceObject.private_aux or bogon_aux!=interfaceObject.bogon_aux:
            cmd_final+=[
                'sudo nft -f /etc/rulesNetwork/{}/nftables.conf'.format(ifname),
            ]
    else:
        #call function to clean old config
       config=clean_old_config(config,"nftables config {}".format(ifname))
    return configuration,commandes,config,cmd_final

#############################################################################################################################################
#############################################ipv6#############################################
##static ipv6
# convert  to static connexion  ipv6 
def update_conn_static_ipv6(config,ifname,ip_address,netmask):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP6Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 static
    commands=[
         "#Start IP6Config {}".format(ifname),
        "ExecStart=/usr/bin/ip -6 addr flush dev {}".format(ifname),
        "ExecStart=/usr/bin/ip -6 addr add {}/{} dev {}".format(ip_address,netmask,ifname),
         "#End IP6Config {}".format(ifname)
    ]
    cmd_final=[ 
        "sudo ip -6 addr flush dev {}".format(ifname),
        "sudo ip -6 addr add {}/{} dev {}".format(ip_address,netmask,ifname)]
    return commands,config,cmd_final
##dhcp ipv6
###############
###return base config
def return_config_base_ipv6(ifname,id,Request_only,Prefix_delegation,prefix_hint,IPv4_connectivity,VLAN_priority):
    #contenu de fichier dhclient.conf "config base"
    configContenu=["interface {} {".format(ifname)]
    if Request_only==False:
        configContenu.append("  send ia-na {}; # request stateful address".format(id))
    configContenu += ["  request domain-name-servers;", 
                      "  request domain-name;",
                          "};"]   
    if Request_only==False:
        configContenu.append("id-assoc na {} { };".format(id))
    if Prefix_delegation is not None:
        # Setup the prefix delegation 
            configContenu.append("id-assoc pd {} {".format(id))
            if  prefix_hint is not None:
                preflen = 64 - Prefix_delegation
                configContenu.append("  prefix ::/{} infinity;".format(preflen))
                        
    return configContenu

###return advanced config
def return_config_advanced_ipv6(ifname,
id,IPv4_connectivity,VLAN_priority,information_only,
send_options,request_options,script,non_temporary,id_assoc,address,Nlifetime,Nvalid_time,
prefix_delegation,id_assoc_pd,IPv6_Prefix,Plifetime,Pvalid_time,
authname,protocol,algorithm,
rdm,keyname,royaume,keyid,secret,expire):
    #contenu de fichier dhcp6c.conf "config advanced"
 ####### 
    sendOptionString=""
    regex_pattern = r'\s*,\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    # Usamos re.split() para dividir la cadena en Python:
    options = re.split(regex_pattern,send_options)
    for opt in options:
        sendOptionString+=" send {};\n".format(opt)
 ####### 
    requestOptionString=""
    regex_pattern = r'\s*,\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    # Usamos re.split() para dividir la cadena en Python:
    options = re.split(regex_pattern,request_options)
    for opt in options:
        requestOptionString+=" request {};\n".format(opt) 
 ####### 
    informationOnlyString=""    
    if information_only==True:
       informationOnlyString+=" information-only;\n"
     
    configContenu=["interface {} {\n".format(ifname),
                   "{}".format(sendOptionString),
                   "{}".format(requestOptionString),
                   "{}".format(informationOnlyString),
                   "};"
                   ]
    id_assoc_statement_address=""
    if non_temporary==True:
        id_assoc_statement_address += "id-assoc na "
        if  id_assoc.isdigit():
            id_assoc_statement_address +=id_assoc
        else:
            id_assoc_statement_address+=id
        id_assoc_statement_address+="{\n"
        if address!='' and Nlifetime.isdigit() or Nlifetime == 'infinity':
            id_assoc_statement_address+=" address "+ address+Nlifetime
            if Nvalid_time.isdigit() or Nvalid_time == 'infinity':
                id_assoc_statement_address+=Nvalid_time
            id_assoc_statement_address+=";\n"
        id_assoc_statement_address+="};\n"
    
    id_assoc_statement_prefix=""
    if prefix_delegation:
        id_assoc_statement_prefix = "id-assoc pd "
        if id_assoc_pd.isdigit():
            id_assoc_statement_prefix += id_assoc_pd
        else:
            id_assoc_statement_prefix += id_assoc_pd
        id_assoc_statement_prefix += "{\n"
        if IPv6_Prefix != '' and Plifetime.isdigit() and Plifetime == 'infinity':
            id_assoc_statement_prefix += " prefix " + IPv6_Prefix + Plifetime
            if Pvalid_time.isdigit() or Pvalid_time == 'infinity':
                id_assoc_statement_prefix+=Pvalid_time
            id_assoc_statement_prefix+=";\n"
        id_assoc_statement_prefix  += "};\n"
    authentication_statement = ""
    if authname!='' and  protocol=="delayed":
        authentication_statement+="authentication {} {\n".format(authname)
        authentication_statement+= " protocol {};\n".format(protocol)
        if re.search(r'(hmac(-)?md5|HMAC(-)?MD5)',algorithm):
           authentication_statement+= " algorithm {};\n".format(algorithm)
        if rdm=="monocounter":
            authentication_statement+" rdm {};\n".format(rdm)
        authentication_statement+="};\n"    
    
    key_info_statement=""
   
    if keyname!='' and royaume!='' and keyid.isdigit() and secret!='':
        key_info_statement += "keyinfo {} {\n".format(keyname)
        key_info_statement += "  realm \"{}\";\n".format(royaume)
        key_info_statement += "  keyid {};\n".format(keyid)
        key_info_statement += "  secret \"{}\";\n".format(secret)
        # The regular expression pattern
        pattern = r"((([0-9]{4}-)?[0-9]{2}[0-9]{2} )?[0-9]{2}:[0-9]{2})|forever"
        if re.match(pattern, expire):
            key_info_statement += "  expire \"{}\";\n".format(expire)
        
        key_info_statement += "};\n"
    
    configContenu += id_assoc_statement_address
    configContenu += id_assoc_statement_prefix
    configContenu += authentication_statement
    configContenu += key_info_statement

    return configContenu

####create file
def create_file_ipv6(ifname,config_contenu):
    #commandes pour créer un dossier et stocker le contenu dans dhclient.conf
    commands = ["""bash -c 'sudo mkdir -p /etc/Dhcp6Config/{} && sudo cat <<EOF > /etc/Dhcp6Config/{}/dhcp6c.conf
{}
EOF'""".format(ifname, ifname, '\n'.join(config_contenu))]
    return commands

# convert  to dhcp  connexion base and advanced
def update_conn_dhcp_ipv6(config,ifname):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP6Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 dhcp
    commandes=[
     "#Start IP6Config {}".format(ifname),   
     "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
    "ExecStart=/usr/bin/dhcp6c -c /etc/Dhcp6Config/{}/dhcp6c.conf {}".format(ifname),
     "#End IP6Config {}".format(ifname)
    ]
    cmd_final=[
    "sudo ip addr flush dev {}".format(ifname),
    "sudo dhcp6c -c /etc/Dhcp6Config/{}/dhcp6c.conf {}".format(ifname),
    ]
    
    return commandes,config,cmd_final
