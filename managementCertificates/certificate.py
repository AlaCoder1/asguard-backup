from managementCertificates.functions import change_vars, download_certificate, get_certifcate_serial_number, initialize_ca, read_certificate_value, revoke_list_certs
from openvpn.functions import execute_command_with_arguments, execute_command_without_arguments, execute_list_commands_without_arguments, get_current_directory


################ Authority ####################
def create_ca_in_system(ca_name, common_name, updated_fields_vars):
    """Function to create in system an authority certificate"""
    current_dir = get_current_directory()

    execute_command_with_arguments(['sudo', 'easyrsa', 'init-pki'], 'yes\n')
    command = ['cp', '/etc/easy-rsa/vars', f'{current_dir}/pki/vars']
    execute_command_without_arguments(command)
    change_vars(current_dir, updated_fields_vars)
    time_sleep = 1.5
    if updated_fields_vars["KEY_SIZE"] >= 8192:
        time_sleep += 12
    elif updated_fields_vars["KEY_SIZE"] > 2048:
        time_sleep += 2
    execute_command_with_arguments(['sudo', 'easyrsa', 'build-ca', 'nopass'], f'{common_name}\n', time_sleep)
    commands_list_without_arguments = [['mkdir', '-p', f'/etc/certificates_{ca_name}/'],
                                       ['cp', f'{current_dir}/pki/vars', f'/etc/certificates_{ca_name}/vars'],
                                       ['cp', f'{current_dir}/pki/ca.crt', f'/etc/certificates_{ca_name}/ca.crt'],
                                       ['cp', f'{current_dir}/pki/private/ca.key', f'/etc/certificates_{ca_name}/ca.key'],
                                       ['sudo', 'easyrsa', 'gen-crl'],
                                       ['cp', f'{current_dir}/pki/crl.pem', f'/etc/certificates_{ca_name}/crl.pem'],
                                    #    'chown -R openvpn:network /etc/openvpn/*',
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)

    serial = get_certifcate_serial_number(f"/etc/certificates_{ca_name}/ca.crt")

    return serial


