from backend.managementKeypairs.functions import get_finger_print, get_key_size
from backend.openvpn.functions import execute_command_without_arguments, execute_list_commands_without_arguments


def create_private_key(private_key_name, private_key_length):
    """Function to create in system a private key"""
    execute_command_without_arguments(['sudo', 'openssl', 'genrsa', '-out', f'/etc/ipsec.d/private/{private_key_name}.key', private_key_length])


def delete_private_key_in_system(private_key_name):
    """Function to delete a private in system"""
    execute_command_without_arguments(['sudo', 'rm', '-rf', f'/etc/ipsec.d/private/{private_key_name}.key'])


def create_public_key(private_key_name, public_key_name):
    """Function to create in system a private key"""
    commands_list_without_arguments = [['mkdir', '-p', '/etc/ipsec.d/finger_prints/'],
                                       ['sudo', 'openssl', 'rsa', '-in', f'/etc/ipsec.d/private/{private_key_name}.key', '-pubout', '-out', f'/etc/ipsec.d/certs/{public_key_name}.key'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    # finger_print = get_finger_print(private_key_name)
    # return finger_print


def import_public_key(public_key_name, public_key_value):
    """Function to import in system a private key"""
    with open(f'/etc/ipsec.d/certs/{public_key_name}.key', 'w') as public_key_file:
        public_key_file.write(public_key_value)
    public_key_length = get_key_size(public_key_name)
    # finger_print = get_finger_print(public_key_name, public_key_length)
    return public_key_length


def delete_public_key_in_system(public_key_name):
    """Function to delete a public in system"""
    execute_command_without_arguments(['sudo', 'rm', '-rf', f'/etc/ipsec.d/certs/{public_key_name}.key'])
