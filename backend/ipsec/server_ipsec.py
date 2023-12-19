import subprocess
from backend.ipsec.constant_variables import PATH_IPSEC_CONF, PATH_IPSEC_D_CACERTS, PATH_IPSEC_D_CERTS, PATH_IPSEC_D_PRIVATE, PATH_IPSEC_SECRETS
from backend.ipsec.utils import comment_conn_in_config_file, comment_line_in_secrets_file, edit_conn_in_config_file, reorganize_file, uncomment_conn_in_config_file, uncomment_line_in_secrets_file
from backend.managementCertificates.constant_variables import PATH_CA_CRT, PATH_CA_KEY, PATH_SERVER_CERT_CRT, PATH_SERVER_CERT_KEY
from backend.managementKeypairs.models import PublicKey
from utils.commands_utils import execute_list_commands_without_arguments
from utils.commands_utils import execute_command_without_arguments


def install_server_ipsec(conn_name, conn_config, authentication, interface_address, remote_gateway, ca):
    """Function to install an ipsec server in system by adding the right config of the tunnel"""
    
    # Adding the secret informations like the pre-shared key or certificates in ipsec.secrets file
    with open(PATH_IPSEC_SECRETS, 'a') as ipsec_secrets_file:
        if authentication["authentication_method"] == "Mutual PSK":
            # Pre-shared key method
            ipsec_secrets_file.write(f"""\n\n{interface_address} {remote_gateway} : PSK '{authentication["pre_shared_key"]}' """)
        elif authentication["authentication_method"] == "Mutual RSA":
            # Certificates method
            # Putting the certificates and its authoity in the ipsec.d directory in pem format
            commands_list_without_arguments = [["sudo", "openssl", "x509", "-inform DER",
                                                "-in", PATH_SERVER_CERT_CRT.format(authentication['cert']),
                                                "-out", f"{PATH_IPSEC_D_CERTS}{authentication['cert']}Cert.pem"],
                                                ["sudo", "openssl", "rsa",
                                                "-in", PATH_SERVER_CERT_KEY.format(authentication['cert']),
                                                "-out", f"{PATH_IPSEC_D_PRIVATE}{authentication['cert']}Key.pem"],
                                                ["sudo", "chmod", "600", f"{PATH_IPSEC_D_PRIVATE}{authentication['cert']}Key.pem"],
                                                ]
            # Test if the certificate had an authority or no
            if ca:
                commands_list_without_arguments.append(["sudo", "openssl", "x509", "-inform DER",
                                                "-in", PATH_CA_CRT.format(ca),
                                                "-out", f"{PATH_IPSEC_D_CACERTS}{ca}Cert.pem"])
                commands_list_without_arguments.append(["sudo", "openssl", "rsa",
                                                "-in", PATH_CA_KEY.format(ca),
                                                "-out", f"{PATH_IPSEC_D_PRIVATE}{ca}Key.pem"])
            execute_list_commands_without_arguments(commands_list_without_arguments)
            ipsec_secrets_file.write(f"""\n\n : RSA {authentication["cert"]}Key.pem """)
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


def delete_server_ipsec(conn_name_to_delete, deleted_line):
    with open(PATH_IPSEC_CONF, 'r') as ipsec_file:
        server_conf_content = ipsec_file.read()
    server_conf_content = edit_conn_in_config_file(server_conf_content, conn_name_to_delete, '')
    server_conf_content = reorganize_file(server_conf_content)
    with open(PATH_IPSEC_CONF,'w') as ipsec_file:
        ipsec_file.write(server_conf_content)
    
    with open(PATH_IPSEC_SECRETS, 'r') as secrets_file:
        secrets_content = secrets_file.read()
    secrets_content = secrets_content.replace(f'{deleted_line}', '')
    secrets_content = reorganize_file(secrets_content)
    with open(PATH_IPSEC_SECRETS, 'w') as secrets_file:
        secrets_file.write(secrets_content)

    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])


def update_server_ipsec(conn_name_to_update, updated_line_in_secrets_file, conn_config, authentication, interface_address, remote_gateway, ca):
    
    delete_server_ipsec(conn_name_to_update, updated_line_in_secrets_file)
    install_server_ipsec(conn_name_to_update, conn_config, authentication, interface_address, remote_gateway, ca)

    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])
    
    # Up IPsec config
    # execute_command_without_arguments(['sudo', 'ipsec', 'up', conn_name_to_update])


def change_status_conn(conn_name, enable, server):
    """Change status of a config in .conf and .secrets files by commenting or uncommenting"""
    with open(PATH_IPSEC_CONF, 'r') as ipsec_file:
        server_conf_content = ipsec_file.read()
    if enable:
        new_conn_content = uncomment_conn_in_config_file(server_conf_content, conn_name)
    else:
        new_conn_content = comment_conn_in_config_file(server_conf_content, conn_name)
    server_conf_content = edit_conn_in_config_file(server_conf_content, conn_name, new_conn_content)
    with open(PATH_IPSEC_CONF, 'w') as ipsec_file:
        ipsec_file.write(server_conf_content)
    
    with open(PATH_IPSEC_SECRETS, 'r') as secrets_file:
        secrets_content = secrets_file.read()
    if enable:
        new_secrets = uncomment_line_in_secrets_file(secrets_content, server)
    else:
        new_secrets = comment_line_in_secrets_file(secrets_content, server)
    with open(PATH_IPSEC_SECRETS, 'w') as secrets_file:
        secrets_file.write(new_secrets)


def up_ipsec_conn(conn_name):
    """Up IPsec config"""
    process = subprocess.run(['sudo', 'ipsec', 'up', conn_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('error: ', process.stderr.decode())
    error_up_command = process.stderr.decode()
    if len(error_up_command) != 0:
        return False
    return True
    # execute_command_without_arguments(['sudo', 'ipsec', 'up', conn_name])
