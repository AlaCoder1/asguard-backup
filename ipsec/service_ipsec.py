from itertools import islice
import paramiko


def connect_ssh():
    """Connect to SSH ipsec server machine"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='10.1.12.101', username='root', password='root')
    return ssh


def get_config_server(server_path):
    """Get ipsec server configuration"""
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command(f"cat {server_path}")
    return stdout.read().decode()


def show_config_server(server_path):
    """Print ipsec server configuration"""
    ssh = connect_ssh()
    stdin, stdout, stderr = ssh.exec_command(f"cat {server_path}")
    lines = stdout.readlines()
    print('server.conf\n-----------------------------')
    print(lines)


def add_config_server(server_path, server_config:str):
    """Add configuration to the ipsec server"""
    ssh = connect_ssh()
    ssh.exec_command(f"echo '{server_config.strip()}' | sudo tee {server_path}")
    ssh.close()


def delete_header_config_server(server_path):
    """Delete header and commented part in the conf file"""
    server_conf_content = get_config_server(server_path)
    server_conf_content = server_conf_content[server_conf_content.find('''#      auto=start\nconn''') + len('#      auto=start') + 1:]
    add_config_server(server_path=server_path, server_config=server_conf_content)


def get_conn_start_end_indexes(server_conf_content:str, conn_name):
    """Get the start-end indexes of the connection"""
    conn_start_index = 0
    conn_end_index = 0
    for line_index, line in enumerate(server_conf_content.splitlines()):
        if line.startswith(f'conn {conn_name}'):
            conn_start_index = line_index
            conn_end_index = len(server_conf_content.splitlines())
            for line_end_index, line_end in enumerate(islice(server_conf_content.splitlines(), line_index + 1, None), start=line_index + 1):
                if line_end.startswith(f'conn '):
                    conn_end_index = line_end_index
                    break
            break
    return conn_start_index, conn_end_index


def edit_lines_config_server(server_path, conn_name_to_edit, lines_to_update, header_server_conf:str):
    delete_header_config_server(server_path=server_path)
    server_conf_content = get_config_server(server_path)
    conn_name_start, conn_name_end = get_conn_start_end_indexes(server_conf_content, conn_name_to_edit)

    updated_content = []
    for line_index, line in enumerate(server_conf_content.splitlines()):
        if not line.startswith('conn'):
            line = line.replace(' ', '')
            key_value = line.split('=', 1)
            if len(key_value) == 2 and key_value[0] in lines_to_update and line_index in range(conn_name_start, conn_name_end):
                key = key_value[0]
                updated_line = f"       {key}={lines_to_update[key]}"
                updated_content.append(updated_line)
            else:
                updated_content.append(f"       {line}")
        else:
            updated_content.append(line)
    updated_content.insert(0, header_server_conf)

    # Write the updated server.conf content
    server_conf = '\n'.join(updated_content)
    add_config_server(server_path=server_path, server_config=server_conf)


def delete_lines_config_server(server_path, conn_name_to_edit:str, lines_to_delete, header_server_conf:str):
    delete_header_config_server(server_path=server_path)
    server_conf_content = get_config_server(server_path)
    conn_name_start, conn_name_end = get_conn_start_end_indexes(server_conf_content, conn_name_to_edit)

    # Delete the desired lines
    for line_index, line in enumerate(server_conf_content.splitlines()):
        if not line.startswith('conn'):
            line = line.replace(' ', '')
            key_value = line[:line.find('=')]
            if not (key_value in lines_to_delete and line_index in range(conn_name_start, conn_name_end)):
                header_server_conf += f'\n       {line}'
            else:
                print('line to delete: ', line)
        else:
            header_server_conf += '\n' + line
    print('header_server_conf= ', header_server_conf)
    add_config_server(server_path=server_path, server_config=header_server_conf)


def delete_conn_config_server(server_path, conn_name_to_edit, header_server_conf:str):
    delete_header_config_server(server_path=server_path)
    server_conf_content = get_config_server(server_path)
    conn_name_start, conn_name_end = get_conn_start_end_indexes(server_conf_content, conn_name_to_edit)
    
    updated_content = []
    for line_index, line in enumerate(server_conf_content.splitlines()):
        if not line_index in range(conn_name_start, conn_name_end):
            updated_content.append(line)
    updated_content.insert(0, header_server_conf)
    
    # Write the updated server.conf content
    server_conf = '\n'.join(updated_content)
    add_config_server(server_path=server_path, server_config=server_conf)


def add_lines_config_server(server_path, conn_name_to_edit:str, lines_to_add:dict, header_server_conf:str):
    delete_header_config_server(server_path=server_path)
    server_conf_content = get_config_server(server_path)
    updated_content = [line for line in server_conf_content.splitlines()]
    for line_conf_index, line_conf in enumerate(server_conf_content.splitlines()):
        if line_conf.startswith(f'conn {conn_name_to_edit}'):
            for line in lines_to_add.items():
                updated_content.insert(line[1][1] + line_conf_index, f"       {line[0]}={line[1][0]}")
            break
    updated_content.insert(0, header_server_conf)

    # Write the updated server.conf content
    server_conf = '\n'.join(updated_content)
    add_config_server(server_path=server_path, server_config=server_conf)


def add_conn_config_server(server_path, conn_to_add):
    server_conf_content = get_config_server(server_path)
    server_conf_content += conn_to_add + '\n'
    add_config_server(server_path=server_path, server_config=server_conf_content)


# Update the desired options
# Modify the lines list as per your requirements


server_path = "/etc/ipsec.conf"

header_server_conf = """
# basic configuration

