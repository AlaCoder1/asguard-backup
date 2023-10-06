from managementCertificates.functions import change_vars, download_certificate, get_certifcate_serial_number, initialize_ca, read_certificate_value, revoke_list_certs
from openvpn.functions import connect_ssh, execute_command_with_arguments, execute_list_commands_without_arguments, execute_list_of_commands


################ Authority ####################
def create_ca_in_system(ca_name, updated_fields_vars):
    """Function to create in system an authority certificate"""
    ssh, current_dir = connect_ssh()
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
                                       'sudo easyrsa gen-crl',
                                       f'cp {current_dir}/pki/crl.pem "/etc/certificates_{ca_name}/crl.pem"',
                                    #    'chown -R openvpn:network /etc/openvpn/*',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)

    serial = get_certifcate_serial_number(ssh, f"/etc/certificates_{ca_name}/ca.crt")

    return serial


def import_ca_in_system(ca_name, input_fields):
    ssh, current_dir = connect_ssh()
    initialize_ca(ssh, current_dir, ca_name)
    ca_data = '-----BEGIN CERTIFICATE-----\n' + input_fields["certificate_data"] + '\n-----END CERTIFICATE-----'
    ca_private_key = '-----BEGIN PRIVATE KEY-----\n' + input_fields["certificate_private_key"] + '\n-----END PRIVATE KEY-----'
    commands_list_without_arguments = [f'mkdir -p /etc/certificates_{ca_name}/',
                                       f'echo "{ca_data.strip()}" | sudo tee /etc/certificates_{ca_name}/ca.crt',
                                       f'echo "{ca_private_key.strip()}" | sudo tee /etc/certificates_{ca_name}/ca.key',
                                       f'cp /etc/certificates_{ca_name}/ca.crt "{current_dir}/pki/ca.crt"'
                                       f'cp /etc/certificates_{ca_name}/ca.key "{current_dir}/pki/private/ca.key"'
                                       f'cp {current_dir}/pki/vars "/etc/certificates_{ca_name}/vars/',
                                       'sudo easyrsa gen-crl',
                                       f'cp {current_dir}/pki/crl.pem "/etc/certificates_{ca_name}/crl.pem"',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)

    serial = get_certifcate_serial_number(ssh, f"/etc/certificates_{ca_name}/ca.crt")

    return serial


def delete_ca_in_system(ca_name):
    """Function to delete a ca in system"""
    ssh, current_dir = connect_ssh()
    commands_list_without_arguments = [f'sudo rm -r /etc/certificates_{ca_name}',
                                       f'sudo rm -f {current_dir}/pki/ca.crt',
                                       f'sudo rm -f {current_dir}/pki/private/ca.key',]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def export_ca_in_system(ca_path, download_ca_path):
    """Export a CA certificate from system"""
    ssh, current_dir = connect_ssh()
    ca_value = read_certificate_value(ssh, ca_path)
    download_certificate(download_ca_path, ca_value)


def export_ca_list_rev_in_system(ca_name, download_cert_path):
    """Export a list of revocation of a CA certificate from system"""
    ssh, current_dir = connect_ssh()
    commands_list_without_arguments = [f'cp /etc/certificates_{ca_name}/crl.pem "/etc/certificates_{ca_name}/crl_copy.pem"',
                                       f'mv /etc/certificates_{ca_name}/crl_copy.pem "/etc/certificates_{ca_name}/crl.crl"',
                                       ]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)
    ca_value = read_certificate_value(ssh, f'"/etc/certificates_{ca_name}/crl.crl"')
    download_certificate(download_cert_path, ca_value)


################ Certificate ####################
def create_certificate_in_system(cert_name, ca_name, type_cert, updated_fields_vars):
    """Function to create in system an authority certificate"""
    ssh, current_dir = connect_ssh()
    
    # Initialize the openvpn and easyrsa
    initialize_ca(ssh, current_dir, ca_name)

    change_vars(ssh, current_dir, updated_fields_vars)
    time_sleep = 1
    if updated_fields_vars["KEY_SIZE"] >= 8192:
        time_sleep += 20
    elif updated_fields_vars["KEY_SIZE"] > 2048:
        time_sleep += 2
    # Creating Certificates (server or client)
    if type_cert == 'server':
        # Create certificate without password
        execute_command_with_arguments(ssh, 'sudo easyrsa build-server-full server nopass', ['yes'], time_sleep)

        # Create certificate with password
        # execute_command_with_arguments(ssh, 'sudo easyrsa build-server-full server nopass', ['akrampass','akrampass','yes'], time_sleep)

        commands_list_without_arguments = [f'mkdir -p /etc/openvpn/certificates_{cert_name}/',
                                           f'cp {current_dir}/pki/vars "/etc/openvpn/certificates_{cert_name}/vars"',
                                           f'cp {current_dir}/pki/issued/server.crt "/etc/openvpn/certificates_{cert_name}/server.crt"',
                                           f'cp {current_dir}/pki/private/server.key "/etc/openvpn/certificates_{cert_name}/server.key"',
                                        #    'sudo easyrsa gen-dh',
                                        #    f'cp {current_dir}/pki/dh.pem "/etc/openvpn/certificates_{cert_name}/dh.pem"',
                                           ]
        execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)

        serial = get_certifcate_serial_number(ssh, f"/etc/openvpn/certificates_{cert_name}/server.crt")

    elif type_cert == 'client':
        # Create client without password
        execute_command_with_arguments(ssh, f'sudo easyrsa build-client-full {cert_name} nopass', ['yes'], time_sleep)

        # Create client with password
        # execute_command_with_arguments(ssh, f'sudo easyrsa build-client-full {cert_name}', ['clientpass', 'clientpass', 'yes'], time_sleep)
        
        commands_list_without_arguments = [f'mkdir -p /etc/openvpn/client/certificates_{cert_name}/',
                                           f'cp {current_dir}/pki/vars "/etc/openvpn/client/certificates_{cert_name}/vars"',
                                           f'cp {current_dir}/pki/issued/{cert_name}.crt "/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt"',
                                           f'cp {current_dir}/pki/private/{cert_name}.key "/etc/openvpn/client/certificates_{cert_name}/{cert_name}.key"',
                                           ]
        execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)
        
        serial = get_certifcate_serial_number(ssh, f"/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt")

    return serial


