"""This file is for working on Server OpenVPN in system"""

import os
import shutil
import time
from backend.managementCertificates.constant_variables import PATH_CERT, PATH_KEY
from backend.managementCertificates.utils import initialize_ca
from backend.openvpn.constant_variables import PATH_DH_FILES, PATH_LOG_OPENVPN, PATH_OPENVPN, PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD, PATH_SERVER_CONF, PATH_SERVER_DH, PATH_SERVER_LOG, PATH_SERVER_STATIC, PATH_STATUS_LOG
from backend.openvpn.utils import create_tls_file
from backend.openvpn.servers_status import change_status_server_openvpn
from utils.commands_utils import execute_list_commands_without_arguments, get_current_directory


def install_server_openvpn_in_system(server_name, ca_name, tls_auth, dh_length, server_conf:str):
    """Function to install an openvpn server in system using easyrsa package to generate keys and certificates"""
    current_dir = get_current_directory()
    
    # Initialization
    initialize_ca(current_dir, ca_name)
    create_tls_file(tls_auth, PATH_SERVER_STATIC.format(server_name))

    commands_list_without_arguments = [['sudo', 'mkdir', '-p', PATH_LOG_OPENVPN],
                                       ['sudo', 'touch', PATH_STATUS_LOG],
                                       ['sudo', 'cp', PATH_DH_FILES.format(dh_length), PATH_SERVER_DH.format(server_name)]
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)
    
    with open(PATH_SERVER_CONF.format(server_name), 'w') as server_file:
        server_file.write(server_conf)


def delete_server_openvpn_in_system(server_name):
    """Function to delete an openvpn server in system and his keys and certificates"""
    commands_list_without_arguments = [['sudo', 'systemctl', 'stop', f'openvpn-server@server_{server_name}'],
                                       ['sudo', 'rm', '-f', PATH_SERVER_CONF.format(server_name)],
                                       ['sudo', 'rm', '-f', PATH_SERVER_DH.format(server_name)],
                                       ['sudo', 'rm', '-f', PATH_SERVER_STATIC.format(server_name)],
                                       ['sudo', 'rm', '-f', PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD.format(server_name)],
                                       ['sudo', 'rm', '-f', PATH_SERVER_LOG.format(server_name)],
                                       ]
    execute_list_commands_without_arguments(commands_list_without_arguments)


def update_server_openvpn_in_system(previous_server_name, server_name, tls_auth, server_conf, server_status):
    """Function to update an openvpn server in system"""
    # Change files name related to the server openvpn
    change_status_server_openvpn(previous_server_name, 'stop')
    if previous_server_name != server_name:
        commands_list_without_arguments = [['sudo', 'mv', PATH_SERVER_CONF.format(previous_server_name), 
                                            PATH_SERVER_CONF.format(server_name)],
                                           ['sudo', 'mv', PATH_SERVER_DH.format(previous_server_name), 
                                            PATH_SERVER_DH.format(server_name)],
                                           ['sudo', 'mv', PATH_SERVER_STATIC.format(previous_server_name), 
                                            PATH_SERVER_STATIC.format(server_name)],
                                           ]
        if os.path.isfile(PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD.format(previous_server_name)):
            commands_list_without_arguments.append(['sudo', 'mv', PATH_SERVER_CLIENT_MANAGEMENT_PASSWORD.format(previous_server_name),
                                                    PATH_SERVER_STATIC.format(server_name)])
        execute_list_commands_without_arguments(commands_list_without_arguments)
    
    create_tls_file(tls_auth, PATH_SERVER_STATIC.format(server_name))
    
    with open(PATH_SERVER_CONF.format(server_name), 'w') as server_file:
        server_file.write(server_conf)
    
    #Restart server in system if the system was started before the changes7
    if server_status:
        change_status_server_openvpn(server_name, 'start')
        time.sleep(1)
