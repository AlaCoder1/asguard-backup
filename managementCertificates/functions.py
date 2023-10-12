from openvpn.functions import connect_ssh, execute_command_with_arguments, execute_list_commands_without_arguments, execute_list_of_commands


def read_certificate_value(ssh, certificate_path, decode=True):
    """This function take a certificate path and return the certificate value rfom system file"""
    std = ssh.exec_command(f'cat {certificate_path}')
    if decode:
        return std[1].read().decode()
    return std[1].read()


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


def initialize_ca(ssh, current_dir, ca_name='test'):
    """This function initialize the openvpn and easyrsa in system"""

    # Creating a CA
    list_of_commands_with_arguments = [{'command': 'sudo easyrsa init-pki', 'arguments': ['yes', 'yes']},
                                       {'command': 'sudo easyrsa build-ca nopass', 'arguments': [f'{ca_name}']}]
    execute_list_of_commands(ssh, list_of_commands_with_arguments)

    #Importing an existing CA to the standard easyrsa path
    commands_list_without_arguments = [f'cp /etc/certificates_{ca_name}/ca.crt "{current_dir}/pki/ca.crt"',
                                       f'cp /etc/certificates_{ca_name}/ca.key "{current_dir}/pki/private/ca.key"',
                                       f'cp /etc/certificates_{ca_name}/vars "{current_dir}/pki/vars"',
                                       f'cp /etc/certificates_{ca_name}/crl.pem "{current_dir}/pki/crl.pem"',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def get_certifcate_serial_number(ssh, cert_path):
    """Get the serial number of certificate"""
    stdin, stdout, stderr = ssh.exec_command(f'openssl x509 -in {cert_path} -noout -serial')
    serial = stdout.read().decode('utf-8')
    serial = serial.replace('serial=', '')
    return serial


def revoke_list_certs(ssh, current_dir, ca_name, list_revoked_cert):
    """Revoking a list of certificates and generate the crl file"""

    for revoked_cert in list_revoked_cert:
        if revoked_cert.certificate_type == 'server':
            ssh.exec_command(f'cp /etc/openvpn/certificates_{revoked_cert.name}/server.crt "{current_dir}/pki/issued/server.crt"')
            execute_command_with_arguments(ssh, 'sudo easyrsa revoke server', ['yes'])
        elif revoked_cert.certificate_type == 'client':
            ssh.exec_command(f'cp /etc/openvpn/client/certificates_{revoked_cert.name}/{revoked_cert.name}.crt "{current_dir}/pki/issued/{revoked_cert.name}.crt"')
            execute_command_with_arguments(ssh, f'sudo easyrsa revoke {revoked_cert.name}', ['yes'])

    # Generate crl file containing all the revoked certificates
    commands_list_without_arguments = ['sudo easyrsa gen-crl',
                                       f'cp {current_dir}/pki/crl.pem "/etc/certificates_{ca_name}/crl.pem"',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def download_certificate(download_cert_path, cert_value, mode_open='w+'):
    """Download a certificate"""
    with open(download_cert_path, mode_open) as download_cert:
        download_cert.write(cert_value)
