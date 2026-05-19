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
"sudo nft add chain inet filter_{} inbound {{ type filter hook forward priority 0 \; }}".format(ifname),
"sudo nft add chain inet filter_{} outbound {{ type filter hook forward priority 0 \; }}".format(ifname),
"sudo nft add chain inet filter_{} cellular {{ type filter hook forward priority 0 \; }}".format(ifname),
"sudo nft add chain inet filter_{} inbound_cellular {{ type filter hook forward priority 0 \; }}".format(ifname),
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


def return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule):
   """function to return rule  outbound"""
   #initialiser une chaine vide
   rule=''
   #concatener tous les addresses à bloquer
   ##cas inbound
   if policy=="reject":
      policy="reject with icmp port-unreachable"
   if type_rule=='inbound' :
      if protocol.upper() != "ALL":
         rule = f'ip saddr {saddr} ip daddr {daddr} {protocol} sport {sport} {protocol} dport {dport} {policy}'
      else:
         rule = f'ip saddr {saddr} ip daddr {daddr} {policy}'
         
    ##cas outbound
   elif type_rule=='outbound' :
      if protocol.upper() != "ALL":
         rule = f'ip daddr {daddr} ip saddr {saddr} {protocol} sport {sport} {protocol} dport {dport} {policy}'
      else:
         rule = f'ip daddr {daddr} ip saddr {saddr} {policy}'
         
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
      rule=rule[:rule.find(policy)]+" ip protocol {} ".format(protocol)+rule[rule.find(policy):]
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
         'sudo nft add rule inet filter_{} {} {} '.format(ifname,type_rule,rule),
         "sudo nft list table inet filter_{} > /etc/rules/{}/nftables.conf".format(ifname,ifname)
         ]
      ###executer ces commandes
      for cmd in commandes:
         _,error=run_command(cmd)
         if error!='': 
            # print({"cmd":cmd,"error":error})
            return error
      return True


def get_handle_rule(ifname,type_rule,rule):
   """function to get handle rule"""
   # if not(rule.find('sport')==-1 and rule.find('dport')==-1):
   rule_modif=rule.split("log prefix")[0]   
   # print(rule)
   if 'sport' not in rule and 'dport' not in rule:
      if rule_modif.find('ip protocol')!=-1 and rule_modif.find("type")==-1 :
         ip_protocol_index = rule_modif.find('ip protocol')
         reject_with_index = rule_modif.find('reject with')
         icmp_index = rule_modif.find('icmp', ip_protocol_index)
         if icmp_index != -1 and (reject_with_index == -1 or icmp_index < reject_with_index):
            rule_modif = rule_modif[:icmp_index] + '1' + rule_modif[icmp_index + len('icmp'):]
         # rule = rule.replace("icmp", "1", 1)
     
      rule_modif=rule_modif.replace("echo-request","8")
      rule_modif=rule_modif.replace("echo-reply","0")
      rule_modif=rule_modif.replace("tcp","6")
      rule_modif=rule_modif.replace("udp","17")
   ##cmd pour obtenir handle number pour supprimer rule 
   rule_modif=rule_modif.replace("port-unreachable","3")
   rule=rule.replace("port-unreachable","3")
   if rule.find("log prefix")!=-1:
      rule=f"{rule_modif.strip()} log prefix {rule.split("log prefix")[1].strip()}" 
   cmd="sudo nft --handle --numeric list chain inet filter_{} {} | grep '{}'".format(ifname,type_rule,rule)
   ##executer cette commande
   output,_=run_command(cmd)
   output = output.split('#')
   # print(cmd,output)
   if len(output)<2:
      return None
   else:
      return output[1].strip().split("\n")[0]

def update_rule_remote(ifname,type_rule,handle,ruleupdate):
   """function to update rule"""
   ##initialiser les commanndes pour supprimer une règle et l'entregistrer dans nftables.conf
   commandes=[
      f"sudo nft replace rule inet filter_{ifname} {type_rule} handle {handle} {ruleupdate} ",
      f'sudo nft list table inet filter_{ifname} > /etc/rules/{ifname}/nftables.conf'
   ]
   ##executer ces commandes
   for cmd in commandes:
      _,error=run_command(cmd)
      if error !="":
         return error  
   return True

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


def get_position(type_rule):
   positions = list(Rule.objects.filter(type_rule=type_rule).values_list('position', flat=True))
   max_position = max(positions) if positions else 0
   position=max_position+1
   return position
     
