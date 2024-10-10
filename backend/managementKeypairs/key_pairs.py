"""This file is for working on Key Pairs (Private Key and Public Key) in system"""

from backend.ipsec.constant_variables import PATH_IPSEC_D_CERTS, PATH_IPSEC_D_FINGER_PRINTS, PATH_IPSEC_D_PRIVATE
from backend.managementKeypairs.utils import get_finger_print, get_key_size
from utils.commands_utils import execute_list_commands_without_arguments
from utils.commands_utils import execute_command_without_arguments


def create_private_key_in_system(private_key_name, private_key_length):
    """Function to create in system a private key"""
    execute_command_without_arguments(['sudo', 'openssl', 'genrsa', '-out', f'{PATH_IPSEC_D_PRIVATE}{private_key_name}.pem', private_key_length])


def delete_private_key_in_system(private_key_name):
    """Function to delete a private in system"""
    execute_command_without_arguments(['sudo', 'rm', '-rf', f'{PATH_IPSEC_D_PRIVATE}{private_key_name}.pem'])


def create_public_key_in_system(private_key_name, public_key_name):
    """Function to create in system a private key"""
    commands_list_without_arguments = [['sudo', 'mkdir', '-p', PATH_IPSEC_D_FINGER_PRINTS],
                                       ['sudo', 'openssl', 'rsa', '-in', f'{PATH_IPSEC_D_PRIVATE}{private_key_name}.pem', '-pubout', '-out', f'{PATH_IPSEC_D_CERTS}{public_key_name}.pem'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    # finger_print = get_finger_print(private_key_name)
    # return finger_print


def import_public_key(public_key_name, public_key_value):
    """Function to import in system a private key"""
    with open(f'{PATH_IPSEC_D_CERTS}{public_key_name}.pem', 'w') as public_key_file:
        public_key_file.write(public_key_value)
    public_key_length = get_key_size(public_key_name)
    # finger_print = get_finger_print(public_key_name, public_key_length)
    return public_key_length


def delete_public_key_in_system(public_key_name):
    """Function to delete a public in system"""
    execute_command_without_arguments(['sudo', 'rm', '-rf', f'{PATH_IPSEC_D_CERTS}{public_key_name}.pem'])
