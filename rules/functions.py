import paramiko
from rules.serializers import *
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.163', username='root', password='root')
 
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
   cmd="""bash -c 'if [ ! -d /etc/rules/{} ];then
sudo mkdir -p /etc/rules/{}
sudo cat <<EOF >> /etc/rules/{}/nftables.conf
{} 
EOF
sudo nft add table inet filter_{} 
sudo nft add chain inet filter_{} inbound {{ type filter hook input priority 0 \; }}
sudo nft add chain inet filter_{} outbound {{ type filter hook input priority 0 \; }}
sudo nft add chain inet filter_{} cellular {{ type filter hook input priority 0 \; }}
sudo nft add chain inet filter_{} inbound_cellular {{ type filter hook input priority 0 \; }}
sudo cat <<EOF >> /etc/nftables.conf
{} 
EOF
fi'""" .format(ifname,ifname,ifname,rules,ifname,ifname,ifname,ifname,ifname,include_rules)
##executer le script créée précédamment retourner true si pas d'error sinon false en cas d'error
   stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   error = stderr.read().decode('utf-8')
   output = stdout.read().decode('utf-8').split('\n')
   if error:
      return False
   return True


###function to return rule  outbound
def return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule):
   #initialiser une chaine vide
   rule=''
   ##cas inbound
   if type_rule=='inbound':
         rule='iifname "{}" ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(ifname,saddr,daddr,protocol,sport,protocol,dport,policy)
    ##cas outbound
   elif type_rule=='outbound':
         print("outbound==========")
         rule='oifname "{}" ip daddr {} ip saddr {} {} dport {} {} sport {} {}'.format(ifname,daddr,saddr,protocol,dport,protocol,sport,policy)
   #####cas saddr is None
   if saddr is None:
      rule=rule[:rule.find('ip saddr None')]+rule[rule.find('ip saddr None')+len(('ip saddr None'))+1:].strip()
      print('confition1====',rule)
   #####cas daddr is None
   if daddr is None:
      rule=rule[:rule.find('ip daddr None')]+rule[rule.find('ip daddr None')+len(('ip daddr None'))+1:].strip()
      print('confition2====',rule)
   #####cas sport is None
   if sport is None:
      rule=rule[:rule.find(('{} sport None').format(protocol))]+rule[rule.find(('{} sport None').format(protocol))+len(('{} sport None').format(protocol)):].strip()
      print('confition3====',rule)
   #####cas dport is None
   if dport is None:
      rule=rule[:rule.find(('{} dport None').format(protocol))]+rule[rule.find(('{} dport None').format(protocol))+len(('{} dport None').format(protocol)):].strip()
      print('confition4====',rule)
   # print(rule)
   return rule
###function to add rule
def add_rule_remote(rule,ifname,type_rule):
   ##initialiser les commanndes pour ajouter une règle et l'entregistrer 
      commandes=[
         "sudo nft add rule inet filter_{} {} {}".format(ifname,type_rule,rule),
        'sudo nft list table inet filter_{} > /etc/rules/{}/nftables.conf'.format(ifname,ifname)
   ]
      ###executer ces commandes
      for cmd in commandes:
         stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
         error = stderr.read().decode('utf-8')
         if error: 
            return False
      return True
###function to get handle rule   
def get_handle_rule(ifname,type_rule,rule):
   ##cmd pour obtenir handle number pour supprimer rule 
   cmd="sudo nft --handle --numeric list chain inet filter_{} {} | grep '{}'".format(ifname,type_rule,rule)
   ##executer cette commande
   stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   error = stderr.read().decode('utf-8')
   output = stdout.read().decode('utf-8').split('#')
   if error:
      print("error ",error,"    :",cmd)
   else:
     print(output)
   return output[1].strip('\n').strip()
###function to delete rule
def delete_rule_remote(ifname,type_rule,handle):
   ##initialiser les commanndes pour supprimer une règle et l'entregistrer dans nftables.conf
   commandes=[
      "sudo nft delete rule inet filter_{} {} {}".format(ifname,type_rule,handle),
      'sudo nft list table inet filter_{} > /etc/rules/{}/nftables.conf'.format(ifname,ifname)
   ]
   ##executer ces commandes
   for cmd in commandes:
      stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
      error = stderr.read().decode('utf-8')
      if error:
        return False    
   return True

   
###function to add in DB
def add_rule_DB(data,rule,type_rule):
   data['rule']=rule
   data["rule_status"]=True
   data["type_rule"]=type_rule
   
   print(data)
   InboundSerializer = RuleSerializer(data=data)
   print(InboundSerializer.is_valid())
   if InboundSerializer.is_valid():
      InboundSerializer.save()
      return True
   return False

###function to update rule in DB
def update_rule_DB(rule,rules,data):
         data['rule']=rule
         InboundSerializer = RuleSerializer(rules,data=data)
         if InboundSerializer.is_valid():
            InboundSerializer.save()
            return True
         return False





