from openvpn.functions import connect_ssh

from openvpn.functions import execute_list_commands_without_arguments


def install_client_openvpn(client_name, client_conf):
    ssh = connect_ssh()
    execute_list_commands_without_arguments(
        ssh_connect=ssh, commands_list=[f'rm -f /etc/openvpn/client/client_{client_name}.ovpn',
                                        f'''echo '{client_conf.strip()}' >>/etc/openvpn/client/client_{client_name}.ovpn''',
                                        ])


def delete_client_openvpn(client_name):
    """Function to delete an openvpn client"""
    ssh = connect_ssh()
    commands_list_without_arguments = [f'sudo rm /etc/openvpn/client/client_{client_name}.ovpn']
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def update_client_openvpn(client_name, client_conf):
    """Function to update an openvpn client"""
    ssh = connect_ssh()
    commands_list_without_arguments = [f'rm /etc/openvpn/client/client_{client_name}.ovpn',
                                       f'''echo '{client_conf.strip()}' >>/etc/openvpn/client/client_{client_name}.ovpn''']
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


# server_name = 'azizserver'
# client_name = 'test3client'
# config_client = f'''client
# remote 10.1.12.9 1195
# proto udp
# dev tun
# nobind
# remote-cert-tls server
# cipher AES-256-CBC
# auth-nocache
# script-security 2
# persist-key
# persist-tun

# ca /etc/openvpn/certificates_{server_name}/ca.crt
# cert /etc/openvpn/client/certificates_{client_name}/{client_name}.crt
# key /etc/openvpn/client/certificates_{client_name}/{client_name}.key
# dh /etc/openvpn/certificates_{server_name}/dh.pem
# tls-version-min 1.2
# tls-cipher TLS-DHE-RSA-WITH-AES-256-GCM-SHA384:TLS-DHE-RSA-WITH-AES-128-GCM-SHA256:TLS-DHE-RSA-WITH-AES-256-CBC-SHA256:TLS-DHE-RSA-WITH-AES-128-CBC-SHA256'''

# install_client_openvpn(client_name=client_name, client_conf=config_client)
# print('client done')
