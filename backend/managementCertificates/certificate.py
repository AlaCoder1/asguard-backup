from backend.managementCertificates.constant_variables import PATH_CA, PATH_CA_CRL, PATH_CA_CRL_PEM, PATH_CA_CRT, PATH_CA_KEY, PATH_CA_VARS, PATH_CLIENT_CERT, PATH_CLIENT_CERT_CRT, PATH_CLIENT_CERT_KEY, PATH_CLIENT_CERT_VARS, PATH_SERVER_CERT, PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY, PATH_SERVER_CERT_VARS, PATH_VARS_INITIALIZE
from backend.managementCertificates.utils import change_vars, initialize_ca, revoke_list_certs, save_certificate_in_text_format
from backend.managementCertificates.get_data_from_certificate import extract_certificate_distingushed_name, extract_type_certificate, get_certifcate_dates, get_certifcate_serial_number, read_certificate_value
from utils.commands_utils import get_current_directory
from utils.commands_utils import execute_command_with_arguments, execute_command_without_arguments, execute_list_commands_without_arguments


################ Authority ####################
def create_ca_in_system(ca_name, common_name, updated_fields_vars):
    """Function to create in system an authority certificate"""
    current_dir = get_current_directory()

    execute_command_with_arguments(['sudo', 'easyrsa', 'init-pki'], 'yes\n')
    command = ['cp', PATH_VARS_INITIALIZE, f'{current_dir}/pki/vars']
    execute_command_without_arguments(command)
    change_vars(current_dir, updated_fields_vars)
    time_sleep = 1.5
    if updated_fields_vars["KEY_SIZE"] >= 8192:
        time_sleep += 12
    elif updated_fields_vars["KEY_SIZE"] > 2048:
        time_sleep += 2
    execute_command_with_arguments(['sudo', 'easyrsa', 'build-ca', 'nopass'], f'{common_name}\n', time_sleep)
    save_certificate_in_text_format(f'{current_dir}/pki/ca.crt')
    commands_list_without_arguments = [['mkdir', '-p', PATH_CA.format(ca_name)],
                                       ['cp', f'{current_dir}/pki/vars', PATH_CA_VARS.format(ca_name)],
                                       ['cp', f'{current_dir}/pki/ca.crt', PATH_CA_CRT.format(ca_name)],
                                       ['cp', f'{current_dir}/pki/private/ca.key', PATH_CA_KEY.format(ca_name)],
                                       ['sudo', 'easyrsa', 'gen-crl'],
                                       ['cp', f'{current_dir}/pki/crl.pem', PATH_CA_CRL_PEM.format(ca_name)],
                                    #    'chown -R openvpn:network /etc/openvpn/*',
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)

    serial = get_certifcate_serial_number(PATH_CA_CRT.format(ca_name))

    return serial


