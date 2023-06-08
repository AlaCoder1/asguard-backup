from django.http import JsonResponse
from .models import *
from settings.serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
from authentification.views import *
from network.address import *
# API to update connexion using ssh and netlink
# API to update connexion to static


###################
##clean old config
def clean_old_config(config,typeConf):
    if "#Start {}".format(typeConf) in config and "#End {}".format(typeConf) in config: 
        i=config.index("#Start {}".format(typeConf))
        j=config.index("#End {}".format(typeConf))
        config=config[:i]+config[j+1:]
    return config
 

################### Static      
# convert  to static connexion 
def update_conn_static(config,ifname,ip_address,netmask,gateway):
    config=clean_old_config(config,"IP4Config {}".format(ifname))
    commands=[
         "#Start IP4Config {}".format(ifname),
        "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
        "ExecStart=/usr/bin/ip addr add {}/{} dev {}".format(ip_address,netmask,ifname),
         "#End IP4Config {}".format(ifname)
    ]
    
    return commands,config

################### Dhcp
####create file
def create_file(ifname,config_contenu):
    commands = ["""bash -c 'mkdir -p /etc/Dhcp4Config/{} && cat <<EOF > /etc/Dhcp4Config/{}/dhclient.conf
{}
EOF'""".format(ifname, ifname, '\n'.join(config_contenu))]
    return commands

# convert  to dhcp  connexion base and advanced
def update_conn_dhcp(config,ifname):
    config=clean_old_config(config,"IP4Config {}".format(ifname))
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
   
    if addmac is not None:
            config=clean_old_config(config,"addmac config {}".format(ifname))
            commandes+=[
            "#Start addmac config {}".format(ifname),
            'ExecStart=/usr/bin/ip link set dev {} address {}'.format(ifname,addmac),
            "#End addmac config {}".format(ifname)
            ]
    if mtuV is not None:
        config=clean_old_config(config,"mtu config {}".format(ifname))
        commandes+=[
        "#Start mtu config {}".format(ifname),
        'ExecStart=/usr/bin/ip link set dev {} mtu {}'.format(ifname,mtuV),
        "#End mtu config {}".format(ifname)
            ]
    if mssV is not None:
        config=clean_old_config(config,"mss config {}".format(ifname))
        commandes+=[
        "#Start mss config {}".format(ifname),
        'ExecStart=/usr/bin/iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -o {} -j TCPMSS --set-mss {}'.format(ifname,mssV),
        "#End mss config {}".format(ifname),
            ]
    if speed_duplex is not None:
        config=clean_old_config(config,"speed duplex config {}".format(ifname))
        commandes+=[
        "#Start speed duplex config {}".format(ifname),
        'ExecStart=/usr/bin/ethtool -s {} speed {} duplex {}'.format(ifname,speedV,duplexV),
        "#End speed duplex config {}".format(ifname),
                    ]
    return commandes,config

#################Blockage address
####add all addresse 
def create_rule(address):
    block=''
    for i in range(len(address)-1):
        block+=address[i]+','
    block+=address[-1]
    block='{ '+block+' } drop'
    return block


####create file
def create_file_nftables(ifname,rules):
    commands = [
        'if nft list tables | grep -q "filter_{}"; then sudo nft delete table inet filter_{} ; fi'.format(ifname,ifname),
        """bash -c 'mkdir -p /etc/nftables/{} && cat <<EOF > /etc/nftables/{}/nftables.conf
{}
EOF' """.format(ifname, ifname, '\n'.join(rules))
      ]
    return commands

###Function to block private or bogons address
def block_address_commandes(config,ifname,bogon_aux,private_aux):
    rule=''
    commandes=[]
    configuration=[]
    if bogon_aux or private_aux:
        if bogon_aux and private_aux:
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(bogon_address_ip4))
            rule+='\n iifname {} ip6 saddr {}'.format(ifname,create_rule(bogon_address_ip6))    
        elif bogon_aux and not private_aux:
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(bogon_address_ip4))
            rule+='\n iifname {} ip6 saddr {}'.format(ifname,create_rule(bogon_address_ip6))
            
        elif private_aux and not bogon_aux:
            rule='iifname {} ip saddr {}'.format(ifname,create_rule(private_address))
            
        rules=[
            'table inet filter_'+ifname+' {',
                    'chain input {',
                            'type filter hook input priority filter; policy accept;',
                            '{}'.format(rule),
            '        }',
            '}'
        ]  
        configuration=create_file_nftables(ifname,rules)
        commandes=[
            "#Start nftables config {}".format(ifname),
            'ExecStart=/usr/bin/nft -f /etc/nftables/{}/nftables.conf'.format(ifname),
            "#End nftables config {}".format(ifname)
            ]
    else:
       config=clean_old_config(config,"nftables config {}".format(ifname))
    
   
    
    return configuration,commandes,config






