from backend.ipsec.functions import comment_conn_in_config_file, comment_line_in_secrets_file, edit_conn_in_config_file, uncomment_conn_in_config_file, uncomment_line_in_secrets_file
from backend.managementKeypairs.models import PublicKey
from backend.openvpn.functions import execute_command_without_arguments, execute_list_commands_without_arguments


def install_server_ipsec(conn_name, conn_config, authentication, interface_address, remote_gateway, ca):
    """Function to install an ipsec server in system by adding the right config of the tunnel"""
    
    # Adding the secret informations like the pre-shared key or certificates in ipsec.secrets file
    with open('/etc/ipsec.secrets', 'a') as ipsec_secrets_file:
        if authentication["authentication_method"] == "Mutual PSK":
            # Pre-shared key method
            ipsec_secrets_file.write(f"""\n\n{interface_address} {remote_gateway} : PSK '{authentication["pre_shared_key"]}' """)
        elif authentication["authentication_method"] == "Mutual RSA":
            # Certificates method
            # Putting the certificates and its authoity in the ipsec.d directory in pem format
            commands_list_without_arguments = [["sudo", "openssl", "x509", "-inform DER",
                                                "-in", f"/etc/certificates_{ca}/ca.crt",
                                                "-out", f"/etc/ipsec.d/cacerts/{ca}Cert.pem"],
                                                ["sudo", "openssl", "rsa",
                                                "-in", f"/etc/certificates_{ca}/ca.key",
                                                "-out", f"/etc/ipsec.d/private/{ca}Key.pem"],
                                                ["sudo", "openssl", "x509", "-inform DER",
                                                "-in", f"/etc/openvpn/certificates_{authentication['cert']}/server.crt",
                                                "-out", f"/etc/ipsec.d/certs/{authentication['cert']}Cert.pem"],
                                                ["sudo", "openssl", "rsa",
                                                "-in", f"/etc/openvpn/certificates_{authentication['cert']}/server.key",
                                                "-out", f"/etc/ipsec.d/private/{authentication['cert']}Key.pem"],
                                                ["sudo", "chmod", "600", f"/etc/ipsec.d/private/{authentication['cert']}Key.pem"],
                                                ]
            execute_list_commands_without_arguments(commands_list_without_arguments)
            ipsec_secrets_file.write(f"""\n\n : RSA {authentication["cert"]}Key.pem """)
        else:
            # Public Key method
            # Putting the Private Key in the ipsec.d directory in pem format
            public_key = PublicKey.objects.get(name=authentication["local_key_pair"])
            private_key = public_key.private_key.name
            ipsec_secrets_file.write(f"""\n\n : RSA {private_key}.pem """)

    with open('/etc/ipsec.conf', 'a') as ipsec_file:
        ipsec_file.write(f'\n{conn_config}')
    
    # Restart IPsec service to take the new configuration
    execute_command_without_arguments(['sudo', 'ipsec', 'restart'])
    
    # Up IPsec config
    # execute_command_without_arguments(['sudo', 'ipsec', 'up', conn_name])


def delete_server_ipsec(conn_name_to_delete, deleted_line):
    with open('/etc/ipsec.conf', 'r') as ipsec_file:
        server_conf_content = ipsec_file.read()
    conn_name_start = server_conf_content.find(f'conn {conn_name_to_delete}')
    conn_name_end = server_conf_content.find('conn', conn_name_start+5)
    if conn_name_end == -1:
        conn_name_end = len(server_conf_content)
    conn_delete_content = server_conf_content[conn_name_start:conn_name_end]
    server_conf_content = server_conf_content.replace(conn_delete_content, '')
    server_conf_content = server_conf_content.replace('\n\n\n', '\n\n')
    with open('/etc/ipsec.conf','w') as ipsec_file:
        ipsec_file.write(server_conf_content)
    
    with open('/etc/ipsec.secrets', 'r') as secrets_file:
        secrets_content = secrets_file.read()
    secrets_content = secrets_content.replace(f'{deleted_line}', '')
    secrets_content = secrets_content.replace('\n\n\n', '\n\n')
    with open('/etc/ipsec.secrets', 'w') as secrets_file:
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
    with open('/etc/ipsec.conf', 'r') as ipsec_file:
        server_conf_content = ipsec_file.read()
    if enable:
        new_conn_content = uncomment_conn_in_config_file(server_conf_content, conn_name)
    else:
        new_conn_content = comment_conn_in_config_file(server_conf_content, conn_name)
    server_conf_content = edit_conn_in_config_file(server_conf_content, conn_name, new_conn_content)
    with open('/etc/ipsec.conf', 'w') as ipsec_file:
        ipsec_file.write(server_conf_content)
    
    with open('/etc/ipsec.secrets', 'r') as secrets_file:
        secrets_content = secrets_file.read()
    if enable:
        new_secrets = uncomment_line_in_secrets_file(secrets_content, server)
    else:
        new_secrets = comment_line_in_secrets_file(secrets_content, server)
    with open('/etc/ipsec.secrets', 'w') as secrets_file:
        secrets_file.write(new_secrets)
