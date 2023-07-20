import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.178', username='root', password='root')
 
##function to create chaineroot
def create_chaine():
    commandes=[
       'sudo nft add table inet filter',
       'nft add chain inet filter inbound { type filter hook input priority 0 \; }',
       'nft add chain inet filter outbound { type filter hook input priority 0 \; }',
       'nft add chain inet filter cellular { type filter hook input priority 0 \; }',
       'nft add chain inet filter inbound_cellular { type filter hook input priority 0 \; }',
       'nft list ruleset > /etc/nftables.conf',
       'sudo systemctl restart nftables.service'
    ]
    for cmd in commandes:
         ssh.exec_command(cmd)
 
create_chaine()   
###function to add rule
def add_rule_inbound(policy,saddr,daddr,sport,dport,protocol):
   rule=''
   if saddr is not None and daddr is not None and sport is not None and dport is not None and protocol is not None:
      rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
   elif saddr is not None and daddr is not None and dport is not None and protocol is not None:
       rule='ip saddr {} ip daddr {} {} dport {} {}'.format(saddr,daddr,protocol,dport,policy)
   elif  saddr is not None  and sport is not None and protocol is not None:
   #     rule='ip saddr {}  {} sport {}  {}'.format(saddr,protocol,sport,policy)
   
      #  rule='ip saddr {} ip daddr {} {} dport {} {}'.format(saddr,daddr,protocol,dport,policy)
       
   print(rule)
   commandes=[
      'sudo nft flush ruleset',
      'sudo nft add rule inet filter inbound {}'.format(rule),
      'sudo nft list ruleset > /etc/nftables.conf',
      'sudo systemctl restart nftables.service'
   ]
   for cmd in commandes:
         stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
         error = stderr.read().decode('utf-8')
         output = stdout.read().decode('utf-8').split('\n')

         if error:
            print("error ",error,"    :",cmd)
            # break
         else:
            print("service created successufully!!",cmd)
policy="drop"
saddr= '10.1.12.101'
daddr='10.1.12.178'
sport=''
dport='22'
protocol='tcp'  
add_rule_inbound(policy,saddr,daddr,sport,dport,protocol)

###function to add rule
def add_rule_outbound(policy,saddr,daddr,sport,dport,protocol):
   rule=''
   if saddr is not None and daddr is not None and sport is not None and dport is not None and protocol is not None:
      #  rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
       rule='ip saddr {} ip daddr {} {} dport {} {}'.format(saddr,daddr,protocol,dport,policy)
       
   print(rule)
   commandes=[
      'sudo nft flush ruleset',
      'sudo nft add rule inet filter inbound {}'.format(rule),
      'sudo nft list ruleset > /etc/nftables.conf',
      'sudo systemctl restart nftables.service'
   ]
   for cmd in commandes:
         stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
         error = stderr.read().decode('utf-8')
         output = stdout.read().decode('utf-8').split('\n')

         if error:
            print("error ",error,"    :",cmd)
            # break
         else:
            print("service created successufully!!",cmd)
    
policy="drop"
saddr= '10.1.12.101'
daddr='10.1.12.178'
sport=''
dport='22'
protocol='tcp'    
add_rule_outbound(policy,saddr,daddr,sport,dport,protocol)
#################################################################################################
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.178', username='root', password='root')
 
##function to create chaineroot
def create_chaine():
    commandes=[
      #  'sudo nft flush ruleset',
       'sudo nft add table inet filter',
       'nft add chain inet filter inbound { type filter hook input priority 0 \; }',
       'nft add chain inet filter outbound { type filter hook input priority 0 \; }',
       'nft add chain inet filter cellular { type filter hook input priority 0 \; }',
       'nft add chain inet filter inbound_cellular { type filter hook input priority 0 \; }',
       'nft list ruleset > /etc/nftables.conf',
       'sudo systemctl restart nftables.service'
    ]
    for cmd in commandes:
         stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
         error = stderr.read().decode('utf-8')
         output = stdout.read().decode('utf-8').split('\n')

         if error:
            print("error ",error,"    :",cmd)
            break
         else:
            print("service created successufully!!",cmd)
 
create_chaine()   
###function to add rule
def add_rule_inbound(policy,saddr,daddr,sport,dport,protocol):
   rule=''
   if saddr is not None and daddr is not None and sport is not None and dport is not None and protocol is not None:
      rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
   elif saddr is not None and daddr is not None and dport is not None and protocol is not None:
       rule='ip saddr {} ip daddr {} {} dport {} {}'.format(saddr,daddr,protocol,dport,policy)
   elif  saddr is not None  and sport is not None and protocol is not None:
       rule='ip saddr {}  {} sport {}  {}'.format(saddr,protocol,sport,policy)
   elif  saddr is not None:
       rule='ip saddr {} '.format(saddr,policy)
       
   print(rule)
   cmd = """python -c "
with open('/etc/inbound.conf', 'r') as file:
    for line in file:
        print(line)
        " """
   ssh.exec_command(cmd)
   stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   error = stderr.read().decode('utf-8')
   output = stdout.read().decode('utf-8').split('\n')
    #cmd ajouter un dossier contenant le fichier config
   cmd="""bash -c 'mkdir -p /etc/nftables.conf && cat <<EOF > /etc/nftables.conf
{}
EOF' """.format('\n'.join(output))
   output = [x.strip('\t') for x in output if x]    
   print(output)
    
   # commandes=[
   #    # 'sudo nft flush chain inet filter inbound',
   #    'sudo nft add rule inet filter inbound {}'.format(rule),
   #    'sudo nft list ruleset > /etc/nftables.conf',
   #    'sudo systemctl restart nftables.service'
   # ]
   # for cmd in commandes:
   #       stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   #       error = stderr.read().decode('utf-8')
   #       output = stdout.read().decode('utf-8').split('\n')

   #       if error:
   #          print("error ",error,"    :",cmd)
   #          break
   #       else:
   #          print("service created successufully!!",cmd)
policy="drop"
saddr= '10.1.12.101'
daddr='10.1.12.178'
sport=None
dport='22'
protocol='tcp'  
# policy="drop"
# saddr= '10.1.12.101'
# daddr=None
# sport=None
# dport=None
# protocol=None
add_rule_inbound(policy,saddr,daddr,sport,dport,protocol)









###function to add rule
def add_rule_outbound(policy,saddr,daddr,sport,dport,protocol):
   rule=''
   if saddr is not None and daddr is not None and sport is not None and dport is not None and protocol is not None:
      #  rule='ip saddr {} ip daddr {} {} sport {} {} dport {} {}'.format(saddr,daddr,protocol,sport,protocol,dport,policy)
       rule='ip saddr {} ip daddr {} {} dport {} {}'.format(saddr,daddr,protocol,dport,policy)
       
   print(rule)
   commandes=[
      # 'sudo nft flush ruleset',
      'sudo nft add rule inet filter inbound {}'.format(rule),
      'sudo nft list ruleset > /etc/nftables.conf',
      'sudo systemctl restart nftables.service'
   ]
   for cmd in commandes:
         stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
         error = stderr.read().decode('utf-8')
         output = stdout.read().decode('utf-8').split('\n')

         if error:
            print("error ",error,"    :",cmd)
            # break
         else:
            print("service created successufully!!",cmd)
    
policy="drop"
saddr= '10.1.12.24'
daddr='10.1.12.178'
sport=''
dport='22'
protocol='tcp'    
add_rule_outbound(policy,saddr,daddr,sport,dport,protocol)