def calculate_subnet_address(addr_prefix):
   if addr_prefix is not None:
      if addr_prefix.find('/')!=-1:
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
         return addr_prefix
   else:
      return None
   
   
   
###
def add_rule_db(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule,rule_description,interface_object,position):
   """function to add rule in system and database"""
   msg=''
   id_rule=None
   #appel la fonction pour initialiser les fichies nftables.conf
   return_init_file_nftables = init_file_nftables(ifname)
   if return_init_file_nftables:
      saddr_db=calculate_subnet_address(saddr)
      daddr_db=calculate_subnet_address(daddr)
      #appel la fonction pour retourner rule à ajouter 
      rule=return_rule(ifname,policy,saddr_db,daddr_db,sport,dport,protocol,type_rule)
      prefix="___nftables_logs_rule___"+"_".join(rule.split(" "))+"___"
      prefix=prefix.replace('"', '')
      prefix=prefix.replace('-', '')
      prefix=prefix.replace("reject_with_icmp_portunreachable","reject")
      if rule.find("reject with icmp port-unreachable")==-1:
         rule_mod=" ".join(rule.split(" ")[:-1])
         policy=rule.split(" ")[-1]
         rule=f'{rule_mod} log prefix "{prefix}" {policy}'
      else:
         rule_mod=rule.split("reject with icmp port-unreachable")[0].strip()
         rule=f'{rule_mod} log prefix "{prefix}" reject with icmp port-unreachable'
      
      rule=rule.strip()
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
         # position=get_handle_rule(ifname,type_rule,rule)
         # position=int(position.strip('handle').strip()) if position is not None else None
         # print({"position":position})
         
         if return_add_rule is True:
            data = {
               'policy': policy,
               'saddr':saddr,
               'daddr': daddr,
               'sport': sport,
               'dport': dport,
               'protocol': protocol,
               'type_rule': type_rule,
               'rule_description': rule_description,
               'position':position,
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
            # print({"error rule ":return_add_rule})
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
def update_rule_db(id,ifname,policy,saddr,daddr,sport,dport,protocol,rule_description,position):
      if (id is not None and Rule.objects.filter(id=id).exists()):
         rules_object = Rule.objects.get(id=id)
         rule=rules_object.rule
         type_rules=rules_object.type_rule
         #appel la fonction pour retourner rule à ajouter 
         saddr_db=calculate_subnet_address(saddr)
         daddr_db=calculate_subnet_address(daddr)
         #appel la fonction pour retourner rule à ajouter 
         ruleupdate=return_rule(ifname,policy,saddr_db,daddr_db,sport,dport,protocol,type_rules)
         prefix="___nftables_logs_rule___"+"_".join(ruleupdate.split(" "))+"___"
         prefix=prefix.replace('"', '')
         prefix=prefix.replace('-', '')
         prefix=prefix.replace("reject_with_icmp_portunreachable","reject")
         
         if ruleupdate.find("reject with icmp port-unreachable")==-1:
            rule_mod=" ".join(ruleupdate.split(" ")[:-1])
            policy=ruleupdate.split(" ")[-1]
            ruleupdate=f'{rule_mod} log prefix "{prefix}" {policy}'
         else:
            rule_mod=ruleupdate.split("reject with icmp port-unreachable")[0].strip()
            ruleupdate=f'{rule_mod} log prefix "{prefix}" reject with icmp port-unreachable'
         ruleupdate=ruleupdate.strip()
         handle=get_handle_rule(ifname,type_rules,rule)
         if handle is not None: 
               return_delete_rule_remotyre=delete_rule_remote(ifname,type_rules,handle)
         if not Rule.objects.filter(
               ~Q(id=id)& 
               Q(rule=ruleupdate) & (
               (Q(interface_id=rules_object.interface_id) ) &
               (Q(type_rule=type_rules))
               # & Q (rule_description=rule_description)
               )
            ).exists():
               # if return_delete_rule_remote is True:
                  return_add_rule=add_rule_remote(ruleupdate,ifname,type_rules)
                  # position=get_handle_rule(ifname,type_rules,rule)
                  # position=int(position.strip('handle').strip()) if position is not None else None
                  if  return_add_rule is True:
                        data = {
                        "id":id,
                        'policy': policy,
                        'saddr':saddr,
                        'daddr': daddr,
                        'sport': sport,
                        'dport': dport,
                        'protocol': protocol,
                        'rule_description': rule_description,
                        'position':position,
                        
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
               # else:
               #    msg=f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"
               #    status=400
            # else:
            #    msg=f"{CONSTANT_RULE} {ERROR_MESSAGES_EXISTANT}"
            #    status=400
         else:
               msg= f"{CONSTANT_RULE} {ERROR_MESSAGES_EXISTANT}"
               status=400
              
      else:
         msg=f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"
         status=400

      return msg,status


# ─────────────────────────────────────────────────────────────────────────────
# Rebuild nftables from the database
# ─────────────────────────────────────────────────────────────────────────────
# Called after an LVM snapshot restore so the runtime nftables state (kernel +
# /etc/rules/<ifname>/nftables.conf) matches the rolled-back DB. Without this,
# the on-disk file contains whatever was captured in the snapshot — which can
# legitimately include rules that were ALREADY orphaned at snapshot time (rule
# present in file but missing from DB, e.g. left over from a partial nft sync).
# Making the DB the single source of truth eliminates that drift.
def rebuild_nft_from_db(ifname: str) -> dict:
    """Flush table inet filter_<ifname>, recreate its chains, and re-apply every
    enabled Rule for this interface in `position` order. Final kernel state is
    dumped back to /etc/rules/<ifname>/nftables.conf so the persistent file is
    also realigned with the DB.

    Returns {"status": "success"|"error", "ifname": ..., "applied": N,
             "errors": [str]}.
    """
    from backend.rules.models import Rule
    from backend.network.models import Interface

    errors: list[str] = []

    # Resolve the Interface row. Some installs don't have a row per nft table
    # (e.g. ens33 exists in fstab but not in the Interface model) — in that
    # case we still flush + recreate empty chains so stale rules disappear.
    iface = Interface.objects.filter(ifname=ifname).first()

    # 1. Flush the existing table. `nft delete table` is idempotent (silent if
    # missing); we then re-init structures via init_file_nftables which creates
    # the table + four chains and writes a fresh /etc/rules/<ifname>/nftables.conf.
    run_command(f"sudo nft delete table inet filter_{ifname} 2>/dev/null || true")
    run_command(f"sudo rm -f /etc/rules/{ifname}/nftables.conf")
    init_err = init_file_nftables(ifname)
    if init_err is not True:
        return {"status": "error", "ifname": ifname, "applied": 0,
                "errors": [f"init_file_nftables: {init_err}"]}

    # 2. Re-apply enabled DB rules in their stored position order. Use the raw
    # `rule` column — it already holds the final nft expression that was
    # serialized at create/update time (with the log prefix baked in).
    applied = 0
    if iface is not None:
        rules_qs = (Rule.objects
                    .filter(interface=iface, rule_status=True)
                    .order_by("type_rule", "position", "id"))
        for r in rules_qs:
            if not r.rule or not r.type_rule:
                continue
            cmd = f"sudo nft add rule inet filter_{ifname} {r.type_rule} {r.rule}"
            _, err = run_command(cmd)
            if err:
                errors.append(f"rule id={r.id}: {err.strip()}")
            else:
                applied += 1

    # 3. Persist the final kernel state to the include file so a reboot or a
    # nft reload from /etc/nftables.conf produces the same view.
    run_command(
        f"sudo nft list table inet filter_{ifname} "
        f"> /etc/rules/{ifname}/nftables.conf"
    )

    return {
        "status":  "success" if not errors else "partial",
        "ifname":  ifname,
        "applied": applied,
        "errors":  errors,
    }


def rebuild_nft_from_db_all() -> dict:
    """Rebuild nftables for every Interface in the DB. Returns an aggregate
    `{"status", "interfaces": [{...per-iface result...}], "total_applied", "total_errors"}`.
    Safe to call from any post-restore hook — never raises."""
    from backend.network.models import Interface
    results = []
    total_applied = 0
    total_errors = 0
    try:
        for iface in Interface.objects.exclude(ifname__isnull=True).exclude(ifname=""):
            r = rebuild_nft_from_db(iface.ifname)
            results.append(r)
            total_applied += r.get("applied", 0)
            total_errors  += len(r.get("errors", []))
    except Exception as exc:  # never block the caller (e.g. restore_snapshot)
        return {"status": "error", "error": str(exc),
                "interfaces": results, "total_applied": total_applied,
                "total_errors": total_errors}
    status = "success" if total_errors == 0 else "partial"
    return {"status": status, "interfaces": results,
            "total_applied": total_applied, "total_errors": total_errors}

