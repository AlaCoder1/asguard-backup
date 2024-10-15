from backend.managementCertificates.constant_variables import PATH_CLIENT_CERT_CRT, PATH_CLIENT_CERT_KEY, PATH_DOWNLOADS_CERTS_P12, PATH_PKI_CERT, PATH_PKI_CERT_INLINE, PATH_PKI_CERT_KEY, PATH_PKI_CERT_REQ, PATH_PKI_CERT_REVOKED, PATH_PKI_VARS, PATH_REVOKED, PATH_REVOKED_CERT, PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY, PATH_VARS, PATH_VARS_INITIALIZE
from backend.managementCertificates.get_data_from_certificate import extract_certificate_distingushed_name, extract_type_certificate, get_certifcate_dates, get_certifcate_serial_number, read_certificate_value
from backend.managementCertificates.utils import change_vars, initialize_ca, revoke_list_certs, save_certificate_in_text_format
from utils.commands_utils import execute_command_with_arguments, execute_command_without_arguments, execute_list_commands_without_arguments, get_current_directory


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
    cert_vars = PATH_VARS.format(cert_name)
    cert_path = PATH_SERVER_CERT_CRT.format(cert_name)
    cert_private_key = PATH_SERVER_CERT_KEY.format(cert_name)
    if cert_type == 'client':
        cert_path = PATH_CLIENT_CERT_CRT.format(cert_name)
        cert_private_key = PATH_CLIENT_CERT_KEY.format(cert_name)

    commands_list_without_arguments = [['sudo', 'cp', PATH_PKI_VARS.format(current_dir), cert_vars],
                                       ['sudo', 'cp', PATH_PKI_CERT.format(current_dir, common_name), cert_path],
                                       ['sudo', 'cp', PATH_PKI_CERT_KEY.format(current_dir, common_name), cert_private_key],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)

    serial = get_certifcate_serial_number(cert_path)

    return serial


def import_certificate_in_system(cert_name, input_fields):
    """Function to import in system an authority certificate"""
    current_dir = get_current_directory()
    execute_command_without_arguments(['cp', PATH_VARS_INITIALIZE, PATH_PKI_VARS.format(current_dir)])
    cert_path = PATH_PKI_CERT.format(current_dir, cert_name)
    private_key_path = PATH_PKI_CERT_KEY.format(current_dir, cert_name)
    with open(cert_path, "w+") as cert_file:
        cert_file.write(input_fields["certificate_data"])
    if input_fields["certificate_private_key"] != "":
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
    cert_vars = PATH_VARS.format(cert_name)
    cert_path = PATH_SERVER_CERT_CRT.format(cert_name)
    cert_private_key = PATH_SERVER_CERT_KEY.format(cert_name)
    if cert_type == 'client':
        cert_path = PATH_CLIENT_CERT_CRT.format(cert_name)
        cert_private_key = PATH_CLIENT_CERT_KEY.format(cert_name)

    commands_list_without_arguments = [['sudo', 'cp', PATH_PKI_VARS.format(current_dir), cert_vars],
                                       ['sudo', 'cp', PATH_PKI_CERT.format(current_dir, cert_name), cert_path],
                                       ]
    if input_fields["certificate_private_key"] != "":
        commands_list_without_arguments.append(['sudo', 'cp', PATH_PKI_CERT_KEY.format(current_dir, cert_name), cert_private_key])
    execute_list_commands_without_arguments(commands_list_without_arguments)

    return serial, start_date, end_date, lifetime, distingushed_name, cert_type


def delete_certificate_in_system(cert_name, cert_type):
    """Function to delete a certificate in system"""
    current_dir = get_current_directory()

    commands_list_without_arguments = [['sudo', 'rm', '-f', PATH_VARS.format(cert_name)],
                                       ['sudo', 'rm', '-f', PATH_PKI_CERT.format(current_dir, cert_name)],
                                       ['sudo', 'rm', '-f', PATH_PKI_CERT_KEY.format(current_dir, cert_name)],
                                       ['sudo', 'rm', '-f', PATH_PKI_CERT_REQ.format(current_dir, cert_name)],
                                       ['sudo', 'rm', '-f', PATH_PKI_CERT_INLINE.format(current_dir, cert_name)],]

    if cert_type == 'server':
        commands_list_without_arguments.append(['sudo', 'rm', '-f', PATH_SERVER_CERT_CRT.format(cert_name)])
        commands_list_without_arguments.append(['sudo', 'rm', '-f', PATH_SERVER_CERT_KEY.format(cert_name)])
    
    elif cert_type == 'client':
        commands_list_without_arguments.append(['sudo', 'rm', '-f', PATH_CLIENT_CERT_CRT.format(cert_name)])
        commands_list_without_arguments.append(['sudo', 'rm', '-f', PATH_CLIENT_CERT_KEY.format(cert_name)])

    execute_list_commands_without_arguments(commands_list_without_arguments)


def revoke_certificates_in_system(ca_name, cert, list_revoked_cert):
    """Revokate a list of certificates and update the crl of the authority"""
    current_dir = get_current_directory()

    # Initialization the CA
    initialize_ca(current_dir, ca_name)

    # Revoking certificates
    revoke_list_certs(current_dir, ca_name, list_revoked_cert)
    commands_list_without_arguments = [['sudo', 'mkdir', '-p', PATH_REVOKED],
                                       ['sudo', 'cp', PATH_PKI_CERT_REVOKED.format(current_dir, cert.serial), PATH_REVOKED_CERT.format(cert.serial)]]
    execute_list_commands_without_arguments(commands_list_without_arguments)

def unrevoke_certificates_in_system(ca_name, cert, list_revoked_cert):
    """Revokate a list of certificates and update the crl of the authority"""
    current_dir = get_current_directory()

    # Initialization the CA
    initialize_ca(current_dir, ca_name)

    # Revoking certificates
    revoke_list_certs(current_dir, ca_name, list_revoked_cert)

    command = ['sudo', 'rm', '-f', PATH_REVOKED_CERT.format(cert.serial)]
    execute_command_without_arguments(command)


def export_certificate_in_system(cert_name, cert_type, download_type, password=''):
    """Export a certificate from system"""
    # configure certificate path: Server or Client
    cert_path = PATH_SERVER_CERT_CRT.format(cert_name)
    cert_key_path = PATH_SERVER_CERT_KEY.format(cert_name)
    if cert_type == 'client':
        cert_path = PATH_CLIENT_CERT_CRT.format(cert_name)
        cert_key_path = PATH_CLIENT_CERT_KEY.format(cert_name)

    if download_type == 'certificate':
        cert_value = read_certificate_value(cert_path)
    elif download_type == 'private_key':
        cert_value = read_certificate_value(cert_key_path)
    else:  # .p12 file
        # execute_command_without_arguments(["sudo", "rm", "-f", PATH_DOWNLOADS_CERTS_P12.format(cert_name)])
        execute_command_without_arguments(["sudo", "openssl", "pkcs12", "-export", "-out", PATH_DOWNLOADS_CERTS_P12.format(cert_name),
                                           "-inkey", cert_key_path, "-in", cert_path,
                                           "-passout", f'pass:{password}'])
        cert_value = "Certificate p12"
    return cert_value
