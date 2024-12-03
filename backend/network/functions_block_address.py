from .address import *
from  .functions import *

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
        f'sudo bash -c "if nft list tables | grep -q \'filter_{ifname}\'; then nft delete table inet filter_{ifname}; fi"',
        #cmd ajouter un dossier contenant le fichier config
        """sudo bash -c 'mkdir -p /etc/rulesNetwork/{} && sudo cat <<EOF > /etc/rulesNetwork/{}/nftables.conf
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
        if interfaceObject is not None and private_aux!=interfaceObject.private_aux or bogon_aux!=interfaceObject.bogon_aux:
            cmd_final+=[
                'sudo nft -f /etc/rulesNetwork/{}/nftables.conf'.format(ifname),
            ]
    else:

        #call function to clean old config
       config=clean_old_config(config,"nftables config {}".format(ifname))
    return configuration,commandes,config,cmd_final

