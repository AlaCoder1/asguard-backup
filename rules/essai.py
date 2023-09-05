import paramiko
# from rules.serializers import *
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.156', username='root', password='root')
###function to get handle rule   
def get_handle_rule(ifname,type_rule,rule):
   ##cmd pour obtenir handle number pour supprimer rule 
   cmd="sudo nft --handle --numeric list chain inet filter_{} {} | grep '{}'".format(ifname,type_rule,rule)
   ##executer cette commande
   stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
   error = stderr.read().decode('utf-8')
   output = stdout.read().decode('utf-8').split('#')
   if error:
      return None
   else:
      return output[1].strip('\n').strip()
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
      if error !="":
        return error    
   return True

handle=get_handle_rule("eth2","inbound",'iifname "eth2" ip saddr 10.1.12.200 ip daddr 10.1.12.128 tcp sport 22 tcp dport 22 drop')
print(handle)
print(delete_rule_remote("eth2","inbound",handle))