def import_ca_in_system(ca_name, input_fields):
    current_dir = get_current_directory()
    initialize_ca(current_dir, ca_name)
    ca_data = '-----BEGIN CERTIFICATE-----\n' + input_fields["certificate_data"] + '\n-----END CERTIFICATE-----'
    ca_private_key = '-----BEGIN PRIVATE KEY-----\n' + input_fields["certificate_private_key"] + '\n-----END PRIVATE KEY-----'
    commands_list_without_arguments = [['mkdir', f'-p /etc/certificates_{ca_name}/'],
                                       ['echo', f'"{ca_data.strip()}"', '|', f'sudo tee /etc/certificates_{ca_name}/ca.crt'],
                                       ['echo', f'"{ca_private_key.strip()}"', '|', f'sudo tee /etc/certificates_{ca_name}/ca.key'],
                                       ['cp', f'/etc/certificates_{ca_name}/ca.crt', f'{current_dir}/pki/ca.crt'],
                                       ['cp', f'/etc/certificates_{ca_name}/ca.key', f'{current_dir}/pki/private/ca.key'],
                                       ['cp', f'{current_dir}/pki/vars', f'/etc/certificates_{ca_name}/vars/'],
                                       ['sudo', 'easyrsa gen-crl'],
                                       ['cp', f'{current_dir}/pki/crl.pem', f'/etc/certificates_{ca_name}/crl.pem'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)

    serial = get_certifcate_serial_number(f"/etc/certificates_{ca_name}/ca.crt")

    return serial


def delete_ca_in_system(ca_name):
    """Function to delete a ca in system"""
    current_dir = get_current_directory()
    commands_list_without_arguments = [['sudo', 'rm', '-rf', f'/etc/certificates_{ca_name}'],
                                       ['sudo', 'rm', '-f', f'{current_dir}/pki/ca.crt'],
                                       ['sudo', 'rm', '-f', f'{current_dir}/pki/private/ca.key'],]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def export_ca_in_system(ca_path, download_ca_path):
    """Export a CA certificate from system"""
    ca_value = read_certificate_value(ca_path)
    download_certificate(download_ca_path, ca_value)


def export_ca_list_rev_in_system(ca_name, download_cert_path):
    """Export a list of revocation of a CA certificate from system"""
    commands_list_without_arguments = [['cp', f'/etc/certificates_{ca_name}/crl.pem', f'/etc/certificates_{ca_name}/crl_copy.pem'],
                                       ['mv', f'/etc/certificates_{ca_name}/crl_copy.pem', f'/etc/certificates_{ca_name}/crl.crl'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    ca_value = read_certificate_value(f'/etc/certificates_{ca_name}/crl.crl')
    download_certificate(download_cert_path, ca_value)


################ Certificate ####################
def create_certificate_in_system(cert_name, common_name, ca_name, type_cert, updated_fields_vars):
    """Function to create in system an authority certificate"""
    current_dir = get_current_directory()
    
    # Initialize the openvpn and easyrsa
    initialize_ca(current_dir, ca_name)

    change_vars(current_dir, updated_fields_vars)
    time_sleep = 1
    if updated_fields_vars["KEY_SIZE"] >= 8192:
        time_sleep += 20
    elif updated_fields_vars["KEY_SIZE"] > 2048:
        time_sleep += 2
    # Creating Certificates (server or client)
    if type_cert == 'server':
        # Create certificate without password
        execute_command_with_arguments(['sudo', 'easyrsa', 'build-server-full', common_name, 'nopass'], 'yes\n', time_sleep)

        # Create certificate with password
        # execute_command_with_arguments(['sudo', 'easyrsa', 'build-server-full', 'common_name'], 'akrampass\nakrampass\nyes', time_sleep)

        commands_list_without_arguments = [['mkdir', '-p', f'/etc/openvpn/certificates_{cert_name}/'],
                                           ['cp', f'{current_dir}/pki/vars', f'/etc/openvpn/certificates_{cert_name}/vars'],
                                           ['cp', f'{current_dir}/pki/issued/{common_name}.crt', f'/etc/openvpn/certificates_{cert_name}/server.crt'],
                                           ['cp', f'{current_dir}/pki/private/{common_name}.key', f'/etc/openvpn/certificates_{cert_name}/server.key'],
                                           ]
        execute_list_commands_without_arguments(commands_list_without_arguments)

        serial = get_certifcate_serial_number(f"/etc/openvpn/certificates_{cert_name}/server.crt")

    elif type_cert == 'client':
        # Create client without password
        execute_command_with_arguments(['sudo', 'easyrsa', 'build-client-full', f'{cert_name}', 'nopass'], 'yes\n', time_sleep)

        # Create client with password
        # execute_command_with_arguments(['sudo', 'easyrsa', 'build-client-full', f'{cert_name}'], 'clientpass\nclientpass\nyes', time_sleep)
        
        commands_list_without_arguments = [['mkdir', '-p', f'/etc/openvpn/client/certificates_{cert_name}/'],
                                           ['cp', f'{current_dir}/pki/vars', 
                                            f'/etc/openvpn/client/certificates_{cert_name}/vars'],
                                           ['cp', f'{current_dir}/pki/issued/{cert_name}.crt', 
                                            f'/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt'],
                                           ['cp', f'{current_dir}/pki/private/{cert_name}.key', 
                                            f'/etc/openvpn/client/certificates_{cert_name}/{cert_name}.key'],
                                           ]
        execute_list_commands_without_arguments(commands_list_without_arguments)
        
        serial = get_certifcate_serial_number(f"/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt")

    return serial


def import_certificate_in_system(cert_name, cert_type, input_fields):
    """Function to import in system an authority certificate"""
    cert_data = '-----BEGIN CERTIFICATE-----\n' + input_fields["certificate_data"] + '\n-----END CERTIFICATE-----'
    cert_private_key = '-----BEGIN ENCRYPTED PRIVATE KEY-----\n' + input_fields["certificate_private_key"] + '\n-----END ENCRYPTED PRIVATE KEY-----'
    if cert_type == 'server':
        commands_list_without_arguments = [['mkdir', '-p', f'/etc/openvpn/certificates_{cert_name}/'],
                                           ['echo', cert_data.strip(), '|', 'sudo', 'tee', f'/etc/openvpn/certificates_{cert_name}/server.crt'],
                                           ['echo', cert_private_key.strip(), '|', 'sudo', 'tee', f'/etc/openvpn/certificates_{cert_name}/server.key'],
                                           ]
        execute_list_commands_without_arguments(commands_list_without_arguments)

        serial = get_certifcate_serial_number(f"/etc/openvpn/certificates_{cert_name}/server.crt")
    elif cert_type == 'client':
        commands_list_without_arguments = [['mkdir', '-p', f'/etc/openvpn/client/certificates_{cert_name}/'],
                                           ['echo', cert_data.strip(), '|', 'sudo', 'tee', f'/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt'],
                                           ['echo', cert_private_key.strip(), '|', 'sudo', 'tee', f'/etc/openvpn/client/certificates_{cert_name}/{cert_name}.key'],
                                        ]
        execute_list_commands_without_arguments(commands_list_without_arguments)

        serial = get_certifcate_serial_number(f"/etc/openvpn/certificates_{cert_name}/server.crt")
    
    return serial


def delete_certificate_in_system(cert_name, type_cert):
    """Function to delete a certificate in system"""
    current_dir = get_current_directory()

    if type_cert == 'server':
        commands_list_without_arguments = [['sudo', 'rm', '-rf', f'/etc/openvpn/certificates_{cert_name}'],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/issued/server.crt'],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/private/server.key'],
                                        #    f'sudo rm -f {current_dir}/pki/dh.pem',
                                           ]
    elif type_cert == 'client':
        commands_list_without_arguments = [['sudo', 'rm', '-rf', f'/etc/openvpn/client/certificates_{cert_name}'],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/issued/{cert_name}.crt'],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/private/{cert_name}.key'],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/reqs/{cert_name}.req'],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/inline/{cert_name}.inline'],]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def revoke_certificates_in_system(ca_name, cert, list_revoked_cert):
    """Revokate a list of certificates and update the crl of the authority"""
    current_dir = get_current_directory()

    # Initialization the CA
    initialize_ca(current_dir, ca_name)

    # Revoking certificates
    revoke_list_certs(current_dir, ca_name, list_revoked_cert)
    command = ['cp', f'{current_dir}/pki/revoked/certs_by_serial/{cert.serial}.crt',
               f'/etc/certificates_{ca_name}/{cert.serial}.crt']
    execute_command_without_arguments(command)
    

