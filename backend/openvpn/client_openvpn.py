from pathlib import Path
from backend.openvpn.constant_variables import PATH_CLIENT_OVPN, PATH_CLIENT_PAS, PATH_CLIENT_STATIC, PATH_CLIENT_UP
from backend.openvpn.utils import create_tls_file

from utils.commands_utils import execute_list_commands_without_arguments


def install_client_openvpn(client_name, client_conf, tls_auth):
    """Function to create an openvpn client"""
    
    create_tls_file(tls_auth, PATH_CLIENT_STATIC.format(client_name))
    
    with open(PATH_CLIENT_OVPN.format(client_name), 'w') as client_file:
        client_file.write(client_conf)


def delete_client_openvpn(client_name):
    """Function to delete an openvpn client"""
    commands_list_without_arguments = [['sudo', 'rm', '-f', PATH_CLIENT_OVPN.format(client_name)],
                                       ['sudo', 'rm', '-f', PATH_CLIENT_STATIC.format(client_name)],
                                       ['sudo', 'rm', '-f', PATH_CLIENT_UP.format(client_name)],
                                       ['sudo', 'rm', '-f', PATH_CLIENT_PAS.format(client_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def update_client_openvpn(previous_client_name, client_name, client_conf, tls_auth):
    """Function to update an openvpn client"""
    if previous_client_name != client_name:
        commands_list_without_arguments = [['sudo', 'mv', PATH_CLIENT_OVPN.format(previous_client_name), PATH_CLIENT_OVPN.format(client_name)],
                                           ['sudo', 'mv', PATH_CLIENT_STATIC.format(previous_client_name), PATH_CLIENT_STATIC.format(client_name)],]
        if Path(PATH_CLIENT_UP.format(previous_client_name)).is_file():
            commands_list_without_arguments.append(['sudo', 'mv', PATH_CLIENT_UP.format(previous_client_name), PATH_CLIENT_UP.format(client_name)])
        if Path(PATH_CLIENT_PAS.format(previous_client_name)).is_file():
            commands_list_without_arguments.append(['sudo', 'mv', PATH_CLIENT_PAS.format(previous_client_name), PATH_CLIENT_PAS.format(client_name)])
            
        execute_list_commands_without_arguments(commands_list_without_arguments)
    install_client_openvpn(client_name, client_conf, tls_auth)


def export_client_in_system(list_balise_client, config:str):
    """Replace in a file the path of certificates or private key or something else with its balise and value"""
    for balise in list_balise_client:
        balise_line = config[config.find(f'{balise} '):config.find('\n', config.find(f'{balise} '))]
        balise_path = balise_line.replace(f'{balise} ', '')
        with open(balise_path) as balise_file:
            balise_value = balise_file.read()
            balise_value = balise_value[balise_value.find('-----BEGIN '):balise_value.find('\n', balise_value.find('-----END'))]
        config = config.replace(balise_line, f'<{balise}>\n{balise_value}\n</{balise}>\n')
        
    return config
