from datetime import datetime
from openvpn.functions import CommandExecutionError, connect_ssh, create_tls_file, execute_command_with_arguments, execute_list_commands_without_arguments


def install_server_openvpn(server_name, ca_name, dh_length, tls_auth, server_conf):
    """Function to install an openvpn server in system using easyrsa package to generate keys and certificates"""
    ssh, current_dir = connect_ssh()
    
    create_tls_file(ssh, tls_auth, f'/etc/openvpn/server/static_{server_name}.key')

    execute_command_with_arguments(ssh, 'sudo easyrsa init-pki', ['yes', 'yes'])
    commands_list_without_arguments = [f'sudo easyrsa gen-dh {dh_length}',
                                       f'cp {current_dir}/pki/dh.pem "/etc/openvpn/server/dh_{server_name}.pem"',
                                       f'rm -f /etc/openvpn/server/server_{server_name}.conf',
                                       f'''echo '{server_conf.strip()}' >>/etc/openvpn/server/server_{server_name}.conf''',
                                       'chown -R openvpn:network /etc/openvpn/*',
                                       f'chown -R openvpn:openvpn /etc/certificates_{ca_name}/*',
                                    #    f'chown -R openvpn:network {current_dir}/*',
                                       'mkdir -p /var/log/openvpn/',
                                       'touch /var/log/openvpn/status.log',
                                       'sudo chown 777 /var/log/openvpn/status.log',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def delete_server_openvpn(server_name):
    """Function to delete an openvpn server in system and his keys and certificates"""
    ssh, current_dir = connect_ssh()
    commands_list_without_arguments = [f'sudo systemctl stop openvpn-server@server_{server_name}',
                                       f'sudo rm -f /etc/openvpn/server/server_{server_name}.conf',
                                       f'sudo rm -f /etc/openvpn/server/dh_{server_name}.pem',
                                       f'sudo rm -f /etc/openvpn/server/static_{server_name}.key',
                                       f'sudo rm -f /var/log/openvpn/status-server_{server_name}.log',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def update_server_openvpn(server_name, dh_length, tls_auth, server_conf):
    """Function to update an openvpn server in system"""
    ssh, current_dir = connect_ssh()
    
    create_tls_file(ssh, tls_auth, f'/etc/openvpn/server/static_{server_name}.key')

    execute_command_with_arguments(ssh, 'sudo easyrsa init-pki', ['yes', 'yes'])
    commands_list_without_arguments = [f'sudo easyrsa gen-dh {dh_length}',
                                       f'rm /etc/openvpn/server/server_{server_name}.conf',
                                       f'''echo '{server_conf.strip()}' >>/etc/openvpn/server/server_{server_name}.conf''']
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)
