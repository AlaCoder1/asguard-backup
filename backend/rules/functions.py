import ipaddress
import subprocess
import socket
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from backend.rules.models import Rule
from backend.rules.serializers import RuleSerializer
CONSTANT_RULE = _('Rule')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("Error in creating")
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_EXISTANT = _("already exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")

def customize_error_msg(serializer):
    """function to custom error message serializer"""
    error_messages = [
    f"{field}: {error}"
    for field, errors in serializer.errors.items()
    for error in errors
]
    concatenated_error_message = "\n".join(error_messages)
    concatenated_error_message+="!"
    return concatenated_error_message
######function to run commande
def run_command(command):
    """function to run commande"""
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error


def init_file_nftables(ifname):
   """function initial nftables.conf et /rules/ifname/nftables.conf"""
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


def return_rule(policy,saddr,daddr,sport,dport,protocol,type_rule):
   """function to return rule  outbound"""
   #initialiser une chaine vide
   rule=''
   #concatener tous les addresses à bloquer
   ##cas inbound
   if policy=="reject":
      policy="reject with icmp port-unreachable"
   # if policy=="reject" and not protocol.startswith("icmp type"):
   #    policy="reject with icmp port-unreachable"
   # elif policy=="reject" and  protocol.startswith("icmp type"):
   #    policy="reject with icmp type port-unreachable"
   if type_rule=='inbound' :
      if protocol.upper() != "ALL":
         rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
      else:
         rule='ip saddr {} ip daddr {} {}'.format(saddr,daddr,policy)
         
    ##cas outbound
   elif type_rule=='outbound' :
      if protocol.upper() != "ALL":
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


def get_config_file(ifname):
   """function to get file config contenu"""
   cmd="cat /etc/rules/{}/nftables.conf".format(ifname)
   output,error=run_command("sudo "+cmd)
   # print(output)
   if error!='': 
      return error
   return output.splitlines()
   

def add_rule_remote(rule,ifname,type_rule):
      """function to add rule"""
      ##initialiser les commanndes pour ajouter une règle et l'entregistrer 
      commandes=[
         "sudo nft add rule inet filter_{} {} {}".format(ifname,type_rule,rule),
         "sudo nft list table inet filter_{} > /etc/rules/{}/nftables.conf".format(ifname,ifname)
         ]
      ###executer ces commandes
      for cmd in commandes:
         _,error=run_command(cmd)
         if error!='': 
            return error
      return True


def get_handle_rule(ifname,type_rule,rule):
   """function to get handle rule"""
   # if not(rule.find('sport')==-1 and rule.find('dport')==-1):
      
   if 'sport' not in rule and 'dport' not in rule:
      if rule.find('ip protocol')!=-1 and rule.find("type")==-1 :
         ip_protocol_index = rule.find('ip protocol')
         reject_with_index = rule.find('reject with')
         icmp_index = rule.find('icmp', ip_protocol_index)
         if icmp_index != -1 and (reject_with_index == -1 or icmp_index < reject_with_index):
            rule = rule[:icmp_index] + '1' + rule[icmp_index + len('icmp'):]
         # rule = rule.replace("icmp", "1", 1)
      rule=rule.replace("echo-request","8")
      rule=rule.replace("echo-reply","0")
      rule=rule.replace("tcp","6")
      rule=rule.replace("udp","17")
   ##cmd pour obtenir handle number pour supprimer rule 
   rule=rule.replace("port-unreachable","3")
   
   cmd="sudo nft --handle --numeric list chain inet filter_{} {} | grep '{}'".format(ifname,type_rule,rule)
   ##executer cette commande
   output,_=run_command(cmd)
   output = output.split('#')
   # print(cmd,output)
   if len(output)<2:
      return None
   else:
      return output[1].strip().split("\n")[0]


def delete_rule_remote(ifname,type_rule,handle):
   """function to delete rule"""
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

   
def get_protocol_number(protocol_name):
    """function to get protocol"""
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
   
   
   
