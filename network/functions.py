from .models import *
from authentification.views import *
from network.address import *
####background task to execute it 
from background_task import background
from django.conf import settings
import subprocess
###############################################################
####update in Database functions
#function to update config tables
def update_DB(id,data,model,IP4serializer):
    data['interface']=id
    if model.objects.filter(interface_id=id).exists():
        objectConfig=model.objects.get(interface_id=id)
        # Set all attributes to None
        for field in objectConfig._meta.fields:
            if field.attname not in ["id", "interface_id",'ifname','created_at','updated_at','created_by','updated_by']: 
                setattr(objectConfig, field.attname, None)
        setattr(objectConfig, 'updated_by', settings.CurrentUserId)
        serializerIP4Config = IP4serializer(objectConfig,data=data)
        print(data)
    else:
        serializerIP4Config = IP4serializer(data=data)
    print(serializerIP4Config.is_valid())
    if (serializerIP4Config.is_valid()):
        serializerIP4Config.save()

#function to update interface tables  
def update_interface_table(id,data,InterfaceSerializer):
    objectConfig=Interface.objects.get(id=id)
    # Set all attributes to None
    for field in objectConfig._meta.fields:
        if field.attname not in ["id",'ifname','created_at','updated_at']: 
            setattr(objectConfig, field.attname, None)
    serializerInterface= InterfaceSerializer(objectConfig,data=data)
    if serializerInterface.is_valid():
            serializerInterface.save()      
############################################################
@background
def your_background_task(commands):
    # Code to execute in the background
    ssh_conx = paramiko.SSHClient()
    ssh_conx.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # connect to SSH server
    ssh_conx.connect("10.1.12.74", username="root",
                password="root", port="22")
    # username=settings.CurrentUserId
    print({"heniiiiiiiiiiiiii":settings.USERNAME})
    # print({"HOST":settings.SSH_HOST,"username":settings.USERNAME,"password":settings.PASSWORD})
    # ssh.connect(settings.SSH_HOST, username=settings.USERNAME,
    #                         password=settings.PASSWORD)
    for cmd in commands:
        stdin, stdout, stderr = ssh_conx.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')
        if error:
            print("error ",error,"    :",cmd)
            # break
        else:
            print("service created successufully!!",cmd)
    ssh_conx.close()    
###################    
##get old configuration in service
def get_old_config():
        cmd = """python -c "
with open('/etc/systemd/system/Asguard-Networking.service', 'r') as file:
    for line in file:
        print(line)
        " """
        ssh.exec_command(cmd)
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')
        return output,error
###################    
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
 

################### Static      
# convert  to static connexion 
def update_conn_static(config,ifname,ip_address,netmask):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP4Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 static
    commands=[
         "#Start IP4Config {}".format(ifname),
        "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
        "ExecStart=/usr/bin/ip addr add {}/{} dev {}".format(ip_address,netmask,ifname),
         "#End IP4Config {}".format(ifname)
    ]
    
    return commands,config

################### Dhcp
###return base config
def return_config_base(ifname,reject,hostname,alias_add,alias_mask):
    #contenu de fichier dhclient.conf "config base"
    configContenu=[
        'reject {};'.format(reject),
        'interface "{}"'.format(ifname),
            '{',
        'send host-name "{}";'.format(hostname),
        '}',
        'alias {',
        'interface "{}";'.format(ifname),
        'fixed-address {};'.format(alias_add),
        'option subnet-mask {};'.format(alias_mask),
        '}',
                        ]
    return configContenu

###return advanced config
def return_config_advanced(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domaine_name,domain_server,lease_time,request,require):
    #contenu de fichier dhclient.conf "config advanced"
    configContenu=[
        'timeout {};'.format(timeout),
        'retry {};'.format(retry),
        'reboot {};'.format(reboot),
        'backoff-cutoff {};'.format(backoff),
        'select-timeout {};'.format(select_timeout),
        'initial-interval {};'.format(initial_interval),
            'reject {};'.format(reject),
            'interface "{}"'.format(ifname),
                '{',
        'send host-name "{}";'.format(hostname),
        'send dhcp-client-identifier {};'.format(dhcp_client),
        'supersede domain-name "{}";'.format(domaine_name),
        'prepend domain-name-servers {};'.format(domain_server),
        'send dhcp-lease-time {};'.format(lease_time),
        ' request {};'.format(request),
            'require {};'.format(require),
            '}',
        'alias {',
        'interface "{}";'.format(ifname),
        'fixed-address {};'.format(alias_add),
        'option subnet-mask {};'.format(alias_mask),
        '}'
                                        ]
    return configContenu

