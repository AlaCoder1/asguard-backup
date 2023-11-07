import re
from .functions import *

#############################################ipv6#############################################

##static ipv6
# convert  to static connexion  ipv6 
def update_conn_static_IPV6(config,ifname,uuid,ip_address6,netmask6,cmdgw):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP6Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 static
    commands=[]
    cmd_final=[]
    if ip_address6 is not None and netmask6 is not None:
        cmd_final.append("sudo nmcli connection modify {} ipv6.method manual ipv6.addresses {}/{}".format(uuid,ip_address6,netmask6))
    cmd_final+=[ 
         cmdgw,      
       ]
    
    return commands,config,cmd_final
##dhcp ipv6
###############
###return base config
def return_config_base_ipv6(ifname,id,Request_only,prefix_delegation_size,prefix_hint,ipv4_connectivity,vlan_priority):
    #contenu de fichier dhclient.conf "config base"
    configContenu=["interface "+ ifname+" {",]
    if Request_only==False:
        configContenu.append("  send ia-na {}; # request stateful address".format(id))
    configContenu += ["  request domain-name-servers;", 
                      "  request domain-name;",
                          "};"]   
    if Request_only==False:
        configContenu.append("id-assoc na " +str(id)+" { };")
    if prefix_delegation_size is not None:
        # Setup the prefix delegation 
            configContenu.append("id-assoc pd "+str(id)+ " {")
            if  prefix_hint is True:
                preflen = 64 - prefix_delegation_size
                configContenu.append("  prefix ::/"+str(preflen)+" infinity; \n ")
    configContenu.append("};")                    
    return configContenu

###return advanced config
def return_config_advanced_ipv6(ifname,
id,IPv4_connectivity,VLAN_priority,information_only,
send_options,request_options,script,non_temporary,id_assoc,address,nlifetime,nvalid_time,
prefix_delegation,id_assoc_pd,ipv6_prefix,plifetime,pvalid_time,
authname,protocol,algorithm,
rdm,keyname,royaume,keyid,secret,expire):
    #contenu de fichier dhcp6c.conf "config advanced"
 ####### 
    sendOptionString=""
    regex_pattern = r'\s*,\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    #chaine de caractères chaque option séparé par ,
    options = re.split(regex_pattern,send_options)
    for opt in options:
        sendOptionString+=" send {};\n".format(opt)
 ####### 
    requestOptionString=""
    regex_pattern = r'\s*,\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'
    #chaine de caractères chaque option séparé par ,
    
    options = re.split(regex_pattern,request_options)
    for opt in options:
        requestOptionString+=" request {};\n".format(opt) 
 ####### 
    informationOnlyString=""    
    if information_only==True:
       informationOnlyString+=" information-only;\n"
 ####### 
    script_final = "  script \"/var/etc/dhcp6c_{}_script.sh\";\n;".format(ifname)
    if script is not None: 
        script_final = "  script {};\n".format(script)
    
 
    configContenu=["interface "+ifname+ " {\n",
                   sendOptionString,
                   requestOptionString,
                   informationOnlyString,
                   script_final,
                   "};"
                   ]
    id_assoc_statement_address=""
    if non_temporary is True:
        id_assoc_statement_address += "id-assoc na "
        if  id_assoc.isdigit():
            id_assoc_statement_address +=str(id_assoc)
        else:
            id_assoc_statement_address+=str(id)
        id_assoc_statement_address+=" {\n"
        if address is not None and nlifetime.isdigit() or nlifetime == 'infinity':
            id_assoc_statement_address+=" address "+ address+" " +nlifetime
            if nvalid_time.isdigit() or nvalid_time == 'infinity':
                id_assoc_statement_address+=" "+nvalid_time
            id_assoc_statement_address+=";\n"
        id_assoc_statement_address+="};\n"
    
    id_assoc_statement_prefix=""
    if prefix_delegation is True:
        id_assoc_statement_prefix = "id-assoc pd "
        if id_assoc_pd.isdigit():
            id_assoc_statement_prefix += id_assoc_pd
        else:
            id_assoc_statement_prefix += id_assoc_pd
        id_assoc_statement_prefix += " {\n"
        if ipv6_prefix is not None and plifetime.isdigit() or plifetime == 'infinity':
            id_assoc_statement_prefix += " prefix " + ipv6_prefix +" "+ plifetime
            if pvalid_time.isdigit() or pvalid_time == 'infinity':
                id_assoc_statement_prefix+=" "+pvalid_time
            id_assoc_statement_prefix+=";\n"
        id_assoc_statement_prefix  += "};\n"
    authentication_statement = ""
    if authname is not None and protocol=="delayed" :
        authentication_statement+="authentication "+authname+" {\n"
        authentication_statement+= " protocol {};\n".format(protocol)
        if re.search(r'(hmac(-)?md5|HMAC(-)?MD5)',algorithm):
           authentication_statement+= " algorithm {};\n".format(algorithm)
        if rdm=="monocounter":
            authentication_statement+" rdm {};\n".format(rdm)
        authentication_statement+="};\n"    
    
    key_info_statement=""
   
    if keyname is not None and royaume is not None and keyid.isdigit() and secret is not None:
        key_info_statement += "keyinfo "+keyname+" {\n"
        key_info_statement += "  realm \"{}\";\n".format(royaume)
        key_info_statement += "  keyid {};\n".format(keyid)
        key_info_statement += "  secret \"{}\";\n".format(secret)
        # The regular expression pattern
        pattern = r"((([0-9]{4}-)?[0-9]{2}[0-9]{2} )?[0-9]{2}:[0-9]{2})|forever"
        if re.match(pattern, expire):
            key_info_statement += "  expire \"{}\";\n".format(expire)
        
        key_info_statement += "};\n"
    
    configContenu += [id_assoc_statement_address,
     id_assoc_statement_prefix,
     authentication_statement,
     key_info_statement]
    return configContenu