@api_view(['POST'])
@permission_classes([AllowAny])

def conf(request):
    ifname='eth1'
    msg = ""
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # BPN = data['BPN']
        # BBN = data['BBN']
        ##static
        ip_address = data['ip_address']
        netmask=data['netmask']
        gateway= data['gateway']
        ##DHCP
        timeout=data['timeout']
        retry=data['retry']
        reboot=data['reboot']
        backoff=data['backoff']
        select_timeout=data['select_timeout']
        initial_interval=data['initial_interval']
        reject=data['reject']
        ####
        hostname=data['hostname']
        dhcp_client=data['dhcp_client']
        domaine_name='fugue.comrc.vix.comhome.vix.com'
        domain_server=data['domain_server']
        lease_time=data['lease_time']
        request='subnet-mask, broadcast-address, time-offset, routers,domain-name, domain-name-servers, host-name'
        require='subnet-mask , domain-name-servers'
        alias_add=data['alias_add']
        alias_mask=data['alias_mask']

        ###generic config
        mtuV=data.get('mtuV', None)
        addmac=data.get('addmac', None)
        mssV=data.get('mssV', None)
        speed_duplex=None
        ####
        IP4Config=data['IP4Config']
        typeDhcp=data['typeDhcp']
        ##blockage addresse
        bogon_aux=data['bogon_aux']
        private_aux=data['private_aux']
        commandes=[]
        commandes_final=[]
        print({'bbbbbb':"commandes_final"})
        ##get old configuration in service
        cmd = """python -c "
with open('/etc/systemd/system/Asguard-Networking.service', 'r') as file:
    for line in file:
        print(line)
        " """
        ssh.exec_command(cmd)
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')
        if error:
            print("error ",error,"  :",cmd)
        else:
            if len(output)!=0:
                output = [x for x in output if x]
                index=output.index('[Service]')
                ##add requirement service
                values_to_add=['BindsTo=sys-subsystem-net-devices-{}.device'.format(ifname),
                            'After=sys-subsystem-net-devices-{}.device'.format(ifname)]
                values_to_add = [x for x in values_to_add if x not in output]
                output = output[:index] + values_to_add + output[index:]
                ##IPV4 configuration cases 
                match IP4Config:
                    case "None":
                        pass
                    case "static":
                        commandes,output=update_conn_static(output,ifname,ip_address,netmask,gateway)
                    case "dhcp":
                        if typeDhcp=="Base" :
                            configContenu=['reject {};'.format(reject),
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
                        if typeDhcp=="Advanced":
                            configContenu=['timeout {};'.format(timeout),
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
                        commandes_final+=create_file(ifname,configContenu)
                        commandes,output=update_conn_dhcp(output,ifname)
                ##for generic config 
                cmds=[]       
                cmds,output=generic_config(output,ifname,speed_duplex,addmac,mtuV,mssV)
                ##blocages des adresses
                cmdsBlock=[]
                configs=[]
            
                configs,cmdsBlock,output=block_address_commandes(output,ifname,bogon_aux,private_aux)
                cmdsBlock = [x for x in cmdsBlock if x not in output]
                ###add all commandes to the service
                index_cmd=output.index('[Install]') 
                commandes+=cmds+cmdsBlock
                output = output[:index_cmd] + commandes + output[index_cmd:]
            ####
                commandes_final +=configs+[
                """cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output)),
                    'sudo systemctl daemon-reload',
                    # 'sudo systemctl disable Asguard-Networking.service',
                    # 'sudo systemctl enable Asguard-Networking.service',
                    'sudo systemctl restart Asguard-Networking.service',
                ]
                print({"trah":commandes_final})
    # print({'aaaa':commandes_final})
    for cmd in commandes_final:
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')

        if error:
            print("error ",error,"    :",cmd)
            # break
        else:
            print("service created successufully!!",cmd)
    return JsonResponse({"commandes_finals:": commandes_final})
