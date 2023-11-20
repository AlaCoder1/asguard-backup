from backend.openvpn.functions import create_tls_file, replace_cert_with_value

from backend.openvpn.functions import execute_list_commands_without_arguments


def install_client_openvpn(client_name, client_conf, tls_auth):
    """Function to create an openvpn client"""
    
    create_tls_file(tls_auth, f'/etc/openvpn/client/static_{client_name}.key')
    
    with open(f'/etc/openvpn/client/client_{client_name}.ovpn', 'w') as client_file:
        client_file.write(client_conf)


def delete_client_openvpn(client_name):
    """Function to delete an openvpn client"""
    commands_list_without_arguments = [['sudo', 'rm', '-f', f'/etc/openvpn/client/client_{client_name}.ovpn'],
                                       ['sudo', 'rm', '-f', f'/etc/openvpn/client/static_{client_name}.key'],
                                       ['sudo', 'rm', '-f', f'/etc/openvpn/client/client_{client_name}.up'],
                                       ['sudo', 'rm', '-f', f'/etc/openvpn/client/client_{client_name}.pas'],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def export_client_in_system(list_balise_client, config:str):
    """Replace in a file the path of certificates or private key or something else with its balise and value"""
    for balise in list_balise_client:
        balise_line = config[config.find(f'{balise} '):config.find('\n', config.find(f'{balise} '))]
        balise_path = balise_line.replace(f'{balise} ', '')
        with open(balise_path) as balise_file:
            balise_value = balise_file.read()
            balise_value = balise_value[balise_value.find('-----BEGIN '):balise_value.find('\n', balise_value.find('-----END'))]
        config = replace_cert_with_value(balise, balise_value, config)
        
    return config
