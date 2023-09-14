from openvpn.functions import connect_ssh, execute_command_with_arguments, execute_list_commands_without_arguments


################ Authority ####################
def create_ca_in_system(ca_name, updated_fields_vars):
    """Function to create in system an authority certificate"""
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]
    execute_command_with_arguments(ssh, 'sudo easyrsa init-pki', ['yes', 'yes'])
    change_vars(ssh, current_dir, updated_fields_vars)
    time_sleep = 1.5
    if updated_fields_vars["KEY_SIZE"] >= 8192:
        time_sleep += 12
    elif updated_fields_vars["KEY_SIZE"] > 2048:
        time_sleep += 2
    execute_command_with_arguments(ssh, 'sudo easyrsa build-ca nopass', [f'{ca_name}'], time_sleep)
    commands_list_without_arguments = [f'mkdir -p /etc/certificates_{ca_name}/',
                                       f'cp {current_dir}/pki/vars "/etc/certificates_{ca_name}/vars"',
                                       f'cp {current_dir}/pki/ca.crt "/etc/certificates_{ca_name}/ca.crt"',
                                       f'cp {current_dir}/pki/private/ca.key "/etc/certificates_{ca_name}/ca.key"',
                                    #    'chown -R openvpn:network /etc/openvpn/*',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def import_ca_in_system(ca_name, input_fields):
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]
    ca_data = '-----BEGIN CERTIFICATE-----\n' + input_fields["certificate_data"] + '\n-----END CERTIFICATE-----'
    ca_private_key = '-----BEGIN PRIVATE KEY-----\n' + input_fields["certificate_private_key"] + '\n-----END PRIVATE KEY-----'
    commands_list_without_arguments = [f'mkdir -p /etc/certificates_{ca_name}/',
                                       f'echo "{ca_data.strip()}" | sudo tee /etc/certificates_{ca_name}/ca.crt',
                                       f'echo "{ca_private_key.strip()}" | sudo tee /etc/certificates_{ca_name}/ca.key',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def delete_ca_in_system(ca_name):
    """Function to delete a ca in system"""
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]
    commands_list_without_arguments = [f'sudo rm -r /etc/certificates_{ca_name}',
                                       f'sudo rm -f {current_dir}/pki/ca.crt',
                                       f'sudo rm -f {current_dir}/pki/private/ca.key',]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