config setup
        # strictcrlpolicy=yes
        # uniqueids = no

# Add connections here.

# Sample VPN connections

#conn sample-self-signed
#      leftsubnet=10.1.0.0/16
#      leftcert=selfCert.der
#      leftsendcert=never
#      right=192.168.0.2
#      rightsubnet=10.2.0.0/16
#      rightcert=peerCert.der
#      auto=start

#conn sample-with-ca-cert
#      leftsubnet=10.1.0.0/16
#      leftcert=myCert.pem
#      right=192.168.0.2
#      rightsubnet=10.2.0.0/16
#      rightid="C=CH, O=Linux strongSwan CN=peer name"
#      auto=start 
"""

new_server_conf = """
# basic configuration

config setup
        # strictcrlpolicy=yes
        # uniqueids = no

# Add connections here.

# Sample VPN connections

#conn sample-self-signed
#      leftsubnet=10.1.0.0/16
#      leftcert=selfCert.der
#      leftsendcert=never
#      right=192.168.0.2
#      rightsubnet=10.2.0.0/16
#      rightcert=peerCert.der
#      auto=start

#conn sample-with-ca-cert
#      leftsubnet=10.1.0.0/16
#      leftcert=myCert.pem
#      right=192.168.0.2
#      rightsubnet=10.2.0.0/16
#      rightid="C=CH, O=Linux strongSwan CN=peer name"
#      auto=start
conn ipsec1-to-ipsec2
       authby=secret
       left=%defaultroute
       leftid=10.1.12.155
       leftsubnet=10.9.141.0/24
       rightid=10.1.12.31
       rightsubnet=10.9.27.0/24
       ike=aes256-sha2_256-modp1024!
       esp=aes256-sha2_256!
       keyexchange=ikev1
       keyingtries=0
       ikelifetime=1h
       lifetime=8h
       dpddelay=60
       dpdaction=120
       dpdaction=restart
       auto=start 
conn ipsec2-to-ipsec3
       authby=secret
       left=%defaultroute
       leftid=10.1.12.155
       leftsubnet=10.9.141.0/24
       rightid=10.1.12.31
       rightsubnet=10.9.27.0/24
       ike=aes256-sha2_256-modp1024!
       esp=aes256-sha2_256!
       keyexchange=ikev1
       keyingtries=0
       ikelifetime=1h
       lifetime=8h
       dpddelay=60
       dpdaction=120
       dpdaction=restart
       auto=start 
conn ipsec3-to-ipsec4
       authby=secret
       left=%defaultroute
       leftid=10.1.12.155
       leftsubnet=10.9.141.0/24
       rightid=10.1.12.31
       rightsubnet=10.9.27.0/24
       ike=aes256-sha2_256-modp1024!
       esp=aes256-sha2_256!
       keyexchange=ikev1
       keyingtries=0
       ikelifetime=1h
       lifetime=8h
       dpddelay=60
       dpdaction=120
       dpdaction=restart
       auto=start """

added_conn_server_conf = """
conn ipsec4-to-ipsec5
       authby=secret
       left=%defaultroute
       leftid=10.1.12.155
       leftsubnet=10.9.141.0/24
       rightid=10.1.12.31
       rightsubnet=10.9.27.0/24
       ike=aes256-sha2_256-modp1024!
       esp=aes256-sha2_256!
       keyexchange=ikev1
       keyingtries=0
       ikelifetime=1h
       lifetime=8h
       dpddelay=60
       dpdaction=120
       dpdaction=restart
       auto=start"""

updated_lines_server_conf = {'dpddelay': 80,
                             'lifetime': '6h'}

delete_lines_serve_conf = ['new1', 'new2', 'new3']

added_lines_server_conf = {'new1': ['new1', 3],
                           'new2': ['new2', 5],
                           'new3': ['new3', 7]}

print('before changes')
show_config_server(server_path=server_path)
add_config_server(server_path=server_path, server_config=new_server_conf)
#delete_header_config_server(server_path=server_path)

#add_lines_config_server(server_path=server_path, conn_name_to_edit='ipsec3-to-ipsec4', lines_to_add=added_lines_server_conf, header_server_conf=header_server_conf)
#add_conn_config_server(server_path=server_path, conn_to_add=added_conn_server_conf)

#delete_lines_config_server(server_path=server_path, conn_name_to_edit='ipsec3-to-ipsec4', lines_to_delete=delete_lines_serve_conf, header_server_conf=header_server_conf)
#delete_conn_config_server(server_path=server_path, conn_name='ipsec2-to-ipsec3', header_server_conf=header_server_conf)

edit_lines_config_server(server_path=server_path, conn_name_to_edit='ipsec-to-ipsec2', lines_to_update=updated_lines_server_conf, header_server_conf=header_server_conf)
print('\n\nAfter changes')
show_config_server(server_path=server_path)
