import paramiko
import getpass
import psycopg2
from datetime import timezone, datetime
def sudo(cmd):
    return "sudo "+cmd

def find_next_char(str, word):
    index = str.find(word)
    if index == -1:  # word not found
        return None
    next_index = index + len(word)
    if next_index < len(str):
        return str[next_index]
    else:
        return 0

def getListOfNextCharByWord(table, word):
    list_next_char =[]
    for row in table:
        if word in row:
            next_char = find_next_char(row,word)
            list_next_char.append(int(next_char))
    return list_next_char
def getMaxListOfNextCharByWord(table, word):
    list_next_char =[]
    for row in table:
        if word in row:
            next_char = find_next_char(row,word)
            list_next_char.append(int(next_char))
    return max(list_next_char)

def create_ssh_client(host,username,password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username,
                password=password, port=22)
    return ssh

host = input("host to connect?: ")
username = input("username?: ")
password = getpass.getpass("password?: ")
ssh  = create_ssh_client(host,username,password)
cmd_cat = "cat /etc/ConfigInterfaces"
stdincat, stdoutcat, stderrcat = ssh.exec_command(sudo(cmd_cat))
LAN_WAN = 'WAN'
choice = "da"
if stderrcat.read().decode('utf-8') == '':
    lines = stdoutcat.read().decode('utf-8').split('\n')
    # lines.pop()
    lines = [x for x in lines if x]
    sftp = ssh.open_sftp()
    content=""
    server_path = "/etc/ConfigInterfaces"
    # Open the remote file in write mode
    remote_file = sftp.open(server_path, 'a')
    cmd_cat = f"cat {server_path}"
    stdincat, stdoutcat, stderrcat = ssh.exec_command(sudo(cmd_cat))
    if stderrcat.read().decode('utf-8') == '':
        lines = stdoutcat.read().decode('utf-8').split('\n')
        lines.pop(0)
        lines.pop()
    list_next_char= getListOfNextCharByWord(lines,"WAN")
    print({"list_next_char":list_next_char})
    print({"max(list_next_char)":max(list_next_char)})
    if list_next_char == []:
        #content
        next_LAN_WAN= LAN_WAN
    else:
        #content
        next_LAN_WAN= LAN_WAN+str(max(list_next_char)+1) 
    print({"next_LAN_WAN":next_LAN_WAN})
    content+="{}: {}\n".format(choice,next_LAN_WAN)
    remote_file.write(content)
    # Close the remote file
    remote_file.close()
    # Close the SFTP session
    sftp.close()