def unrevoke_certificates_in_system(ca_name, cert, list_revoked_cert):
    """Revokate a list of certificates and update the crl of the authority"""
    current_dir = get_current_directory()

    # Initialization the CA
    initialize_ca(current_dir, ca_name)

    # Revoking certificates
    revoke_list_certs(current_dir, ca_name, list_revoked_cert)
    
    command = ['rm', '-f', f'/etc/certificates_{ca_name}/{cert.serial}.crt']
    execute_command_without_arguments(command)


def export_certificate_in_system(cert_name, cert_type, download_cert_path, download_type, password='', confirm_password=''):
    """Export a certificate from system"""
    # configure certificate path: Server or Client
    if cert_type == 'server':
        cert_path = f'/etc/openvpn/certificates_{cert_name}/server.crt'
    else:
        cert_path = f'/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt'
    
    if download_type == 'certificate':
        cert_value = read_certificate_value(cert_path)
        download_certificate(download_cert_path, cert_value)
    elif download_type == 'private_key':
        cert_value = read_certificate_value(cert_path.replace('.crt', '.key'))
        download_certificate(download_cert_path, cert_value)
    else:  # .p12 file
        process = execute_command_without_arguments(["openssl", "pkcs12", "-export", "-out", f"{cert_path.replace('.crt', '.p12')}",
                                                     "-inkey", f"{cert_path.replace('.crt', '.key')}", "-in", f"{cert_path}",
                                                     "-passout", f'pass:{password}'])
        cert_value = read_certificate_value(cert_path.replace('.crt', '.p12'), decode=False)
        download_certificate(download_cert_path, cert_value, 'wb')