###
def add_rule_db(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule,rule_description,interface_object):
   """function to add rule in system and database"""
   msg=''
   id_rule=None
   #appel la fonction pour initialiser les fichies nftables.conf
   return_init_file_nftables = init_file_nftables(ifname)
   if return_init_file_nftables:
      saddr_db=calculate_subnet_address(saddr)
      daddr_db=calculate_subnet_address(daddr)
      #appel la fonction pour retourner rule à ajouter 
      rule=return_rule(policy,saddr_db,daddr_db,sport,dport,protocol,type_rule)
      # if not Rule.objects.filter(Q(rule=rule) & ((Q(interface_id=interface_object.pk)& Q(type_rule!=type_rule ) )|(Q(interface_id!=interface_object.pk) & Q(type_rule=type_rule )))).exists():
      if not Rule.objects.filter(
            Q(rule=rule) & (
                  (Q(interface_id=interface_object.pk) ) &
                  (Q(type_rule=type_rule)) 
                  # Q(rule_description=rule_description)
            )
         ).exists():
      #appel la fonction pour ajouter rule dans le système
         return_add_rule=add_rule_remote(rule,ifname,type_rule)
         if return_add_rule is True:
            data = {
               'policy': policy,
               'saddr':saddr,
               'daddr': daddr,
               'sport': sport,
               'dport': dport,
               'protocol': protocol,
               'type_rule': type_rule,
               'rule_description': rule_description
               }
            data['interface']=interface_object.id
            #appel la fonction pour ajouter rule dans la base de données 
            data={key: value for key, value in data.items() if value is not None}
            data['rule']=rule
            data["rule_status"]=True
            data["type_rule"]=type_rule
            rule_serializer = RuleSerializer(data=data)
            # rule_serializer.is_valid(raise_exception=True)
            if rule_serializer.is_valid():
               rule_instance=rule_serializer.save()
               id_rule=rule_instance.id
   
               msg = f"{CONSTANT_RULE} {SUCCESS_MESSAGES_CREATING}"
               status=200
            else:
               msg=customize_error_msg(rule_serializer)
               status=400
         else:
            msg = f"{ERROR_MESSAGES_CREATING} {CONSTANT_RULE}"
            status=400
      else:
         msg=f"{CONSTANT_RULE} {ERROR_MESSAGES_EXISTANT}"
         status=400
   else:
      msg = f"{ERROR_MESSAGES_CREATING} {CONSTANT_RULE}"
      status=400
   return msg,status,id_rule

##
def update_rule_db(id,ifname,policy,saddr,daddr,sport,dport,protocol,rule_description):
      if (id is not None and Rule.objects.filter(id=id).exists()):
         rules_object = Rule.objects.get(id=id)
         rule=rules_object.rule
         type_rules=rules_object.type_rule
         #appel la fonction pour retourner rule à ajouter 
         saddr_db=calculate_subnet_address(saddr)
         daddr_db=calculate_subnet_address(daddr)
         #appel la fonction pour retourner rule à ajouter 
         ruleupdate=return_rule(policy,saddr_db,daddr_db,sport,dport,protocol,type_rules)
         handle=get_handle_rule(ifname,type_rules,rule)
         if handle is not None: 
            if not Rule.objects.filter(
                 ~Q(id=id)& 
                  Q(rule=ruleupdate) & (
                  (Q(interface_id=rules_object.interface_id) ) &
                  (Q(type_rule=type_rules))
                  # & Q (rule_description=rule_description)
                  )
               ).exists():
               return_delete_rule_remote=delete_rule_remote(ifname,type_rules,handle)
               if return_delete_rule_remote is True:
                  return_add_rule=add_rule_remote(ruleupdate,ifname,type_rules)
                  if  return_add_rule is True:
                        data = {
                        "id":id,
                        'policy': policy,
                        'saddr':saddr,
                        'daddr': daddr,
                        'sport': sport,
                        'dport': dport,
                        'protocol': protocol,
                        'rule_description': rule_description
                        }
                        
                        #appel la fonction pour update rule dans la base de données 
                        data['interface']=rules_object.interface_id
                        data['rule']=ruleupdate
                        rule_serializer = RuleSerializer(rules_object,data=data)
                        if rule_serializer.is_valid():
                           rule_serializer.save()
                           msg = f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"
                           status=200
                        else:
                           msg=customize_error_msg(rule_serializer)
                           status=400
                  else:
                        msg=f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"
                        status=400
               else:
                  msg=f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"
                  status=400
            else:
               msg=f"{CONSTANT_RULE} {ERROR_MESSAGES_EXISTANT}"
               status=400
         else:
               msg= f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"
               status=404
              
      else:
         msg=f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"
         status=400
         
      return msg,status
