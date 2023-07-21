import paramiko
from authentification.views import *

def sudo(cmd):
    return "sudo "+cmd
# def connect_ssh():
#     sshh = paramiko.SSHClient()
#     sshh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     sshh.connect('10.1.12.107', username='root', password='root')
#     return sshh

def get_config_server(server_path):
    # ssh = connect_ssh()
    cmd = f"cat {server_path}"
    stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
    return stdin, stdout, stderr


# def show_config_server(server_path):
#     cmd = f"cat {server_path}"
#     stdin, stdout, stderr = ssh.exec_command((cmd))
#     lines = stdout.readlines()
#     print('server.conf\n-----------------------------')
#     print(lines)
#     return lines


def add_config_server(server_path, server_config):
    cmd = f"echo '{server_config.strip()}' | sudo tee {server_path}"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdin, stdout, stderr


def edit_lines_config_server(server_path, lines_to_update):
    stdin, stdout, stderr = get_config_server(server_path)
    server_conf_content = stdout.read().decode()

    updated_content = []
    for line in server_conf_content.splitlines():
        key_value = line.split(' ', 1)
        if len(key_value) == 2 and key_value[0] in lines_to_update:
            key = key_value[0]
            updated_line = f"{key} {lines_to_update[key]}"
            updated_content.append(updated_line)
        else:
            updated_content.append(line)

    # Write the updated server.conf content
    server_conf = '\n'.join(updated_content)
    add_config_server(server_path=server_path, server_config=server_conf)


def delete_lines_config_server(server_path, lines_to_delete):
    stdin, stdout, stderr = get_config_server(server_path)
    server_conf_content = stdout.read().decode()

    # Delete the desired lines
    updated_content = []
    for line in server_conf_content.splitlines():
        key_value = line.split(' ', 1)
        if not key_value[0] in lines_to_delete:
            updated_content.append(line)

    server_conf = '\n'.join(updated_content)
    add_config_server(server_path=server_path, server_config=server_conf)


def add_lines_config_server(server_path, lines_to_add:dict):
    stdin, stdout, stderr = get_config_server(server_path)
    server_conf_content = stdout.read().decode()
    updated_content = [line for line in server_conf_content.splitlines()]
    for line in lines_to_add.items():
        updated_content.insert(line[1][1], f"{line[0]} {line[1][0]}")

    # Write the updated server.conf content
    server_conf = '\n'.join(updated_content)
    add_config_server(server_path=server_path, server_config=server_conf)


# Update the desired options
# Modify the lines list as per your requirements


server_path = "/etc/openvpn/server.conf"

new_server_conf = """
port 1194
proto udp
dev tun
user baklouti
group gr1
persist-key
persist-tun
keepalive 10 120
topology subnet
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"
push "redirect-gateway def1 bypass-dhcp"
dh none
ecdh-curve prime256v1
tls-crypt tls-crypt.key
crl-verify crl.pem
ca ca.crt
cert server_TzOIvgMDkySTSkvC.crt
key server_TzOIvgMDkySTSkvC.key
auth SHA256
cipher AES-128-GCM
ncp-ciphers AES-128-GCM
tls-server
tls-version-min 1.2 """

updated_lines_server_conf = {'user': '',
                             'group': 'newgroup',
                             'port': 6000}

delete_lines_serve_conf = ['new1', 'new2', 'new3']

added_lines_server_conf = {'new1': ['new1', 0],
                           'new2': ['new2', 5],
                           'new3': ['new3', 7]}


# stdin, stdout, stderr = get_config_server(server_path)
# print(stdout.read().decode('utf-8'))
# stdin, stdout, stderr = get_config_server("/root/akrem.ovpn")
# print(stdout.read().decode('utf-8'))
# print('before changes')
# show_config_server(server_path=server_path)
# #add_lines_config_server(server_path=server_path, lines_to_add=added_lines_server_conf)
# #delete_lines_config_server(server_path=server_path, lines_to_delete=delete_lines_serve_conf)
# #edit_lines_config_server(server_path=server_path, lines_to_update=updated_lines_server_conf)
# #add_config_server(server_path=server_path, server_config=new_server_conf)
# print('\n\nAfter changes')
# show_config_server(server_path=server_path)
