from openvpn.functions import CommandExecutionError, connect_ssh, execute_list_commands_without_arguments


def install_server_openvpn(server_name, ca_name, server_conf, cert_method):
    """Function to install an openvpn server in system using easyrsa package to generate keys and certificates"""
    ssh = connect_ssh()
    commands_list_without_arguments = [f'rm -f /etc/openvpn/server/server_{server_name}.conf',
                                       f'''echo '{server_conf.strip()}' >>/etc/openvpn/server/server_{server_name}.conf''',
                                       'chown -R openvpn:network /etc/openvpn/*',
                                       f'chown -R openvpn:openvpn /etc/certificates_{ca_name}/*',
                                    #    f'chown -R openvpn:network {current_dir}/*',
                                       'mkdir -p /var/log/openvpn/',
                                       'touch /var/log/openvpn/status.log',
                                       'sudo chown 777 /var/log/openvpn/status.log',
                                       ]
    if cert_method["method_name"] == 'shared_key':
        shared_key = f'''-----BEGIN OpenVPN Static key V1-----\n{cert_method["shared_key"]}\n-----END OpenVPN Static key V1-----'''
        commands_list_without_arguments.append(f'''rm -f /etc/openvpn/server/static_{server_name}.key''')
        commands_list_without_arguments.append(f'''echo '{shared_key.strip()}' >>/etc/openvpn/server/static_{server_name}.key''')
    elif cert_method["method_name"] == 'shared_key_auto':
        commands_list_without_arguments.append(f'''openvpn --genkey secret /etc/openvpn/server/static_{server_name}.key''')
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def delete_server_openvpn(server_name):
    """Function to delete an openvpn server in system and his keys and certificates"""
    ssh = connect_ssh()
    commands_list_without_arguments = [f'sudo systemctl stop openvpn-server@server_{server_name}',
                                       f'sudo rm -f /etc/openvpn/server/server_{server_name}.conf',
                                       f'sudo rm -f /etc/openvpn/server/static_{server_name}.key',
                                       f'sudo rm -f /var/log/openvpn/status-server_{server_name}.log',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def update_server_openvpn(server_name, server_conf, cert_method):
    """Function to update an openvpn server in system"""
    ssh = connect_ssh()
    commands_list_without_arguments = [f'rm /etc/openvpn/server/server_{server_name}.conf',
                                       f'''echo '{server_conf.strip()}' >>/etc/openvpn/server/server_{server_name}.conf''']
    if cert_method["method_name"] == 'shared_key':
        shared_key = f'''-----BEGIN OpenVPN Static key V1-----\n{cert_method["shared_key"]}\n-----END OpenVPN Static key V1-----'''
        commands_list_without_arguments.append(f'''rm -f /etc/openvpn/server/static_{server_name}.key''')
        commands_list_without_arguments.append(f'''echo '{shared_key.strip()}' >>/etc/openvpn/server/static_{server_name}.key''')
    elif cert_method["method_name"] == 'shared_key_auto':
        commands_list_without_arguments.append(f'''openvpn --genkey secret /etc/openvpn/server/static_{server_name}.key''')
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)
