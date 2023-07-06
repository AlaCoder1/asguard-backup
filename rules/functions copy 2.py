import paramiko
from rules.serializers import *
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.178', username='root', password='root')
 
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
def return_rule_inbound(policy,saddr,daddr,sport,dport,protocol):
   rule=''
   if saddr is not None and daddr is not None and sport is not None and dport is not None and protocol is not None:
      rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
   elif saddr is not None and daddr is not None and dport is not None and protocol is not None:
       rule='ip saddr {} ip daddr {} {} dport {} {}'.format(saddr,daddr,protocol,dport,policy)
   elif  saddr is not None  and sport is not None and protocol is not None:
       rule='ip saddr {}  {} sport {}  {}'.format(saddr,protocol,sport,policy)
   elif  saddr is not None:
       rule='ip saddr {} '.format(saddr,policy)
   return rule

###function to add in DB
def add_rule_DB(rule):
   id_rule=0
   data={"rule":"","rule_status":False}
   data['rule']=rule
   data["rule_status"]=True
   InboundSerializer = InboundRuleSerializer(data=data)
   if InboundSerializer.is_valid():
      instance=InboundSerializer.save()
      rule_obj = InboundRule.objects.latest('id')
      id_rule=rule_obj.pk
      print({"id_rule":id_rule})
   return id_rule
###function to add rule
def add_rule(rule,file_path):
   cmd = """python -c "
with open('{}', 'r') as file:
    for line in file:
        print(line)
        " """.format(file_path)
   ssh.exec_command(cmd)
   stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   error = stderr.read().decode('utf-8')
   output = stdout.read().decode('utf-8').split('\n')
   output = [x for x in output if x] 
   print({"output":output})
   msg=""
   if rule not in output:
      output.append(rule) 
    #cmd ajouter rule in file
      commandes=["""sudo cat <<EOF > {}
{}
EOF""".format(file_path,'\n'.join(output)),
   "sudo systemctl restart nftables.service"
   ]
     
      for cmd in commandes:
         stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
         error = stderr.read().decode('utf-8')
         output = stdout.read().decode('utf-8').split('\n')

      if error:
         msg="error "+error,"    :"+cmd
         print("error ",error,"    :",cmd)
         
         # break
      else:
         id_rule=add_rule_DB(rule)
         
         print("service created successufully!!",cmd,"id rule ===",id_rule) 
         msg="Successufully add rule "+cmd,"  id  :"+str(id_rule)
   else:
      msg="rule exist!!" 
   return msg        
   
#    print(output)
    

# policy="drop"
# saddr= '10.1.12.24'
# daddr='10.1.12.178'
# sport=None
# dport='22'
# protocol='tcp'  
# file_path='/etc/rules/inbound.conf'
# rule=return_rule_inbound(policy,saddr,daddr,sport,dport,protocol)
# add_rule(rule,file_path)









