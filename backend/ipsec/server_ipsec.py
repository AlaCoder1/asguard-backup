from backend.ipsec.constant_variables import PATH_IPSEC_CONF, PATH_IPSEC_SECRETS
from backend.ipsec.models import ServerIPsec
from backend.ipsec.utils_config import comment_conn_in_config_file, edit_conn_in_config_file, uncomment_conn_in_config_file
from backend.ipsec.utils_secrets import comment_line_in_secrets_file, create_line_secrets, edit_line_in_secrets_file, uncomment_line_in_secrets_file
from backend.managementCertificates.constant_variables import PATH_SERVER_CERT_KEY
from backend.managementKeypairs.models import PublicKey
from backend.openvpn.constant_variables import CONSTANT_METHOD_PSK, CONSTANT_METHOD_RSA
from utils.commands_utils import execute_command_without_arguments


def install_server_ipsec_in_system(conn_config, authentication, interface_address, remote_gateway):
    """Function to install an ipsec server in system by adding the right config of the tunnel"""
    
    # Adding the secret informations like the pre-shared key or certificates in ipsec.secrets file
    with open(PATH_IPSEC_SECRETS, 'a') as ipsec_secrets_file:
        if authentication["authentication_method"] == CONSTANT_METHOD_PSK:
            # Pre-shared key method
            ipsec_secrets_file.write(f"""\n\n{interface_address} {remote_gateway} : PSK '{authentication["pre_shared_key"]}' """)
        elif authentication["authentication_method"] == CONSTANT_METHOD_RSA:
            # RSA method
            ipsec_secrets_file.write(f"""\n\n : RSA {PATH_SERVER_CERT_KEY.format(authentication["cert"])}""")
        else:
            # Public Key method
            # Putting the Private Key in the ipsec.d directory in pem format
            public_key = PublicKey.objects.get(name=authentication["local_key_pair"])
            private_key = public_key.private_key.name
            ipsec_secrets_file.write(f"""\n\n : RSA {private_key}.pem """)

    with open(PATH_IPSEC_CONF, 'a') as ipsec_file:
        ipsec_file.write(f'\n{conn_config}')
    
    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])


def delete_server_ipsec_in_system(server:ServerIPsec):
    """Function to delete an ipsec server in system by removing the right config of the tunnel"""
    
    # Delete Config from config file
    edit_conn_in_config_file(server, '')
    
    # Delete secret line from secrets file
    edit_line_in_secrets_file(server, '')

    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])


def update_server_ipsec_in_system(previous_server:ServerIPsec, server:ServerIPsec, conn_config):
    """Function to update an ipsec server in system by updating the right config of the tunnel"""

    # Create line of the secrets file
    new_line_in_secrets_file = create_line_secrets(server)
    
    # Uncomment conn block and secrets line before updating it if the server is disabled
    if not previous_server.server_status:
        uncomment_conn_in_config_file(previous_server.conn_name)
        uncomment_line_in_secrets_file(previous_server)

    # Updating conn block and secrets line
    edit_conn_in_config_file(previous_server, conn_config)
    edit_line_in_secrets_file(previous_server, new_line_in_secrets_file)
    
    # Comment conn block and secrets line after updating it if the server is disabled
    if not previous_server.server_status:
        comment_conn_in_config_file(server.conn_name)
        comment_line_in_secrets_file(server)
    

    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])


def change_status_conn(enable, server:ServerIPsec):
    """Change status of a config in .conf and .secrets files by commenting or uncommenting"""
    # Edit config file
    if enable:
        uncomment_conn_in_config_file(server.conn_name)
    else:
        comment_conn_in_config_file(server.conn_name)
    
    # Edit secrets file
    if enable:
        uncomment_line_in_secrets_file(server)
    else:
        comment_line_in_secrets_file(server)
