from openvpn.functions import execute_command_with_arguments, execute_command_without_arguments, execute_list_commands_without_arguments, execute_list_commands_with_arguments


def read_certificate_value(certificate_path, decode=True):
    """This function take a certificate path and return the certificate value from system file"""
    command = ['cat', f'{certificate_path}']
    process = execute_command_without_arguments(command, decode)
    return process.stdout


def change_vars(current_dir, updated_field:dict):
    """This function takes some configurations of certificates and change vars file of the easyrsa"""

    # Get the vars file content
    with open(f'{current_dir}/pki/vars', 'r') as file:
        vars_content = file.read()

    for field in updated_field.items():
        # Find the input in vars file
        if vars_content.find(f'set_var EASYRSA_{field[0]}\t') > -1:
            # Get the input value before changing it
            start_index_old_value = vars_content.find(f'set_var EASYRSA_{field[0]}\t')
            end_index_old_value = vars_content.find('\n', start_index_old_value)
            if end_index_old_value > -1:
                old_value = vars_content[start_index_old_value:end_index_old_value]
            else:
                old_value = vars_content[start_index_old_value:]
            # Take in consideration the # because all the config in vars file are commented by default
            if vars_content[vars_content.find(f'set_var EASYRSA_{field[0]}')-1] == '#':
                old_value = '#' + old_value
            # Updating the vars file with the new input
            vars_content = vars_content.replace(old_value, f'set_var EASYRSA_{field[0]}\t{field[1]}')
        else:
            # Append the input in vars file
            vars_content += f'\nset_var EASYRSA_{field[0]}\t{field[1]}'

    with open(f'{current_dir}/pki/vars', 'w') as file:
        file.write(vars_content)

    return vars_content


def initialize_ca(current_dir, ca_name='test'):
    """This function initialize the openvpn and easyrsa in system"""

    # Initialize a fresh PKI and creating a CA
    list_of_commands_with_arguments = [{'command': ['sudo', 'easyrsa', 'init-pki'], 'arguments': 'yes\n'},
                                       {'command': ['sudo', 'easyrsa', 'build-ca', 'nopass'], 'arguments': f'{ca_name}\n'}]
    execute_list_commands_with_arguments(list_of_commands_with_arguments)

    #Importing an existing CA to the standard easyrsa path
    commands_list_without_arguments = [['cp', f'/etc/certificates_{ca_name}/ca.crt', f'{current_dir}/pki/ca.crt'],
                                       ['cp', f'/etc/certificates_{ca_name}/ca.key', f'{current_dir}/pki/private/ca.key'],
                                       ['cp', f'/etc/certificates_{ca_name}/vars', f'{current_dir}/pki/vars'],
                                       ['cp', f'/etc/certificates_{ca_name}/crl.pem', f'{current_dir}/pki/crl.pem'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def get_certifcate_serial_number(cert_path):
    """Get the serial number of certificate"""
    command = ['openssl', 'x509', '-in', f'{cert_path}', '-noout', '-serial']
    process = execute_command_without_arguments(command)
    serial = process.stdout
    serial = serial.replace('serial=', '')
    return serial


def revoke_list_certs(current_dir, ca_name, list_revoked_cert):
    """Revoking a list of certificates and generate the crl file"""

    for revoked_cert in list_revoked_cert:
        if revoked_cert.certificate_type == 'server':
            command =['cp', f'/etc/openvpn/certificates_{revoked_cert.name}/server.crt', 
                      f'{current_dir}/pki/issued/server.crt']
            execute_command_without_arguments(command)
            execute_command_with_arguments(['sudo', 'easyrsa', 'revoke', 'server'], 'yes\n')
        elif revoked_cert.certificate_type == 'client':
            command = ['cp', f'/etc/openvpn/client/certificates_{revoked_cert.name}/{revoked_cert.name}.crt',
                       f'{current_dir}/pki/issued/{revoked_cert.name}.crt']
            execute_command_without_arguments(command)
            execute_command_with_arguments(['sudo', 'easyrsa', 'revoke', f'{revoked_cert.name}'], 'yes\n')

    # Generate crl file containing all the revoked certificates
    commands_list_without_arguments = [['sudo', 'easyrsa', 'gen-crl'],
                                       ['cp', f'{current_dir}/pki/crl.pem', f'/etc/certificates_{ca_name}/crl.pem'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def download_certificate(download_cert_path, cert_value, mode_open='w+'):
    """Download a certificate"""
    with open(download_cert_path, mode_open) as download_cert:
        download_cert.write(cert_value)