def import_ca_in_system(ca_name, input_fields:dict):
    current_dir = get_current_directory()
    execute_command_with_arguments(['sudo', 'easyrsa', 'init-pki'], 'yes\n')
    execute_command_with_arguments(['sudo', 'easyrsa', 'build-ca', 'nopass'], f'{ca_name}\n')
    commands_list_without_arguments = [['cp', PATH_VARS_INITIALIZE, f'{current_dir}/pki/vars'],
                                       ['mkdir', '-p', PATH_CA.format(ca_name)],]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    with open(PATH_CA_CRT.format(ca_name), "w+") as ca_file:
        ca_file.write(input_fields["certificate_data"])
    with open(PATH_CA_KEY.format(ca_name), "w+") as ca_file:
        ca_file.write(input_fields["certificate_private_key"])
    save_certificate_in_text_format(PATH_CA_CRT.format(ca_name))
    
    serial = get_certifcate_serial_number(PATH_CA_CRT.format(ca_name))
    serial = serial[:len(serial)-1]
    
    start_date, end_date, lifetime = get_certifcate_dates(PATH_CA_CRT.format(ca_name))
    distingushed_name = extract_certificate_distingushed_name(PATH_CA_CRT.format(ca_name))
    
    commands_list_without_arguments = [['cp', PATH_CA_CRT.format(ca_name), f'{current_dir}/pki/ca.crt'],
                                       ['cp', PATH_CA_KEY.format(ca_name), f'{current_dir}/pki/private/ca.key'],
                                       ['cp', f'{current_dir}/pki/vars', PATH_CA_VARS.format(ca_name)],
                                       ['sudo', 'easyrsa', 'gen-crl'],
                                       ['cp', f'{current_dir}/pki/crl.pem', PATH_CA_CRL_PEM.format(ca_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)

    return serial, start_date, end_date, lifetime, distingushed_name


def delete_ca_in_system(ca_name):
    """Function to delete a ca in system"""
    current_dir = get_current_directory()
    commands_list_without_arguments = [['sudo', 'rm', '-rf', PATH_CA.format(ca_name)],
                                       ['sudo', 'rm', '-f', f'{current_dir}/pki/ca.crt'],
                                       ['sudo', 'rm', '-f', f'{current_dir}/pki/private/ca.key'],]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def export_ca_in_system(ca_path):
    """Export a CA certificate from system"""
    ca_value = read_certificate_value(ca_path)
    return ca_value


def export_ca_list_rev_in_system(ca_name):
    """Export a list of revocation of a CA certificate from system"""
    commands_list_without_arguments = [['cp', PATH_CA_CRL_PEM.format(ca_name), 
                                        PATH_CA_CRL_PEM.format(ca_name).replace("crl.pem", "crl_copy.pem")],
                                       ['mv', PATH_CA_CRL_PEM.format(ca_name).replace("crl.pem", "crl_copy.pem"), 
                                        PATH_CA_CRL.format(ca_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    ca_value = read_certificate_value(PATH_CA_CRL.format(ca_name))
    return ca_value


################ Certificate ####################
def create_certificate_in_system(cert_name, common_name, ca_name, cert_type, updated_fields_vars):
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
    
    cert_command = ['sudo', 'easyrsa', f'build-{cert_type}-full', common_name, 'nopass']
    execute_command_with_arguments(cert_command, 'yes\n', time_sleep)

    # Creating Certificates (server or client)
    cert_directory = PATH_SERVER_CERT.format(cert_name)
    cert_vars = PATH_SERVER_CERT_VARS.format(cert_name)
    cert_path = PATH_SERVER_CERT_CRT.format(cert_name)
    cert_private_key = PATH_SERVER_CERT_KEY.format(cert_name)
    if cert_type == 'client':
        cert_directory = PATH_CLIENT_CERT.format(cert_name)
        cert_vars = PATH_CLIENT_CERT_VARS.format(cert_name)
        cert_path = PATH_CLIENT_CERT_CRT.format(cert_name)
        cert_private_key = PATH_CLIENT_CERT_KEY.format(cert_name)

    commands_list_without_arguments = [['mkdir', '-p', cert_directory],
                                       ['cp', f'{current_dir}/pki/vars', cert_vars],
                                       ['cp', f'{current_dir}/pki/issued/{common_name}.crt', cert_path],
                                       ['cp', f'{current_dir}/pki/private/{common_name}.key', cert_private_key],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    
    serial = get_certifcate_serial_number(cert_path)

    return serial


def import_certificate_in_system(cert_name, input_fields):
    """Function to import in system an authority certificate"""
    current_dir = get_current_directory()
    execute_command_without_arguments(['cp', PATH_VARS_INITIALIZE, f'{current_dir}/pki/vars'])
    cert_path = f'{current_dir}/pki/issued/{cert_name}.crt'
    private_key_path = f'{current_dir}/pki/private/{cert_name}.key'
    with open(cert_path, "w+") as cert_file:
        cert_file.write(input_fields["certificate_data"])
    with open(private_key_path, "w+") as cert_file:
        cert_file.write(input_fields["certificate_private_key"])
    
    save_certificate_in_text_format(cert_path)
    
    # Get certificate config
    cert_type = extract_type_certificate(cert_path)

    serial = get_certifcate_serial_number(cert_path)
    serial = serial[:len(serial)-1]

    start_date, end_date, lifetime = get_certifcate_dates(cert_path)
    distingushed_name = extract_certificate_distingushed_name(cert_path)

    # Save certificate and its private key in system
    #Set certificate directory and path
    cert_directory = PATH_SERVER_CERT.format(cert_name)
    cert_vars = PATH_SERVER_CERT_VARS.format(cert_name)
    cert_path = PATH_SERVER_CERT_CRT.format(cert_name)
    cert_private_key = PATH_SERVER_CERT_KEY.format(cert_name)
    if cert_type == 'client':
        cert_directory = PATH_CLIENT_CERT.format(cert_name)
        cert_vars = PATH_CLIENT_CERT_VARS.format(cert_name)
        cert_path = PATH_CLIENT_CERT_CRT.format(cert_name)
        cert_private_key = PATH_CLIENT_CERT_KEY.format(cert_name)

    commands_list_without_arguments = [['mkdir', '-p', cert_directory],
                                       ['cp', f'{current_dir}/pki/vars', cert_vars],
                                       ['cp', f'{current_dir}/pki/issued/{cert_name}.crt', cert_path],
                                       ['cp', f'{current_dir}/pki/private/{cert_name}.key', cert_private_key],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)

    return serial, start_date, end_date, lifetime, distingushed_name, cert_type


def delete_certificate_in_system(cert_name, cert_type):
    """Function to delete a certificate in system"""
    current_dir = get_current_directory()

    if cert_type == 'server':
        commands_list_without_arguments = [['sudo', 'rm', '-rf', PATH_SERVER_CERT.format(cert_name)],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/issued/server.crt'],
                                           ['sudo', 'rm', '-f', f'{current_dir}/pki/private/server.key'],
                                        #    f'sudo rm -f {current_dir}/pki/dh.pem',
                                           ]
    elif cert_type == 'client':
        commands_list_without_arguments = [['sudo', 'rm', '-rf', PATH_CLIENT_CERT.format(cert_name)],
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


def export_certificate_in_system(cert_name, cert_type, download_type, password=''):
    """Export a certificate from system"""
    # configure certificate path: Server or Client
    cert_path = PATH_SERVER_CERT.format(cert_name)
    if cert_type == 'cient':
        cert_path = PATH_CLIENT_CERT.format(cert_name)
    
    if download_type == 'certificate':
        cert_value = read_certificate_value(cert_path)
    elif download_type == 'private_key':
        cert_value = read_certificate_value(cert_path.replace(".crt", ".key"))
    else:  # .p12 file
        cert_path_p12 = f'/asguard/newdms/src/downloads/{cert_name}.p12'
        execute_command_without_arguments(["openssl", "pkcs12", "-export", "-out", cert_path_p12,
                                           "-inkey", f"{cert_path.replace('.crt', '.key')}", "-in", f"{cert_path}",
                                           "-passout", f'pass:{password}'])
        cert_value = "Certificate p12"
        # download_certificate(f'/asguard/newdms/src/downloads/{cert_name}.p12', cert_value)
    return cert_value
