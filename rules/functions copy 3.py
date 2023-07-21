import paramiko
from rules.serializers import *
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.237', username='root', password='root')
 
##function initial nftables.conf
def init_file_nftables():
   rules=[ 
'table inet filter {',
'        chain inbound {',
'                type filter hook input priority filter; policy accept;',
'                include "/etc/rules/inbound.conf";',
'        }',

'        chain outbound {',
'                type filter hook input priority filter; policy accept;',
'                include "/etc/rules/outbound.conf";',
'        }',
'        chain cellular {',
'                type filter hook input priority filter; policy accept;',
                'include "/etc/rules/cellular.conf";',
'        }',
'        chain inbound_cellular {',
'                type filter hook input priority filter; policy accept;',
                'include "/etc/rules/inbound_cellular.conf";',
'        }',
'}'   
     ]
   cmd="""sudo cat <<EOF > /etc/nftables.conf
{}
EOF""".format('\n'.join(rules))
   
   stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   error = stderr.read().decode('utf-8')
   output = stdout.read().decode('utf-8').split('\n')
   if error:
      print("error ",error,"    :",cmd)
      
   else:
      print("service created successufully!!",cmd)

# init_file_nftables() 
###function to return rule  inbound
# def return_rule_inbound(policy,saddr,daddr,sport,dport,protocol):
#    rule=''
#    if saddr is not None and daddr is not None and sport is not None and dport is not None and protocol is not None:
#       rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
#    elif saddr is not None and daddr is not None and dport is not None and protocol is not None:
#        rule='ip saddr {} ip daddr {} {} dport {} {}'.format(saddr,daddr,protocol,dport,policy)
#    elif saddr is not None and daddr is not None and protocol is not None:
#        rule='ip saddr {} ip daddr {} {} {}'.format(saddr,daddr,protocol,policy)
#    elif  saddr is not None  and sport is not None and protocol is not None:
#        rule='ip saddr {}  {} sport {}  {}'.format(saddr,protocol,sport,policy)
#    elif  saddr is not None:
#        rule='ip saddr {} '.format(saddr,policy)
#    return rule

def return_rule_inbound(policy,saddr,daddr,sport,dport,protocol):
   rule=''
   rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
   if saddr is None:
      rule=rule[:rule.find('ip saddr')]+rule[rule.find('ip daddr'):].strip()
      print('confition1====',rule)
   if daddr is None:
      rule=rule[:rule.find('ip daddr None')]+rule[rule.find('ip daddr None')+len(('ip daddr None'))+1:].strip()
      print('confition2====',rule)
   if sport is None:
      rule=rule[:rule.find(('{} sport None').format(protocol))]+rule[rule.find(('{} sport None').format(protocol))+len(('{} sport None').format(protocol)):].strip()
      print('confition3====',rule)
   # if protocol is None:
   #    print(rule[:rule.find('None sport')])
   #    print(rule[rule.find('sport'):rule.find('None dport')])
   #    print(rule[:rule.find('None sport')]+rule[rule.find('sport'):rule.find('None dport')]+rule[rule.find('dport'):])
   #    print(rule[rule.find('dport'):])
   #    rule=rule[:rule.find('None sport')]+rule[rule.find('sport'):rule.find('None dport')]+rule[rule.find('dport'):]
   #    print('confition3====',rule)
   
   if dport is None:
      rule=rule[:rule.find(('{} dport None').format(protocol))]+rule[rule.find(('{} dport None').format(protocol))+len(('{} dport None').format(protocol)):].strip()

      print('confition5====',rule)
   # print(rule)
   return rule


###function to add rule
def add_rule_remote(rule,file_path):
   cmd="sudo cat {}".format(file_path)
   ssh.exec_command(cmd)
   stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   output = stdout.read().decode('utf-8').split('\n')
   output = [x for x in output if x] 
   print({"output":output})
   if rule not in output:
      output.append(rule) 
    #cmds ajouter rule in file
      commandes=[
          'sudo nft flush ruleset',
          """sudo cat <<EOF > {}
{}
EOF""".format(file_path,'\n'.join(output)),
   "sudo systemctl restart nftables.service"
   ]
      for cmd in commandes:
         stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
         error = stderr.read().decode('utf-8')
         output = stdout.read().decode('utf-8').split('\n')
         if error: 
           return False
   
      return True
   return False
###function to delete rule
def delete_rule_remote(rule,file_path):
   commandes=[
      'sudo nft flush ruleset',
      "sudo sed -i '/{}/d' {}".format(rule,file_path),
        "sudo systemctl restart nftables.service"
   ]
   for cmd in commandes:
      stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
      error = stderr.read().decode('utf-8')
      if error:
        return False    
   return True

   
###function to add in DB
def add_rule_DB(rule,type_rule):
   data={"rule":"","rule_status":False,"type_rule":""}
   data['rule']=rule
   data["rule_status"]=True
   data["type_rule"]=type_rule
   print(data)
   InboundSerializer = InboundRuleSerializer(data=data)
   print(InboundSerializer.is_valid())
   if InboundSerializer.is_valid():
      InboundSerializer.save()
      return True
   return False

###function to update rule in DB
def update_rule_DB(rule,rules,data):
         data['rule']=rule
         InboundSerializer = InboundRuleSerializer(rules,data=data)
         if InboundSerializer.is_valid():
            InboundSerializer.save()
            return True
         return False