####create file
def create_file(ifname,config_contenu):
    #commandes pour créer un dossier et stocker le contenu dans dhclient.conf
    commands = ["""bash -c 'sudo mkdir -p /etc/Dhcp4Config/{} && sudo cat <<EOF > /etc/Dhcp4Config/{}/dhclient.conf
{}
EOF'""".format(ifname, ifname, '\n'.join(config_contenu))]
    return commands

# convert  to dhcp  connexion base and advanced
def update_conn_dhcp(config,ifname):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP4Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 dhcp
    commandes=[
     "#Start IP4Config {}".format(ifname),   
     "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
    "ExecStart=/usr/bin/dhclient -4 -v -cf  /etc/Dhcp4Config/{}/dhclient.conf {}".format(ifname,ifname),
     "#End IP4Config {}".format(ifname)
    ]
    
    return commandes,config


###################generic configuration

def generic_config(config,ifname,speed_duplex,addmac,mtuV,mssV):
    commandes=[]
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
    if addmac is not None:
            #lancer la fonction de "remove old config"
            config=clean_old_config(config,"addmac config {}".format(ifname))
             #la liste des commandes pour l'address mac
            commandes+=[
            "#Start addmac config {}".format(ifname),
            'ExecStart=/usr/bin/ip link set dev {} address {}'.format(ifname,addmac),
            "#End addmac config {}".format(ifname)
            ]
    #tester si mtu is not None
    if mtuV is not None:
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"mtu config {}".format(ifname))
        #la liste des commandes pour mtu
        commandes+=[
        "#Start mtu config {}".format(ifname),
        'ExecStart=/usr/bin/ip link set dev {} mtu {}'.format(ifname,mtuV),
        "#End mtu config {}".format(ifname)
            ]
    #tester si mtu is not None
    if mssV is not None:
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"mss config {}".format(ifname))
         #la liste des commandes pour mss
        commandes+=[
        "#Start mss config {}".format(ifname),
        'ExecStart=/usr/bin/iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -o {} -j TCPMSS --set-mss {}'.format(ifname,mssV),
        "#End mss config {}".format(ifname),
            ]
    #tester si speed_duplex is not None
    if speed_duplex is not None:
        #lancer la fonction de "remove old config"
        config=clean_old_config(config,"speed duplex config {}".format(ifname))
        #la liste des commandes pour speed duplex
        commandes+=[
        "#Start speed duplex config {}".format(ifname),
        'ExecStart=/usr/bin/ethtool -s {} speed {} duplex {}'.format(ifname,speedV,duplexV),
        "#End speed duplex config {}".format(ifname),
                    ]
    return commandes,config

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
        """bash -c 'sudo mkdir -p /etc/nftables/{} && cat <<EOF > /etc/nftables/{}/nftables.conf
{}
EOF' """.format(ifname, ifname, '\n'.join(rules))
      ]
    return commands

###Function to block private or bogons address
def block_address_commandes(config,ifname,bogon_aux,private_aux):
    rule=''
    commandes=[]
    configuration=[]
    #tester si on bloque les addresses bogons ou private
    if bogon_aux or private_aux:
        #tester si on bloque les addresses bogons and private
        if bogon_aux and private_aux:
            #rules pour les adresses ipv4
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(bogon_address_ip4))
            #rules pour les adresses ipv6
            rule+='\n iifname {} ip6 saddr {}'.format(ifname,create_rule(bogon_address_ip6))    
        #tester si on bloque les addresses bogons seulement
        elif bogon_aux and not private_aux:
            #rules pour les adresses ipv4
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(bogon_address_ip4))
            #rules pour les adresses ipv6
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
            'ExecStart=/usr/bin/nft -f /etc/nftables/{}/nftables.conf'.format(ifname),
            "#End nftables config {}".format(ifname)
            ]
    else:
        #call function to clean old config
       config=clean_old_config(config,"nftables config {}".format(ifname))
    
   
    
    return configuration,commandes,config
