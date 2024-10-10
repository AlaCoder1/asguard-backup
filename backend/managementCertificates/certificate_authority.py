from backend.managementCertificates.constant_variables import PATH_CA_CRL, PATH_CA_CRL_PEM, PATH_CA_CRT, PATH_CA_KEY, PATH_PKI_CA, PATH_PKI_CA_CRL, PATH_PKI_CA_KEY, PATH_PKI_VARS, PATH_VARS, PATH_VARS_INITIALIZE
from backend.managementCertificates.utils import change_vars, save_certificate_in_text_format
from backend.managementCertificates.get_data_from_certificate import extract_certificate_distingushed_name, get_certifcate_dates, get_certifcate_serial_number, read_certificate_value
from utils.commands_utils import get_current_directory
from utils.commands_utils import execute_command_with_arguments, execute_command_without_arguments, execute_list_commands_without_arguments


def create_ca_in_system(ca_name, common_name, updated_fields_vars):
    """Function to create in system an authority certificate"""
    current_dir = get_current_directory()

    execute_command_with_arguments(['sudo', 'easyrsa', 'init-pki'], 'yes\nyes')
    command = ['cp', PATH_VARS_INITIALIZE, PATH_PKI_VARS.format(current_dir)]
    execute_command_without_arguments(command)
    change_vars(current_dir, updated_fields_vars)
    time_sleep = 1.5
    if updated_fields_vars["KEY_SIZE"] >= 8192:
        time_sleep += 12
    elif updated_fields_vars["KEY_SIZE"] > 2048:
        time_sleep += 2
    execute_command_with_arguments(['sudo', 'easyrsa', 'build-ca', 'nopass'], f'\n\n\n\n\n{common_name}\n\n\n', time_sleep)
    save_certificate_in_text_format(PATH_PKI_CA.format(current_dir))

    commands_list_without_arguments = [['sudo', 'cp', PATH_PKI_VARS.format(current_dir), PATH_VARS.format(ca_name)],
                                       ['sudo', 'cp', PATH_PKI_CA.format(current_dir), PATH_CA_CRT.format(ca_name)],
                                       ['sudo', 'cp', PATH_PKI_CA_KEY.format(current_dir), PATH_CA_KEY.format(ca_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    
    # Create revocation list
    create_list_rev_in_system(current_dir, ca_name)

    serial = get_certifcate_serial_number(PATH_CA_CRT.format(ca_name))

    return serial


def import_ca_in_system(ca_name, input_fields:dict):
    current_dir = get_current_directory()
    execute_command_with_arguments(['sudo', 'easyrsa', 'init-pki'], 'yes\nyes')
    execute_command_with_arguments(['sudo', 'easyrsa', 'build-ca', 'nopass'], f'{ca_name}\n')
    commands_list_without_arguments = [['sudo', 'cp', PATH_VARS_INITIALIZE, PATH_PKI_VARS.format(current_dir)],
                                       ['sudo', 'cp', PATH_VARS_INITIALIZE, PATH_VARS.format(ca_name)]]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    with open(PATH_CA_CRT.format(ca_name), "w+") as ca_file:
        ca_file.write(input_fields["certificate_data"])
    if input_fields["certificate_private_key"] != "":
        with open(PATH_CA_KEY.format(ca_name), "w+") as ca_file:
            ca_file.write(input_fields["certificate_private_key"])
    save_certificate_in_text_format(PATH_CA_CRT.format(ca_name))
    
    serial = get_certifcate_serial_number(PATH_CA_CRT.format(ca_name))
    serial = serial[:len(serial)-1]
    
    start_date, end_date, lifetime = get_certifcate_dates(PATH_CA_CRT.format(ca_name))
    distingushed_name = extract_certificate_distingushed_name(PATH_CA_CRT.format(ca_name))
    
    # Create revocation list

    # Test existance of private key to create a revocation list
    if input_fields["certificate_private_key"] != "":

        commands_list_without_arguments = [['sudo', 'cp', PATH_CA_CRT.format(ca_name), PATH_PKI_CA.format(current_dir)],
                                           ['sudo', 'cp', PATH_CA_KEY.format(ca_name), PATH_PKI_CA_KEY.format(current_dir)]
                                           ]
        execute_list_commands_without_arguments(commands_list_without_arguments)
        create_list_rev_in_system(current_dir, ca_name)

    return serial, start_date, end_date, lifetime, distingushed_name


def delete_ca_in_system(ca_name):
    """Function to delete a ca in system"""
    current_dir = get_current_directory()
    commands_list_without_arguments = [['sudo', 'rm', '-f', PATH_CA_CRT.format(ca_name)],
                                       ['sudo', 'rm', '-f', PATH_CA_KEY.format(ca_name)],
                                       ['sudo', 'rm', '-f', PATH_VARS.format(ca_name)],
                                       ['sudo', 'rm', '-f', PATH_CA_CRL.format(ca_name)],
                                       ['sudo', 'rm', '-f', PATH_CA_CRL_PEM.format(ca_name)],
                                       ['sudo', 'rm', '-f', PATH_PKI_CA.format(current_dir)],
                                       ['sudo', 'rm', '-f', PATH_PKI_CA_KEY.format(current_dir)],]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def export_ca_in_system(ca_path):
    """Export a CA certificate from system"""
    ca_value = read_certificate_value(ca_path)
    return ca_value


def create_list_rev_in_system(current_dir, ca_name):
    """Create a list of revocation of a CA certificate in system"""
    commands_list_without_arguments = [['sudo', 'easyrsa', 'gen-crl'],
                                       ['sudo', 'cp', PATH_PKI_CA_CRL.format(current_dir), PATH_CA_CRL_PEM.format(ca_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def export_ca_list_rev_in_system(ca_name):
    """Export a list of revocation of a CA certificate from system"""
    commands_list_without_arguments = [['sudo', 'cp', PATH_CA_CRL_PEM.format(ca_name), 
                                        PATH_CA_CRL_PEM.format(ca_name).replace(".pem", "_copy.pem")],
                                       ['sudo', 'mv', PATH_CA_CRL_PEM.format(ca_name).replace(".pem", "_copy.pem"), 
                                        PATH_CA_CRL.format(ca_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    ca_value = read_certificate_value(PATH_CA_CRL.format(ca_name))
    return ca_value