def import_certificate_in_system(cert_name, cert_type, input_fields):
    ssh, current_dir = connect_ssh()
    cert_data = '-----BEGIN CERTIFICATE-----\n' + input_fields["certificate_data"] + '\n-----END CERTIFICATE-----'
    cert_private_key = '-----BEGIN ENCRYPTED PRIVATE KEY-----\n' + input_fields["certificate_private_key"] + '\n-----END ENCRYPTED PRIVATE KEY-----'
    if cert_type == 'server':
        commands_list_without_arguments = [f'mkdir -p /etc/openvpn/certificates_{cert_name}/',
                                           f'echo "{cert_data.strip()}" | sudo tee /etc/openvpn/certificates_{cert_name}/server.crt',
                                           f'echo "{cert_private_key.strip()}" | sudo tee /etc/openvpn/certificates_{cert_name}/server.key',
                                           ]
        execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)

        serial = get_certifcate_serial_number(ssh, f"/etc/openvpn/certificates_{cert_name}/server.crt")
    elif cert_type == 'client':
        commands_list_without_arguments = [f'mkdir -p /etc/openvpn/client/certificates_{cert_name}/',
                                           f'echo "{cert_data.strip()}" | sudo tee /etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt',
                                           f'echo "{cert_private_key.strip()}" | sudo tee /etc/openvpn/client/certificates_{cert_name}/{cert_name}.key',
                                        ]
        execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)

        serial = get_certifcate_serial_number(ssh, f"/etc/openvpn/certificates_{cert_name}/server.crt")
    
    return serial


def delete_certificate_in_system(cert_name, type_cert):
    """Function to delete a certificate in system"""
    ssh, current_dir = connect_ssh()

    if type_cert == 'server':
        commands_list_without_arguments = [f'sudo rm -r /etc/openvpn/certificates_{cert_name}',
                                           f'sudo rm -f {current_dir}/pki/issued/server.crt',
                                           f'sudo rm -f {current_dir}/pki/private/server.key',
                                        #    f'sudo rm -f {current_dir}/pki/dh.pem',
                                           ]
    elif type_cert == 'client':
        commands_list_without_arguments = [f'sudo rm -r /etc/openvpn/client/certificates_{cert_name}',
                                           f'sudo rm -f {current_dir}/pki/issued/{cert_name}.crt',
                                           f'sudo rm -f {current_dir}/pki/private/{cert_name}.key',
                                           f'sudo rm -f {current_dir}/pki/reqs/{cert_name}.req',
                                           f'sudo rm -f {current_dir}/pki/inline/{cert_name}.inline',]
    execute_list_commands_without_arguments(ssh_connect=ssh, commands_list=commands_list_without_arguments)


def revoke_certificates_in_system(ca_name, cert, list_revoked_cert):
    """Revokate a list of certificates and update the crl of the authority"""
    ssh, current_dir = connect_ssh()

    # Initialization the CA
    initialize_ca(ssh, current_dir, ca_name)

    # Revoking certificates
    revoke_list_certs(ssh, current_dir, ca_name, list_revoked_cert)
    print('cert.serial= ', cert.serial)
    ssh.exec_command(f'cp {current_dir}/pki/revoked/certs_by_serial/{cert.serial}.crt "/etc/certificates_{ca_name}/{cert.serial}.crt"')
    print(11111111111111111111)
    

def unrevoke_certificates_in_system(ca_name, cert, list_revoked_cert):
    """Revokate a list of certificates and update the crl of the authority"""
    ssh, current_dir = connect_ssh()

    # Initialization the CA
    initialize_ca(ssh, current_dir, ca_name)

    # Revoking certificates
    revoke_list_certs(ssh, current_dir, ca_name, list_revoked_cert)
    
    ssh.exec_command(f'rm -f /etc/certificates_{ca_name}/{cert.serial}.crt')


def export_certificate_in_system(cert_name, cert_type, download_cert_path, download_type, password='', confirm_password=''):
    """Export a certificate from system"""
    ssh, current_dir = connect_ssh()

    # configure certificate path: Server or Client
    if cert_type == 'server':
        cert_path = f'/etc/openvpn/certificates_{cert_name}/server.crt'
    else:
        cert_path = f'/etc/openvpn/client/certificates_{cert_name}/{cert_name}.crt'
    
    if download_type == 'certificate':
        cert_value = read_certificate_value(ssh, cert_path)
        download_certificate(download_cert_path, cert_value)
    elif download_type == 'private_key':
        cert_value = read_certificate_value(ssh, cert_path.replace('.crt', '.key'))
        download_certificate(download_cert_path, cert_value)
    else:  # .p12 file
        execute_command_with_arguments(ssh_connect=ssh, 
                                       command=f"openssl pkcs12 -export -out {cert_path.replace('.crt', '.p12')} -inkey {cert_path.replace('.crt', '.key')} -in {cert_path}",
                                       arguments=[password, confirm_password])
        cert_value = read_certificate_value(ssh, cert_path.replace('.crt', '.p12'), decode=False)
        download_certificate(download_cert_path, cert_value, 'wb')
