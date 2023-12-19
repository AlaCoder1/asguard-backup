from backend.managementCertificates.constant_variables import PATH_CA_CRL_PEM, PATH_CA_CRT, PATH_CA_KEY, PATH_CA_VARS, PATH_CLIENT_CERT, PATH_CLIENT_CERT_CRT, PATH_CLIENT_CERT_KEY, PATH_CLIENT_CERT_VARS, PATH_SERVER_CERT, PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY, PATH_SERVER_CERT_VARS
from backend.managementCertificates.get_data_from_certificate import get_certificates_details
from utils.commands_utils import execute_list_commands_with_arguments
from utils.commands_utils import execute_command_with_arguments, execute_command_without_arguments, execute_list_commands_without_arguments


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
    commands_list_without_arguments = [['cp', PATH_CA_CRT.format(ca_name), f'{current_dir}/pki/ca.crt'],
                                       ['cp', PATH_CA_KEY.format(ca_name), f'{current_dir}/pki/private/ca.key'],
                                       ['cp', PATH_CA_VARS.format(ca_name), f'{current_dir}/pki/vars'],
                                       ['cp', PATH_CA_CRL_PEM.format(ca_name), f'{current_dir}/pki/crl.pem'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def save_certificate_in_text_format(cert_path):
    cert_text = get_certificates_details(cert_path)
    with open(cert_path, "w+") as cert_file:
        cert_file.write(cert_text)


def revoke_list_certs(current_dir, ca_name, list_revoked_cert):
    """Revoking a list of certificates and generate the crl file"""

    for revoked_cert in list_revoked_cert:
        if revoked_cert.certificate_type == 'server':
            command =['cp', PATH_SERVER_CERT_CRT.format(revoked_cert.name), f'{current_dir}/pki/issued/server.crt']
            execute_command_without_arguments(command)
            execute_command_with_arguments(['sudo', 'easyrsa', 'revoke', 'server'], 'yes\n')
        elif revoked_cert.certificate_type == 'client':
            command = ['cp', PATH_CLIENT_CERT_CRT.format(revoked_cert.name, revoked_cert.name), f'{current_dir}/pki/issued/{revoked_cert.name}.crt']
            execute_command_without_arguments(command)
            execute_command_with_arguments(['sudo', 'easyrsa', 'revoke', f'{revoked_cert.name}'], 'yes\n')

    # Generate crl file containing all the revoked certificates
    commands_list_without_arguments = [['sudo', 'easyrsa', 'gen-crl'],
                                       ['cp', f'{current_dir}/pki/crl.pem', PATH_CA_CRL_PEM.format(ca_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def save_certificate(current_dir, cert_name, cert_type):
    # Save certificate and its private key in system
    #Set certificate directory and path
    cert_directory = PATH_SERVER_CERT.format(cert_name)
    cert_vars = PATH_SERVER_CERT_VARS.format(cert_name)
    cert_path = PATH_SERVER_CERT_CRT.format(cert_name)
    cert_private_key = PATH_SERVER_CERT_KEY.format(cert_name)
    if cert_type == 'client':
        cert_directory = PATH_CLIENT_CERT.format(cert_name)
        cert_vars = PATH_CLIENT_CERT_VARS.format(cert_name)
        cert_path = PATH_CLIENT_CERT_CRT.format(cert_name, cert_name)
        cert_private_key = PATH_CLIENT_CERT_KEY.format(cert_name, cert_name)

    commands_list_without_arguments = [['mkdir', '-p', cert_directory],
                                       ['cp', f'{current_dir}/pki/vars', cert_vars],
                                       ['cp', f'{current_dir}/pki/issued/{cert_name}.crt', cert_path],
                                       ['cp', f'{current_dir}/pki/private/{cert_name}.key', cert_private_key],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def download_certificate(download_cert_path, cert_value, mode_open='w+'):
    """Download a certificate"""
    with open(download_cert_path, mode_open) as download_cert:
        download_cert.write(cert_value)
