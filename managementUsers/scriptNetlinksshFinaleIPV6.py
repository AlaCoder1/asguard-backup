import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.216', username='root', password='rootroot')
###################
# delete dhcp config file if exist


def delete_config_file(ifname):
    command = "if [ -d /etc/Dhcp6Config/{} ]; then rm -r /etc/Dhcp6Config/{}; fi".format(
        ifname, ifname)
    stdin, stdout, stderr = ssh.exec_command(command)
    error = stderr.read().decode('utf-8')
    return error


# delete_old_address


def delete_old_address(ifname):
    command = """python -c "
ifname='{}'
from pyroute2 import IPRoute
ip = IPRoute()
index = ip.link_lookup(ifname=ifname)[0]
ip.link('set', index=index, state='down')
address = ip.get_addr(index=index)
for addr in address:
    if addr['family'] == 2 or addr['family'] == 10 :
        ip.addr('del', index=index, address=addr['attrs'][0][1], mask=addr['prefixlen'], family=addr['family'])
    " """.format(ifname)
    stdin, stdout, stderr = ssh.exec_command(command)
    error = stderr.read().decode('utf-8')
    return error

# convert dhcp  to static connexion


def update_conn_static_IPV6(ifname, ip_address, gateway):
    command = """python -c "
from pyroute2 import IPRoute
ip = IPRoute()
index = ip.link_lookup(ifname='{}')[0]
ip.addr('add', index=interface_index, address='{}')
ip.route('add', dst='default', gateway='{}', family=10)
ip.close()
    " """.format(ifname, ip_address, gateway)
    msg = ''
    error = delete_config_file(ifname)
    if error:
        msg = "Failed to delete config file !!\n"+error
        status = 500
    else:
        error = delete_old_address(ifname)
        if error:
            msg = "Failed to delete old address !!\n"+error
            status = 500
        else:
            stdin, stdout, stderr = ssh.exec_command(command)
            error = stderr.read().decode('utf-8')
            if error:
                msg = "Failed to update connexion to static !! \n"+error
                status = 400
            else:
                msg = "update connexion to static successufully !!"
                status = 200
    return msg, status
###################
ifname="eth2"
ip_address='2001:db8::1000/64'
gateway='fe80::1'
update_conn_static_IPV6(ifname, ip_address, gateway)










