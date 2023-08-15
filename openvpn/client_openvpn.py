import time
import paramiko

# from server_openvpn import execute_command_with_arguments, execute_list_commands_without_arguments


def connect_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.1.12.9', username='root', password='root')
    return ssh


def install_client_openvpn(client_name, client_conf):
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]
    print(f"Command: easyrsa build-client-full {client_name}")
    execute_command_with_arguments(ssh_connect=ssh, command=f'easyrsa build-client-full {client_name}', arguments=['clientpass', 'clientpass', 'yes'])
    print("command done")
    execute_list_commands_without_arguments(ssh_connect=ssh, 
                                            commands_list=[f'rm /etc/openvpn/client/client_{client_name}.ovpn',
                                                           f'''echo '{client_conf.strip()}' >>/etc/openvpn/client/client_{client_name}.ovpn''',
                                                           f'mkdir /etc/openvpn/client/certificates_{client_name}/',
                                                           f'cp {current_dir}/pki/issued/{client_name}.crt "/etc/openvpn/client/certificates_{client_name}/{client_name}.crt"',
                                                           f'cp {current_dir}/pki/private/{client_name}.key "/etc/openvpn/client/certificates_{client_name}/{client_name}.key"',
                                                           ])
    

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


server_name = 'azizserver'
client_name = 'test3client'
config_client = f'''client
remote 10.1.12.9 1195
proto udp
dev tun
nobind
remote-cert-tls server
cipher AES-256-CBC
auth-nocache
script-security 2
persist-key
persist-tun

ca /etc/openvpn/certificates_{server_name}/ca.crt
cert /etc/openvpn/client/certificates_{client_name}/{client_name}.crt
key /etc/openvpn/client/certificates_{client_name}/{client_name}.key
dh /etc/openvpn/certificates_{server_name}/dh.pem
tls-version-min 1.2
tls-cipher TLS-DHE-RSA-WITH-AES-256-GCM-SHA384:TLS-DHE-RSA-WITH-AES-128-GCM-SHA256:TLS-DHE-RSA-WITH-AES-256-CBC-SHA256:TLS-DHE-RSA-WITH-AES-128-CBC-SHA256'''

install_client_openvpn(client_name=client_name, client_conf=config_client)
print('client done')
