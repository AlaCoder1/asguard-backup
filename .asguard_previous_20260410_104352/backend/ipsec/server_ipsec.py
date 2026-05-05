import time
from backend.ipsec.constant_variables import CONSTANT_METHOD_PSK, CONSTANT_METHOD_RSA, PATH_IPSEC_CONF, PATH_IPSEC_SECRETS
from backend.ipsec.models import ServerIPsec
from backend.ipsec.utils import up_ipsec_conn
from backend.ipsec.utils_config import comment_conn_in_config_file, edit_conn_in_config_file, uncomment_conn_in_config_file
from backend.ipsec.utils_secrets import comment_line_in_secrets_file, create_line_secrets, edit_line_in_secrets_file, uncomment_line_in_secrets_file
from backend.managementCertificates.constant_variables import PATH_SERVER_CERT_KEY
from backend.managementKeypairs.models import PublicKey
from backend.nat.utils_system import add_nat_rule_in_system, delete_nat_rule_in_system
from utils.commands_utils import execute_command_without_arguments
from utils.errors_utils import CommandExecutionError


def install_server_ipsec_in_system(conn_config, authentication, interface_address, remote_gateway, address_remote_network):
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

    # Add configuration of IPsec tunnel to the configuration file
    with open(PATH_IPSEC_CONF, 'a') as ipsec_file:
        ipsec_file.write(f'\n{conn_config}')
    
    # Add a postrouting NAT rule of the IPsec configuration
    command_postrouting_nat = ["sudo", "nft", "add", "rule", "nat", "postrouting", "ip", "daddr", address_remote_network, "accept"]
    rule_content, handle_number = add_nat_rule_in_system(command_postrouting_nat)

    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])

    return rule_content, handle_number


def delete_server_ipsec_in_system(server:ServerIPsec):
    """Function to delete an ipsec server in system by removing the right config of the tunnel"""
    
    # Delete Config from config file
    edit_conn_in_config_file(server, '')
    
    # Delete secret line from secrets file
    edit_line_in_secrets_file(server, '')

    # Delete the postrouting NAT rule of the IPsec configuration
    try:
        delete_nat_rule_in_system("postrouting", server.postrouting_rule_handle)
    except CommandExecutionError:
        pass

    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])


def update_server_ipsec_in_system(previous_server:ServerIPsec, server:ServerIPsec, conn_config):
    """Function to update an ipsec server in system by updating the right config of the tunnel"""

    # Create line of the secrets file
    with open(PATH_IPSEC_SECRETS) as secret_file:
        secret_content = secret_file.read()
    new_line_in_secrets_file = create_line_secrets(secret_content, server)
    
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

    # Update the postrouting NAT rule of the IPsec configuration by deleting the previous rule and add the new one
    try:
        delete_nat_rule_in_system("postrouting", server.postrouting_rule_handle)
    except CommandExecutionError:
        pass
    command_postrouting_nat = ["sudo", "nft", "add", "rule", "nat", "postrouting", "ip", "daddr", server.address_remote_network, "accept"]
    new_rule_content, new_handle_number = add_nat_rule_in_system(command_postrouting_nat)

    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])

    return new_rule_content, new_handle_number


def enable_conn(server:ServerIPsec):
    """Enable an Ipsec tunnel in ipsec.conf and ipsec.secrets files by uncommenting and add the postrouting rule"""
    # Enable IPsec tunnel
    uncomment_conn_in_config_file(server.conn_name)
    uncomment_line_in_secrets_file(server)

    # Add a postrouting NAT rule of the IPsec configuration
    command_postrouting_nat = ["sudo", "nft", "add", "rule", "nat", "postrouting", "ip", "daddr", server.address_remote_network, "accept"]
    rule_content, handle_number = add_nat_rule_in_system(command_postrouting_nat)
    return rule_content, handle_number


def disable_conn(server:ServerIPsec):
    """Change status of a config in .conf and .secrets files by commenting or uncommenting and add or delete the postrouting rule"""
    # Disable IPsec tunnel
    comment_conn_in_config_file(server.conn_name)
    comment_line_in_secrets_file(server)
    
    # Delete the postrouting NAT rule of the IPsec configuration
    try:
        delete_nat_rule_in_system("postrouting", server.postrouting_rule_handle)
    except CommandExecutionError:
        pass


def change_status_ipsec_in_system(status="start"):
    """Start or stop IPsec. In case of start IPsec, execute command ipsec up {server_name} for all enabled ipsec config"""

    # Start or stop ipsec
    execute_command_without_arguments(['sudo', 'ipsec', status])

    # Up all enabled ipsec config
    if status == "start":
        time.sleep(2)
        list_enable_server = ServerIPsec.objects.filter(server_status=True)
        for server in list_enable_server:
            up_ipsec_conn(server.conn_name)
            time.sleep(1)
