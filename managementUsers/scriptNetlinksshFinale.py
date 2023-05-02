import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.216', username='root', password='rootroot')
###################
# delete dhcp config file if exist


def delete_config_file(ifname):
    command = "if [ -d /etc/Dhcp4Config/{} ]; then rm -r /etc/Dhcp4Config/{}; fi".format(
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
    if addr['family'] == 2 :
        ip.addr('del', index=index, address=addr['attrs'][0][1], mask=addr['prefixlen'], family=addr['family'])
    " """.format(ifname)
    stdin, stdout, stderr = ssh.exec_command(command)
    error = stderr.read().decode('utf-8')
    return error
# convert dhcp  to static connexion


def update_conn_static(ifname, ip_address, netmask, gateway):
   
    command = """python -c "
from pyroute2 import IPRoute
ip = IPRoute()
ifname = '{}'
index = ip.link_lookup(ifname=ifname)[0]
ip.addr('add', index=index, address='{}', prefixlen={})
ip.route('set', dst='default', gateway='{}')
    " """.format(ifname, ip_address, netmask, gateway)
    msg = ''
    error = delete_config_file(ifname)
    if error:
        msg = "Failed to delete config file !!\n"+error
        status = 500
    
    else:
        error=delete_old_address(ifname)
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
# convert static  to dhcp  connexion base and advanced

# add_file


def add_file(config, ifname):
    cmd = """bash -c 'mkdir -p /etc/Dhcp4Config/{} && cat <<EOF > /etc/Dhcp4Config/{}/dhclient.conf
{}
EOF'""".format(ifname, ifname, '\n'.join(config))
    stdin, stdout, stderr = ssh.exec_command(cmd)
    error = stderr.read().decode('utf-8')
    return error

# obtain address dhcp


def obtain_address_dhcp(ifname):
    # Run dhclient to get new IP address
    command = " ".join(['sudo', 'dhclient', '-4', '-v', '-cf',
                       '/etc/Dhcp4Config/{}/dhclient.conf', ifname]).format(ifname)
    stdin, stdout, stderr = ssh.exec_command(command)
    # Wait for dhclient to finish
    result = stdout.channel.recv_exit_status()
    error = stderr.read().decode('utf-8')
    return result, error


def update_conn_dhcp(ifname, config):
    msg = ''
    error = delete_config_file(ifname)
    if error:
        msg = "Failed to delete config file! \n"+error
        status = 500
    else:
        error = delete_old_address(ifname)
        if error:
            msg = "Failed to prepare data!\n"+error
            status = 500
        else:
            error = add_file(config, ifname)
            if error:
                msg = "Failed to add file!\n"+error
                status = 500
            else:
                result, error = obtain_address_dhcp(ifname)
                if result == 0:
                    msg = "update connexion to dhcp successufully!!"
                    status = 200
                else:
                    err = ''
                    if len(error.split('\n')) > 1:
                        for p in error:
                            err += p+"\n"
                            msg = "Failed to update connexion to dhcp exit code: " + \
                                str(result)+"\n"+err
                    msg = "Failed to update connexion to dhcp exit code: " + \
                        str(result)+"\n"+error
                    status = 500
    return msg, status
