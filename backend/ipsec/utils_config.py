"""This file is for utils functions of the IPsec config file"""

from backend.ipsec.constant_variables import PATH_IPSEC_CONF
from backend.ipsec.models import ServerIPsec
from backend.ipsec.utils import reorganize_file


def find_conn_in_config(config:str, conn_name):
    """Find a conn config in ipsec.conf file"""
    conn_name_start = config.find(f'conn {conn_name}')
    if config[conn_name_start-1] == "#":
        conn_name_start -= 1
    conn_name_end = config.find('\n\nconn ', conn_name_start+5)
    if conn_name_end == -1:
        conn_name_end = config.find('\n\n#conn ', conn_name_start+5)
        if conn_name_end == -1:
            conn_name_end = len(config)
    return config[conn_name_start:conn_name_end]


def edit_conn_in_config_file(previous_server:ServerIPsec, new_conn_config):
    """Edit a conn config in ipsec.conf file"""

    with open(PATH_IPSEC_CONF, 'r') as ipsec_file:
        server_conf_content = ipsec_file.read()

    previous_conn_config = find_conn_in_config(server_conf_content, previous_server.conn_name)
    config = server_conf_content.replace(previous_conn_config, new_conn_config)
    config = reorganize_file(config)

    with open(PATH_IPSEC_CONF, 'w') as ipsec_file:
        ipsec_file.write(config)
    return config


def comment_conn_in_config_file(conn_name):
    """Comment a conn config in ipsec.conf file by adding a # in each line"""
    with open(PATH_IPSEC_CONF) as ipsec_file:
        server_conf_content = ipsec_file.read()
    previous_conn_config = find_conn_in_config(server_conf_content, conn_name)
    conn_config = "#" + previous_conn_config
    conn_config = conn_config.replace('\n', '\n#')

    server_conf_content = server_conf_content.replace(previous_conn_config, conn_config)
    server_conf_content = reorganize_file(server_conf_content)

    with open(PATH_IPSEC_CONF, 'w') as ipsec_file:
        ipsec_file.write(server_conf_content)

    return server_conf_content


def uncomment_conn_in_config_file(conn_name):
    """Uncomment a conn config in ipsec.conf file by reoving the # in each line"""
    with open(PATH_IPSEC_CONF) as ipsec_file:
        server_conf_content = ipsec_file.read()
    previous_conn_config = find_conn_in_config(server_conf_content, conn_name)
    conn_config = previous_conn_config[1:]
    conn_config = conn_config.replace('\n#', '\n')

    server_conf_content = server_conf_content.replace(previous_conn_config, conn_config)
    server_conf_content = reorganize_file(server_conf_content)

    with open(PATH_IPSEC_CONF, 'w') as ipsec_file:
        ipsec_file.write(server_conf_content)

    return server_conf_content
