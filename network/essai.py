import paramiko
# from rules.serializers import *
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.156', username='root', password='root')
def get_conn_name(ifname):
    cmd = "sudo nmcli connection show | awk '$NF == \"{}\" {{print}}'".format(ifname)
      ##executer cette commande
    stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
    output = stdout.read().decode('utf-8').split('  ')
   
    print(output)
    if len(output)==0:
        return None
    else:
        output=[value for value in output if value]
        uuid=output[1]
        return uuid
##    

def update_conn_Static_IPV4(uuid,ipaddress,netmask,gwaddr):
    
    commandes=[
        "sudo nmcli connection modify {} ipv4.method manual ipv4.addresses {}/{}".format(uuid,ipaddress,netmask),
        "sudo nmcli connection modify {} ipv4.gateway {} ipv4.route-metric 0 ".format(uuid,gwaddr),
         "sudo nmcli conn down {} && sudo nmcli conn up {}".format(uuid, uuid),
    ]
    for cmd in commandes:
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if error!="" and not error.startswith("Warning") :
            print("error",error,cmd)
        else:
            print("executed successfully!! ",cmd)
ipaddress="10.1.12.130"
netmask=32
gwaddr="10.1.13.1"
mtu=1800
uuid=get_conn_name("eth3")
print(uuid)
# update_conn_Static_IPV4(uuid,ipaddress,netmask,gwaddr)        
def update_conn_DHCP_IPV4(uuid,ifname):
    commandes=[
        "sudo nmcli connection modify {} ipv4.method auto ipv4.addresses '' ipv4.gateway '' ipv4.route-metric '' ".format(uuid),
        "sudo nmcli conn down {} && sudo nmcli conn up {}".format(uuid, uuid),
        "sudo dhclient -v -cf  /etc/Dhcp4Config/{}/dhclient.conf".format(ifname),
    ]
    for cmd in commandes:
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if error!="" and not error.startswith("Warning") :
            print("error",error,cmd)
        else:
            print("executed successfully!! ",cmd)
update_conn_DHCP_IPV4(uuid,"eth3")