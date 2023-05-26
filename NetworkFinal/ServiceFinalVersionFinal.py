import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.178', username='root', password='rootroot')

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
    commands=[]
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
    ##list of private and bogon address 
    private_address= ['10.0.0.0/8',
                      '172.16.0.0/12','192.168.0.0/16',
                      '10.1.12.221','0.0.0.0']
    bogon_address_ip4=private_address+[
    '0.0.0.0/8','100.64.0.0/10', '127.0.0.0/8','127.0.53.53','169.254.0.0/16',
    '192.0.0.0/24','192.0.2.0/24','198.18.0.0/15', '198.51.100.0/24','203.0.113.0/24',
    '224.0.0.0/4','240.0.0.0/4','255.255.255.255/32']
    bogon_address_ip6=[
        '::/128','::1/128','::ffff:0:0/96',
    '::/96','100::/64','2001:10::/28','2001:db8::/32','fc00::/7','fe80::/10','fec0::/10',
    'ff00::/8','2002::/24','2002:a00::/24','2002:7f00::/24','2002:a9fe::/32','2002:ac10::/28',
    '2002:c000::/40','2002:c000:200::/40','2002:c0a8::/32','2002:c612::/31','2002:c633:6400::/40',
    '2002:cb00:7100::/40','2002:e000::/20','2002:f000::/20','2002:ffff:ffff::/48','2001::/40',
    '2001:0:a00::/40','2001:0:7f00::/40','2001:0:a9fe::/48','2001:0:ac10::/44','2001:0:c000::/56',
    '2001:0:c000:200::/56','2001:0:c0a8::/48','2001:0:c612::/47','2001:0:c633:6400::/56',
    '2001:0:cb00:7100::/56','2001:0:e000::/36','2001:0:f000::/36','2001:0:ffff:ffff::/64',
        ]
    
   
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




#################service config
###create service
def create_service(ifname,speed_duplex,addmac,mtuV,mssV,IP4Config,typeDhcp):
    commandes=[]
    commandes_final=[]
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
    'sudo systemctl disable Asguard-Networking.service',
    'sudo systemctl enable Asguard-Networking.service',
    'sudo systemctl restart Asguard-Networking.service']
    #cmd to block address
           
    return commandes_final
 
 
    
###test
ifname='eth1'
##static
ip_address = "10.1.12.169"
netmask=24
gateway= "10.1.12.1"
##DHCP
timeout=2
retry=60
reboot=10
backoff=10
select_timeout=5
initial_interval=2
reject='192.33.137.209'
####
hostname='andare.fugue.com'
dhcp_client='1:0:a0:24:ab:fb:9c'
domaine_name='fugue.comrc.vix.comhome.vix.com'
domain_server='127.0.0.1'
lease_time=3600
request='subnet-mask, broadcast-address, time-offset, routers,domain-name, domain-name-servers, host-name'
require='subnet-mask , domain-name-servers'
alias_add='192.5.5.120'
alias_mask='255.255.255.255'

###generic config
mtuV=None
addmac=None
mssV=None
# speed_duplex=None
speed_duplex='100baseTx-FD'
####
IP4Config="static"
typeDhcp="Base"
##blockage addresse
bogon_aux=False
private_aux=False

commandes_finals=create_service(ifname,speed_duplex,addmac,mtuV,mssV,IP4Config,typeDhcp)

print(commandes_finals)
for cmd in commandes_finals:
    stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
    error = stderr.read().decode('utf-8')
    output = stdout.read().decode('utf-8').split('\n')

    if error:
        print("error ",error,"    :",cmd)
        # break
    else:
        print("service created successufully!!",cmd)