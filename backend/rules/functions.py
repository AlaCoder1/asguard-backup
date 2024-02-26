import ipaddress
import subprocess
from backend.rules.serializers import *
from django.conf import settings
from backend.authentification.views import *
import socket

######function to run commande
def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error 
##function initial nftables.conf et /rules/ifname/nftables.conf
def init_file_nftables(ifname):
   #declare this line to be added in central  file nftables.conf
   include_rules='include "/etc/rules/{}/nftables.conf";'.format(ifname)
   #declare empty values of rules to initial secondary file /ifname/nftables.conf
   rules=""
   """
   -lancer ce script qui permet:
      1-verifier si le fichier secondaire  /ifname/nftables.conf exist ou non
      si le fichier n'exist pas :
         2-créer le dossier rules/ifname
         3-créer le fichier /ifname/nftables.conf
         4-créer la table de filtrage inet filter_ifname
         5-créer les chaines de filtrage (inbound,outbound,cellular,inbound cellular)
         6-ajouter include_rules contenu in central file /etc/nftables.conf
   """

   commandes=[ 'sudo mkdir -p /etc/rules/{}'.format(ifname),
              """sudo cat <<EOF >> /etc/rules/{}/nftables.conf
{} 
EOF""".format(ifname,rules),
"sudo nft add table inet filter_{} ".format(ifname),
"sudo nft add chain inet filter_{} inbound {{ type filter hook input priority 0 \; }}".format(ifname),
"sudo nft add chain inet filter_{} outbound {{ type filter hook output priority 0 \; }}".format(ifname),
"sudo nft add chain inet filter_{} cellular {{ type filter hook input priority 0 \; }}".format(ifname),
"sudo nft add chain inet filter_{} inbound_cellular {{ type filter hook input priority 0 \; }}".format(ifname),
'sudo nft list table inet filter_{} > /etc/rules/{}/nftables.conf'.format(ifname,ifname),
"grep -q '{}' /etc/nftables.conf || echo '{}' | sudo tee -a /etc/nftables.conf".format(include_rules,include_rules)
]

##executer le script créée précédamment retourner true si pas d'error sinon false en cas d'error
   for cmd in commandes:
      output,error=run_command(cmd)
      output = output.split('\n')
      if error !="":
         return error
   return True


###function to return rule  outbound
def return_rule(policy,saddr,daddr,sport,dport,protocol,type_rule):
   #initialiser une chaine vide
   rule=''
   #concatener tous les addresses à bloquer
   ##cas inbound
   if type_rule=='inbound' :
      if not protocol.upper()=="ALL":
         rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
      else:
         rule='ip saddr {} ip daddr {} {}'.format(saddr,daddr,policy)
         
    ##cas outbound
   elif type_rule=='outbound' :
      if not protocol.upper()=="ALL":
         rule='ip daddr {} ip saddr {} {} sport {} {} dport {} {}'.format(daddr,saddr,protocol,sport,protocol,dport,policy)
      else:
         rule='ip daddr {} ip saddr {} {}'.format(daddr,saddr,policy)
         
   #####cas saddr is None
   if saddr is None:
      rule=rule[:rule.find('ip saddr None')]+rule[rule.find('ip saddr None')+len(('ip saddr None'))+1:].strip()
   #####cas daddr is None
   if daddr is None:
      rule=rule[:rule.find('ip daddr None')]+rule[rule.find('ip daddr None')+len(('ip daddr None'))+1:].strip()
     ####### cas protocol icmp sans port
   if protocol.startswith("icmp type")  :
      rule=rule[:rule.find(protocol)+len(protocol)]+" "+rule[rule.find('{}'.format(policy)):]
   #####cas sport is None
   if sport is None and not protocol.startswith("icmp type") and protocol.upper()!="ALL" :
      rule=rule[:rule.find(('{} sport {}').format(protocol,sport))]+rule[rule.find(('{} sport {}').format(protocol,sport))+len(('{} sport {}').format(protocol,sport)):].strip()
   #####cas dport is None
   if dport is None and not protocol.startswith("icmp type") and protocol.upper()!="ALL":
      rule=rule[:rule.find(('{} dport {}').format(protocol,dport))]+rule[rule.find(('{} dport {}').format(protocol,dport))+len(('{} dport {}').format(protocol,dport)):].strip()
   ############ 
   if sport is None and dport is None and not protocol.startswith("icmp type") and protocol.upper()!="ALL" :
      rule=rule[:rule.find(policy)]+"ip protocol {} ".format(protocol)+rule[rule.find(policy):]
   return rule


#### function to get file config contenu
def get_config_file(ifname):
   cmd="cat /etc/rules/{}/nftables.conf".format(ifname)
   output,error=run_command("sudo "+cmd)
   # print(output)
   if error!='': 
      return error
   return output.splitlines()
   
###function to add rule
###function to add rule
def add_rule_remote(rule,ifname,type_rule):
   ##initialiser les commanndes pour ajouter une règle et l'entregistrer 
      commandes=[
         "sudo nft add rule inet filter_{} {} {}".format(ifname,type_rule,rule),
        'sudo nft list table inet filter_{} > /etc/rules/{}/nftables.conf'.format(ifname,ifname)
   ]
      ###executer ces commandes
      for cmd in commandes:
         _,error=run_command(cmd)
         if error!='': 
            return error
      return True

###function to get handle rule   
def get_handle_rule(ifname,type_rule,rule):
   # if not(rule.find('sport')==-1 and rule.find('dport')==-1):
   if 'sport' not in rule and 'dport' not in rule:
      if rule.find('ip protocol')!=-1 and rule.find("type")==-1 :
         rule=rule.replace("icmp","1")
      rule=rule.replace("echo-request","8")
      rule=rule.replace("echo-reply","0")
      rule=rule.replace("tcp","6")
      rule=rule.replace("udp","17")
   ##cmd pour obtenir handle number pour supprimer rule 
   cmd="sudo nft --handle --numeric list chain inet filter_{} {} | grep '{}'".format(ifname,type_rule,rule)
   ##executer cette commande
   output,_=run_command(cmd)
   output = output.split('#')
   # print(cmd,output)
   if len(output)<2:
      return None
   else:
      return output[1].strip().split("\n")[0]

###function to delete rule
def delete_rule_remote(ifname,type_rule,handle):
   ##initialiser les commanndes pour supprimer une règle et l'entregistrer dans nftables.conf
   commandes=[
      "sudo nft delete rule inet filter_{} {} {}".format(ifname,type_rule,handle),
      'sudo nft list table inet filter_{} > /etc/rules/{}/nftables.conf'.format(ifname,ifname)
   ]
   ##executer ces commandes
   for cmd in commandes:
      _,error=run_command(cmd)
      if error !="":
         return error  
   return True

   
### function to get protocol
def get_protocol_number(protocol_name):
    try:
        protocol_number = socket.getprotobyname(protocol_name)
        return protocol_number
    except socket.error:
        return None  # Protocol name not found

     
def calculate_subnet_address(addr_prefix):
   if addr_prefix is not None:
      ip_address=addr_prefix.split("/")[0]
      prefix=addr_prefix.split("/")[1]
   # Validate input IP address
      try:
         ip_address = ipaddress.IPv4Address(ip_address)
      except ValueError as e:
         return f"Invalid input: {e}"
      if prefix!="32":
         network = ipaddress.IPv4Network(f"{ip_address}/{prefix}", strict=False)
         return str(network.network_address)+"/"+prefix
      else:
         return str(ip_address)
   else:
      return None