################ Certificate ####################
def create_certificate_in_system(cert_name, ca_name, type_cert, updated_fields_vars):
    """Function to create in system an authority certificate"""
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]
    
    # Initialisation of the easyrsa
    execute_command_with_arguments(ssh, 'sudo easyrsa init-pki', ['yes', 'yes'])
    change_vars(ssh, current_dir, updated_fields_vars)
    time_sleep = 1
    if updated_fields_vars["KEY_SIZE"] >= 8192:
        time_sleep += 12
    elif updated_fields_vars["KEY_SIZE"] > 2048:
        time_sleep += 2
    execute_command_with_arguments(ssh, 'sudo easyrsa build-ca nopass', [f'{ca_name}'], time_sleep)

    # Importing the data of the Authority
    commands_list_without_arguments = [f'mkdir -p {current_dir}/pki/',
                                       f'mkdir -p {current_dir}/pki/private/',
                                       f'cp /etc/certificates_{ca_name}/ca.crt "{current_dir}/pki/ca.crt"',
                                       f'cp /etc/certificates_{ca_name}/ca.key "{current_dir}/pki/private/ca.key"',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)

    # Creating Certificates (server or client)
    if type_cert == 'server':
        # Create certificate without password
        execute_command_with_arguments(ssh, 'sudo easyrsa build-server-full server nopass', ['yes'], time_sleep)

        # Create certificate with password
        # execute_command_with_arguments(ssh, 'sudo easyrsa build-server-full server nopass', ['akrampass','akrampass','yes'], time_sleep)

        commands_list_without_arguments = ['sudo easyrsa gen-dh',
                                           f'mkdir -p /etc/openvpn/certificates_{cert_name}/',
                                           f'cp {current_dir}/pki/issued/server.crt "/etc/openvpn/certificates_{cert_name}/server.crt"',
                                           f'cp {current_dir}/pki/private/server.key "/etc/openvpn/certificates_{cert_name}/server.key"',
                                           f'cp {current_dir}/pki/dh.pem "/etc/openvpn/certificates_{cert_name}/dh.pem"',
                                           ]
    elif type_cert == 'client':
        # Create client without password
        execute_command_with_arguments(ssh, f'sudo easyrsa build-client-full {cert_name} nopass', ['yes'], time_sleep)

        # Create client with password
        # execute_command_with_arguments(ssh, f'sudo easyrsa build-client-full {cert_name}', ['clientpass', 'clientpass', 'yes'], time_sleep)
        
        commands_list_without_arguments = [f'mkdir -p /etc/openvpn/client/certificates_{cert_name}/',
                                           f'cp {current_dir}/pki/issued/{cert_name}.crt "/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt"',
                                           f'cp {current_dir}/pki/private/{cert_name}.key "/etc/openvpn/client/certificates_{cert_name}/{cert_name}.key"',
                                           ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def import_certificate_in_system(cert_name, cert_type, input_fields):
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]
    cert_data = '-----BEGIN CERTIFICATE-----\n' + input_fields["certificate_data"] + '\n-----END CERTIFICATE-----'
    cert_private_key = '-----BEGIN ENCRYPTED PRIVATE KEY-----\n' + input_fields["certificate_private_key"] + '\n-----END ENCRYPTED PRIVATE KEY-----'
    if cert_type == 'server':
        commands_list_without_arguments = [f'mkdir -p /etc/openvpn/certificates_{cert_name}/',
                                           f'echo "{cert_data.strip()}" | sudo tee /etc/openvpn/certificates_{cert_name}/server.crt',
                                           f'echo "{cert_private_key.strip()}" | sudo tee /etc/openvpn/certificates_{cert_name}/server.key',
                                           ]
    elif cert_type == 'client':
        commands_list_without_arguments = [f'mkdir -p /etc/openvpn/client/certificates_{cert_name}/',
                                           f'echo "{cert_data.strip()}" | sudo tee /etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt',
                                           f'echo "{cert_private_key.strip()}" | sudo tee /etc/openvpn/client/certificates_{cert_name}/{cert_name}.key',
                                        ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def delete_certificate_in_system(cert_name, type_cert):
    """Function to delete a certificate in system"""
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command('pwd')
    current_dir = stdout.read().decode('utf-8')
    current_dir = current_dir[:len(current_dir)-1]

    if type_cert == 'server':
        commands_list_without_arguments = [f'sudo rm -r /etc/openvpn/certificates_{cert_name}',
                                           f'sudo rm -f {current_dir}/pki/issued/server.crt',
                                           f'sudo rm -f {current_dir}/pki/private/server.key',
                                           f'sudo rm -f {current_dir}/pki/dh.pem',]
    elif type_cert == 'client':
        commands_list_without_arguments = [f'sudo rm -r /etc/openvpn/client/certificates_{cert_name}',
                                           f'sudo rm -f {current_dir}/pki/issued/{cert_name}.crt',
                                           f'sudo rm -f {current_dir}/pki/private/{cert_name}.key',
                                           f'sudo rm -f {current_dir}/pki/reqs/{cert_name}.req',
                                           f'sudo rm -f {current_dir}/pki/inline/{cert_name}.inline',]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def read_certificate_value(certificate_path):
    """This function take a certificate path and return the certificate value rfom system file"""
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command(f'cat {certificate_path}')
    ca_value = stdout.read().decode('utf-8')
    return ca_value


def change_vars(ssh, current_dir, updated_field:dict):
    vars_content = ssh.exec_command(f"cat {current_dir}/pki/vars")
    vars_content = vars_content[1].read().decode('utf-8')
    for field in updated_field.items():
        if vars_content.find(f'set_var EASYRSA_{field[0]}\t') > -1:
            old_value = vars_content[vars_content.find(f'set_var EASYRSA_{field[0]}\t'):vars_content.find('\n', vars_content.find(f'set_var EASYRSA_{field[0]}\t'))]
            if vars_content[vars_content.find(f'set_var EASYRSA_{field[0]}')-1] == '#':
                old_value = '#' + old_value
            vars_content = vars_content.replace(old_value, f'set_var EASYRSA_{field[0]}\t{field[1]}')
            new_value = vars_content[vars_content.find(f'set_var EASYRSA_{field[0]}\t'):vars_content.find('\n', vars_content.find(f'set_var EASYRSA_{field[0]}\t'))]
        else:
            vars_content += f'\nset_var EASYRSA_{field[0]}\t{field[1]}'
    ssh.exec_command(f'''echo '{vars_content.strip()}' | sudo tee {current_dir}/pki/vars''')

    return vars_content

