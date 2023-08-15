import time
import paramiko


def connect_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.1.12.9', username='root', password='root')
    return ssh


def install_server_openvpn(server_name, server_conf):
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]
    commands_list_with_arguments = [{'command': 'sudo easyrsa clean-all', 'arguments': ['yes', 'yes']},
                                    {'command': 'sudo easyrsa init-pki', 'arguments': ['yes', 'yes']},
                                    {'command': 'sudo easyrsa build-ca nopass', 'arguments': [f'{server_name}']},
                                    {'command': 'sudo easyrsa build-server-full server', 'arguments': ['akrampass','akrampass','yes']},
                                    ]
    commands_list_without_arguments = ['sudo easyrsa gen-dh',
                                    f'rm /etc/openvpn/server/server_{server_name}.conf',
                                    f'''echo '{server_conf.strip()}' >>/etc/openvpn/server/server_{server_name}.conf''',
                                    f'mkdir /etc/openvpn/certificates_{server_name}/',
                                    f'cp {current_dir}/pki/ca.crt "/etc/openvpn/certificates_{server_name}/ca.crt"',
                                    f'cp {current_dir}/pki/issued/server.crt "/etc/openvpn/certificates_{server_name}/server.crt"',
                                    f'cp {current_dir}/pki/private/server.key "/etc/openvpn/certificates_{server_name}/server.key"',
                                    f'cp {current_dir}/pki/dh.pem "/etc/openvpn/certificates_{server_name}/dh.pem"',
                                    'chown -R openvpn:network /etc/openvpn/*',
                                    #    f'chown -R openvpn:network {current_dir}/*',
                                    'mkdir /var/log/openvpn/',
                                    'touch /var/log/openvpn/status.log',
                                    'sudo chown 777 /var/log/openvpn/status.log',
                                    ]
    execute_list_of_commands(ssh_connect=ssh, list_commands=commands_list_with_arguments)
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def execute_list_commands_without_arguments(ssh_connect, commands_list):
    for command_number, command in enumerate(commands_list):
        stdin, stdout, stderr = ssh_connect.exec_command(command)
        print(f'command {command}')
        print('Error: ', stderr.read().decode('utf-8'))
        print('Output: ', stdout.read().decode('utf-8'))


def execute_command_with_arguments(ssh_connect, command, arguments):
    """Function that execute a command line with arguments like passing a passphrase in building certificate"""
    # Open a session
    channel = ssh_connect.invoke_shell()

    # Send the command
    channel.send(f'{command}\n')
    time.sleep(1)

    # Send the list of arguments
    for arg in arguments:
        channel.send(f'{arg}\n')
        time.sleep(1)

    # Close the session
    channel.close()


def execute_list_of_commands(ssh_connect, list_commands):
    for command in list_commands:
        print(f"Command: {command['command']}")
        execute_command_with_arguments(ssh_connect=ssh_connect, command=command['command'], arguments=command['arguments'])
        print(f"Command done")


server_name = 'azizserver'
config_server =f'''port 1195
proto udp

# "dev tun" will create a routed IP tunnel.
dev tun
topology subnet

#Certificate Configuration

#ca certificate
ca /etc/openvpn/certificates_{server_name}/ca.crt
#Server Certificate
cert /etc/openvpn/certificates_{server_name}/server.crt

#Server Key and keep this is secret
key /etc/openvpn/certificates_{server_name}/server.key


#See the size a dh key in /etc/openvpn/keys/
dh /etc/openvpn/certificates_{server_name}/dh.pem

#Internal IP will get when already connect
server 10.8.1.0 255.255.255.0

#this line will redirect all traffic through our OpenVPN
push "redirect-gateway def1"
push "route 192.168.0.0 255.255.255.0"

#Provide DNS servers to the client, you can use goolge DNS
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"

#Enable multiple client to connect with same key
duplicate-cn

cipher AES-256-CBC

keepalive 20 60
# comp-lzo adaptive
persist-key
persist-tun
daemon

#openvpn status log
#status /var/log/openvpn/status.log

#enable log
#log-append /var/log/openvpn/openvpn.log

#Log Level
verb 3'''

install_server_openvpn(server_name=server_name, server_conf=config_server)
print('Installation done')