####create file
def create_file_ipv6(ifname,config_contenu):
    #commandes pour créer un dossier et stocker le contenu dans dhclient.conf
    commands = ["""bash -c 'sudo mkdir -p /etc/Dhcp6Config/{} && sudo cat <<EOF > /etc/Dhcp6Config/{}/dhcp6c.conf
{}
EOF'""".format(ifname, ifname, '\n'.join(config_contenu)),
"sudo mkdir -p /var/run/{}".format(ifname)
]
    return commands
# convert  to dhcp  connexion base and advanced
def update_conn_dhcp_ipv6(config,ifname,uuid):
    #lancer la fonction de "remove old config"
    config=clean_old_config(config,"IP6Config {}".format(ifname))
    #la liste des commandes pour l'IPV4 dhcp
    commandes=[
    #  "#Start IP6Config {}".format(ifname),   
    # "ExecStart=/usr/bin/(sudo dhcp6c -c /etc/Dhcp6Config/{}/dhcp6c.conf  -fp /var/run/dhcp6c.pid {}; kill -s SIGTERM $(cat /var/run/dhcp6c.pid))&".format(ifname,ifname),

    #  "#End IP6Config {}".format(ifname)
    ]
    cmd_final=[
    "sudo nmcli connection modify {} ipv6.method auto ipv6.addresses '' ipv6.gateway '' ipv6.route-metric '' ".format(uuid),
    "sudo systemctl enable --quiet dhcp6c@{} && sudo systemctl restart --quiet dhcp6c@{}".format(ifname,ifname),
    # "(sudo dhcp6c -c /etc/Dhcp6Config/{}/dhcp6c.conf  -fp /var/run/dhcp6c.pid {}; kill -s SIGTERM $(cat /var/run/dhcp6c.pid)) &".format(ifname,ifname),
    ]
    
    return commandes,config,cmd_final
