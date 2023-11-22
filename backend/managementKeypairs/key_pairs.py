from backend.openvpn.functions import execute_command_without_arguments


def create_private_key(private_key_name, private_key_length):
    """Function to create in system a private key"""
    execute_command_without_arguments(['sudo', 'openssl', 'genrsa', '-out', f'/etc/ipsec.d/private/{private_key_name}.key', private_key_length])


def delete_private_key_in_system(private_key_name):
    """Function to delete a private in system"""
    execute_command_without_arguments(['sudo', 'rm', '-rf', f'/etc/ipsec.d/private/{private_key_name}.key'])
