import re

from backend.gateway.functions import add_gateway_interface_db, different_metric, get_gateway_dhcp, return_gateway6_system, save_gateways_database
from backend.network.functions_ipv4 import get_address_dhcp
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



def save_address_dhcp_ip6(setuptype_ip4,setuptype_ip6,ifname,name_interface,json_ipv6):
    aux_gw6_dhcp=True
    if setuptype_ip4 is None or setuptype_ip4.lower()=="static" :
            aux_gw6_dhcp=True
    if setuptype_ip6 is not None and setuptype_ip6.lower()=="dhcp":
        #function to get dhcp address6 and mask6
        ip_address6,netmask6=get_address_dhcp(ifname,"6")
        json_ipv6["ip_address6"]=ip_address6
        json_ipv6["netmask6"]=netmask6
        ###
        ##function to get gateway if typeIPV6 est DHCP Base or Advanced
        gwaddr6,metric6,default_aux6,far_aux6,multiwan_aux6=get_gateway_dhcp(ifname,"6")
        aux_gw6_dhcp=save_gateways_database(gwaddr6,name_interface,default_aux6,far_aux6,multiwan_aux6,metric6,False,False)
    return aux_gw6_dhcp,json_ipv6

def configuration_ipv6(commandes_final,data,setuptype_ip6,Gateway,GatewayInterface,list_metric,ifname,name_interface,uuid,id_interface):
     match setuptype_ip6.lower():
        case "none":
            pass
        case "static"  :
            typeDHCP6=''
            ip_address6 =  None if data['value_setup_Ipv6'].get('ip_address6', None) == "" else  data['value_setup_Ipv6'].get('ip_address6', None)
            netmask6 =  None if data['value_setup_Ipv6'].get('netmask6', None) == "" else  data['value_setup_Ipv6'].get('netmask6', None)
            gateway6 =  None if data['value_setup_Ipv6']['gateway6'].get('value', None) == "" else  data['value_setup_Ipv6']['gateway6'].get('value', None)
            GatewayObject6=Gateway.objects.get(Q(gwaddress=gateway6) & Q(staticgw=True) )
            #call function to convert address to static ipv6
            #################
            default_aux6=GatewayObject6.default_aux
            far_aux6=GatewayObject6.far_aux
            multiWan_aux6=GatewayObject6.multiwan_aux
            addrgw6=GatewayObject6.gwaddress
            ############# generete metric statiquement
            metric=0
            allGatewayInterface = GatewayInterface.objects.all()
            if multiWan_aux6:
                for i in allGatewayInterface:
                    list_metric.append(i.metric)
                metric=different_metric(list_metric)
            cmdgw6=return_gateway6_system(uuid,addrgw6,far_aux6,multiWan_aux6,metric)
            ipv4_gw_interface=False
            add_gateway_interface_db(GatewayObject6,name_interface,metric,ipv4_gw_interface)
            #call function to convert address to static
            commandes,output_service,cmd_final_ipv6=update_conn_static_IPV6(output_service,ifname,uuid,ip_address6,netmask6,cmdgw6)
            jsonIPV6={
            "name_interface":name_interface,"ifname":ifname,
            "ip_address6":ip_address6,"netmask6":netmask6,
            "typeip6":setuptype_ip6}
        case "dhcp" :
            typeDHCP6 = data.get('value_setup_Ipv6')['typeDHCP6']
            #Base and Advanced
            ipv4_connectivity =  None if data['value_setup_Ipv6'].get('ipv4_connectivity', None) == "" else  data['value_setup_Ipv6'].get('ipv4_connectivity', None)
            vlan_priority =  None if data['value_setup_Ipv6'].get('vlan_priority', None) == "" else  data['value_setup_Ipv6'].get('vlan_priority', None)
            if typeDHCP6.lower()=="base" :
                ###Base
                request_only =  None if data['value_setup_Ipv6'].get('request_only', None) == "" else  data['value_setup_Ipv6'].get('request_only', None)
                prefix_delegation_size =  None if data['value_setup_Ipv6'].get('prefix_delegation_size', None) == "" else  data['value_setup_Ipv6'].get('prefix_delegation_size', None)
                prefix_hint =  None if data['value_setup_Ipv6'].get('prefix_hint', None) == "" else  data['value_setup_Ipv6'].get('prefix_hint', None)
            #contenu de dhclient.conf dhcp Base
                config_contenu_ipv6=return_config_base_ipv6(ifname,id_interface,request_only,prefix_delegation_size,prefix_hint,ipv4_connectivity,vlan_priority)
                jsonIPV6={
                    "typeip6":setuptype_ip6,"typedhcp6":typeDHCP6,
                    "request_only":request_only,"prefix_delegation_size":prefix_delegation_size,
                    "prefix_hint":prefix_hint,"ipv4_connectivity":ipv4_connectivity,
                    "vlan_priority":vlan_priority
                    }
            if typeDHCP6.lower()=="advanced":
                ###Advanced
                #interface status
                information_only =  None if data['value_setup_Ipv6'].get('information_only', None) == "" else  data['value_setup_Ipv6'].get('information_only', None)
                send_options =  None if data['value_setup_Ipv6'].get('send_options', None) == "" else  data['value_setup_Ipv6'].get('send_options', None)
                request_options =  None if data['value_setup_Ipv6'].get('request_options', None) == "" else  data['value_setup_Ipv6'].get('request_options', None)
                script =  None if data['value_setup_Ipv6'].get('script', None) == "" else  data['value_setup_Ipv6'].get('script', None)
                #####
                non_temporary =  None if data['value_setup_Ipv6'].get('non_temporary', None) == "" else  data['value_setup_Ipv6'].get('non_temporary', None)
                #### if non_temporary is true
                id_assoc =  None if data['value_setup_Ipv6'].get('id_assoc', None) == "" else  data['value_setup_Ipv6'].get('id_assoc', None)
                address =  None if data['value_setup_Ipv6'].get('address', None) == "" else  data['value_setup_Ipv6'].get('address', None)
                nlifetime =  None if data['value_setup_Ipv6'].get('nlifetime', None) == "" else  data['value_setup_Ipv6'].get('nlifetime', None)
                nvalid_time =  None if data['value_setup_Ipv6'].get('nvalid_time', None) == "" else  data['value_setup_Ipv6'].get('nvalid_time', None)
                #####
                prefix_delegation =  None if data['value_setup_Ipv6'].get('prefix_delegation', None) == "" else  data['value_setup_Ipv6'].get('prefix_delegation', None)
                #### if prefix_delegation is true
                id_assoc_pd =  None if data['value_setup_Ipv6'].get('id_assoc_pd', None) == "" else  data['value_setup_Ipv6'].get('id_assoc_pd', None)
                ipv6_prefix =  None if data['value_setup_Ipv6'].get('ipv6_prefix', None) == "" else  data['value_setup_Ipv6'].get('ipv6_prefix', None)
                plifetime =  None if data['value_setup_Ipv6'].get('plifetime', None) == "" else  data['value_setup_Ipv6'].get('plifetime', None)
                pvalid_time =  None if data['value_setup_Ipv6'].get('pvalid_time', None) == "" else  data['value_setup_Ipv6'].get('pvalid_time', None)
                ##auth
                authname =  None if data['value_setup_Ipv6'].get('authname', None) == "" else  data['value_setup_Ipv6'].get('authname', None)
                protocol =  None if data['value_setup_Ipv6'].get('protocol', None) == "" else  data['value_setup_Ipv6'].get('protocol', None)
                algorithm =  None if data['value_setup_Ipv6'].get('algorithm', None) == "" else  data['value_setup_Ipv6'].get('algorithm', None)
                rdm =  None if data['value_setup_Ipv6'].get('rdm', None) == "" else  data['value_setup_Ipv6'].get('rdm', None)
                ##key info
                keyname =  None if data['value_setup_Ipv6'].get('keyname', None) == "" else  data['value_setup_Ipv6'].get('keyname', None)
                royaume =  None if data['value_setup_Ipv6'].get('royaume', None) == "" else  data['value_setup_Ipv6'].get('royaume', None)
                keyid =  None if data['value_setup_Ipv6'].get('keyid', None) == "" else  data['value_setup_Ipv6'].get('keyid', None)
                secret =  None if data['value_setup_Ipv6'].get('secret', None) == "" else  data['value_setup_Ipv6'].get('secret', None)
                expire =  None if data['value_setup_Ipv6'].get('expire', None) == "" else  data['value_setup_Ipv6'].get('expire', None)
                ##
                ##contenu de dhcp6c.conf dhcp advanced
                config_contenu_ipv6=return_config_advanced_ipv6(ifname,
                id_interface,ipv4_connectivity,vlan_priority,information_only,
                send_options,request_options,script,non_temporary,id_assoc,address,nlifetime,nvalid_time,
                prefix_delegation,id_assoc_pd,ipv6_prefix,plifetime,pvalid_time,
                authname,protocol,algorithm,rdm,keyname,royaume,keyid,secret,expire)
                jsonIPV6={
                "typeip6":setuptype_ip6,"typedhcp6":typeDHCP6,
                "information_only":information_only,"send_options":send_options,
                "request_options":request_options,"script":script,
                "non_temporary":non_temporary,"id_assoc":id_assoc,
                "address":address,"nlifetime":nlifetime,"nvalid_time":nvalid_time,
                "prefix_delegation":prefix_delegation,
                "id_assoc_pd":id_assoc_pd,"ipv6_prefix":ipv6_prefix,"plifetime":plifetime,
                "pvalid_time":pvalid_time,"authname":authname,"protocol":protocol,
                "algorithm":algorithm,"rdm":rdm,"keyname":keyname,"royaume":royaume,
                "keyid":keyid,"secret":secret,"expire":expire,
                "ipv4_connectivity":ipv4_connectivity,"vlan_priority":vlan_priority
                    }
            #add commands of create file dhclient to list of commandes to execute    
            commandes_final+=create_file_ipv6(ifname,config_contenu_ipv6)
            #call function to convert address to dhcp advanced /Base  in service
            commandes_ipv6,output_service,cmd_final_ipv6=update_conn_dhcp_ipv6(output_service,ifname,uuid)