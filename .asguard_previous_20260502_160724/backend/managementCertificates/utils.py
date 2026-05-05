import os
from backend.managementCertificates.constant_variables import CONSTANT_EASYRSA_VARIABLE, PATH_CA_CRL_PEM, PATH_CA_CRT, PATH_CA_KEY, PATH_PKI_CA, PATH_PKI_CA_CRL, PATH_PKI_CA_KEY, PATH_PKI_CERT, PATH_PKI_CERT_KEY, PATH_PKI_VARS, PATH_VARS, PATH_CLIENT_CERT_CRT, PATH_CLIENT_CERT_KEY, PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY
from backend.managementCertificates.get_data_from_certificate import get_certificates_details
from utils.commands_utils import execute_list_commands_with_arguments, write_file_from_system_safe_method
from utils.commands_utils import execute_command_with_arguments, execute_command_without_arguments, execute_list_commands_without_arguments


def check_payload(data: dict):
    """Check the payload fileds"""
    # Check the validity of method_name
    try:
        if data["method"]["method_name"] not in ["create", "import"]:
            return False
    except KeyError:
        if data["method"]["name_method"] not in ["create", "import"]:
            return False
    return True


def change_vars(current_dir, updated_field:dict):
    """This function takes some configurations of certificates and change vars file of the easyrsa"""

    # Get the vars file content
    with open(PATH_PKI_VARS.format(current_dir), 'r') as file:
        vars_content = file.read()

    for field in updated_field.items():
        # Find the input in vars file
        if vars_content.find(f'{CONSTANT_EASYRSA_VARIABLE}{field[0]}\t') > -1:
            # Get the input value before changing it
            start_index_old_value = vars_content.find(f'{CONSTANT_EASYRSA_VARIABLE}{field[0]}\t')
            end_index_old_value = vars_content.find('\n', start_index_old_value)
            if end_index_old_value > -1:
                old_value = vars_content[start_index_old_value:end_index_old_value]
            else:
                old_value = vars_content[start_index_old_value:]
            # Take in consideration the # because all the config in vars file are commented by default
            if vars_content[vars_content.find(f'{CONSTANT_EASYRSA_VARIABLE}{field[0]}')-1] == '#':
                old_value = '#' + old_value
            # Updating the vars file with the new input
            vars_content = vars_content.replace(old_value, f'{CONSTANT_EASYRSA_VARIABLE}{field[0]}\t{field[1]}')
        else:
            # Append the input in vars file
            vars_content += f'\n{CONSTANT_EASYRSA_VARIABLE}{field[0]}\t{field[1]}'
    write_file_from_system_safe_method(PATH_PKI_VARS.format(current_dir), vars_content)

    return vars_content


def initialize_ca(current_dir, ca_name='test'):
    """This function initialize the openvpn and easyrsa in system"""

    # Initialize a fresh PKI and creating a CA
    list_of_commands_with_arguments = [{'command': ['sudo', 'easyrsa', 'init-pki'], 'arguments': 'yes\nyes'},
                                       {'command': ['sudo', 'easyrsa', 'build-ca', 'nopass'], 'arguments': f'{ca_name}\n'}]
    execute_list_commands_with_arguments(list_of_commands_with_arguments)

    # Importing an existing CA to the standard easyrsa path
    commands_list_without_arguments = [['sudo', 'cp', PATH_VARS.format(ca_name), PATH_PKI_VARS.format(current_dir)],
                                       ['sudo', 'cp', PATH_CA_CRT.format(ca_name), PATH_PKI_CA.format(current_dir)],
                                       ]

    # Test if the CA has a private key and import it with crl
    if os.path.isfile(PATH_CA_KEY.format(ca_name)):
        commands_list_without_arguments.append(['sudo', 'cp', PATH_CA_KEY.format(ca_name), PATH_PKI_CA_KEY.format(current_dir)])
        commands_list_without_arguments.append(['sudo', 'cp', PATH_CA_CRL_PEM.format(ca_name), PATH_PKI_CA_CRL.format(current_dir)])
                                        
    execute_list_commands_without_arguments(commands_list_without_arguments)


def save_certificate_in_text_format(cert_path):
    cert_text = get_certificates_details(cert_path)
    with open(cert_path, "w+") as cert_file:
        cert_file.write(cert_text)


def revoke_list_certs(current_dir, ca_name, list_revoked_cert):
    """Revoking a list of certificates and generate the crl file"""

    for revoked_cert in list_revoked_cert:
        if revoked_cert.certificate_type == 'server':
            command =['sudo', 'cp', PATH_SERVER_CERT_CRT.format(revoked_cert.name), PATH_PKI_CERT.format(current_dir, 'server')]
            execute_command_without_arguments(command)
            execute_command_with_arguments(['sudo', 'easyrsa', 'revoke', 'server'], 'yes\n')
        elif revoked_cert.certificate_type == 'client':
            command = ['sudo', 'cp', PATH_CLIENT_CERT_CRT.format(revoked_cert.name), PATH_PKI_CERT.format(current_dir, revoked_cert.name)]
            execute_command_without_arguments(command)
            execute_command_with_arguments(['sudo', 'easyrsa', 'revoke', f'{revoked_cert.name}'], 'yes\n')

    # Generate crl file containing all the revoked certificates
    commands_list_without_arguments = [['sudo', 'easyrsa', 'gen-crl'],
                                       ['sudo', 'cp', PATH_PKI_CA_CRL.format(current_dir), PATH_CA_CRL_PEM.format(ca_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def save_certificate(current_dir, cert_name, cert_type):
    # Save certificate and its private key in system
    #Set certificate directory and path
    cert_vars = PATH_VARS.format(cert_name)
    cert_path = PATH_SERVER_CERT_CRT.format(cert_name)
    cert_private_key = PATH_SERVER_CERT_KEY.format(cert_name)
    if cert_type == 'client':
        cert_vars = PATH_VARS.format(cert_name)
        cert_path = PATH_CLIENT_CERT_CRT.format(cert_name)
        cert_private_key = PATH_CLIENT_CERT_KEY.format(cert_name)

    commands_list_without_arguments = [['sudo', 'cp', PATH_PKI_VARS.format(current_dir), cert_vars],
                                       ['sudo', 'cp', PATH_PKI_CERT.format(current_dir, cert_name), cert_path],
                                       ['sudo', 'cp', PATH_PKI_CERT_KEY.format(current_dir, cert_name), cert_private_key],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def download_certificate(download_cert_path, cert_value, mode_open='w+'):
    """Download a certificate"""
    with open(download_cert_path, mode_open) as download_cert:
        download_cert.write(cert_value)
