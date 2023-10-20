import shutil
from managementCertificates.functions import initialize_ca
from openvpn.functions import create_tls_file, execute_command_with_arguments, execute_list_commands_without_arguments, get_current_directory


def install_server_openvpn(server_name, ca_name, dh_length, tls_auth, server_conf:str):
    """Function to install an openvpn server in system using easyrsa package to generate keys and certificates"""
    current_dir = get_current_directory()
    
    # Initialization
    initialize_ca(current_dir, ca_name)
    create_tls_file(tls_auth, f'/etc/openvpn/server/static_{server_name}.key')
    
    with open(f'/etc/openvpn/server/server_{server_name}.conf', 'w') as server_file:
        server_file.write(server_conf)

    commands_list_without_arguments = [['sudo', 'easyrsa', 'gen-dh', f'{dh_length}'],
                                       ['cp', f'{current_dir}/pki/dh.pem', f'/etc/openvpn/server/dh_{server_name}.pem'],
                                       ['sudo', 'mkdir', '-p', '/var/log/openvpn/'],
                                       ['sudo', 'touch', '/var/log/openvpn/status.log'],
                                       ['sudo', 'sudo', 'chown', '777', '/var/log/openvpn/status.log'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)

    # Add permissions to use certificates and other files
    shutil.chown('/etc/openvpn/', user='openvpn', group='network')
    shutil.chown(f'/etc/certificates_{ca_name}/', user='openvpn', group='openvpn')
    commands_list_without_arguments = [['sudo', 'chown', '-R', 'openvpn:network', '/etc/openvpn/'],
                                       ['sudo', 'chown', '-R', 'openvpn:openvpn', f'/etc/certificates_{ca_name}/']
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def delete_server_openvpn(server_name):
    """Function to delete an openvpn server in system and his keys and certificates"""
    commands_list_without_arguments = [['sudo', 'systemctl', 'stop', f'openvpn-server@server_{server_name}'],
                                       ['sudo', 'rm', '-f', f'/etc/openvpn/server/server_{server_name}.conf'],
                                       ['sudo', 'rm', '-f', f'/etc/openvpn/server/dh_{server_name}.pem'],
                                       ['sudo', 'rm', '-f', f'/etc/openvpn/server/static_{server_name}.key'],
                                       ['sudo', 'rm', '-f', f'/var/log/openvpn/status-server_{server_name}.log'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def update_server_openvpn(server_name, dh_length, tls_auth, server_conf):
    """Function to update an openvpn server in system"""
    # current_dir = get_current_directory()
    
    # # Initialization
    # initialize_ca(current_dir)

    create_tls_file(tls_auth, f'/etc/openvpn/server/static_{server_name}.key')
    
    with open(f'/etc/openvpn/server/server_{server_name}.conf', 'w') as server_file:
        server_file.write(server_conf)

    if dh_length:
        commands_list_without_arguments = [['sudo', 'easyrsa', 'gen-dh', f'{dh_length}']]
        execute_list_commands_without_arguments(commands_list_without_arguments)
