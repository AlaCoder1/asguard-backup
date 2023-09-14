import paramiko
import getpass
import psycopg2
from datetime import timezone, datetime
def create_ssh_client(host, username, password, port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=username, password=password, port=port)
        return ssh
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as sshException:
        print(f"Unable to establish SSH connection: {sshException}")
    except paramiko.BadHostKeyException as badHostKeyException:
        print(f"Unable to verify server's host key: {badHostKeyException}")
    except Exception as e:
        print(f"Error occurred: {e}")
    return None

host = input("host to connect?: ")
# port = input("port?: ")
username = input("username?: ")
password = getpass.getpass("password?: ")
# ssh  = connect_ssh(host,port,username,password)
ssh  = create_ssh_client(host,username,password)

def sudo(cmd):
    return "sudo "+cmd
def find_next_char(str, word):
    index = str.find(word)
    if index == -1:  # word not found
        return None
    next_index = index + len(word)
    if next_index < len(str):
        if str[next_index] == " ":
            return 0
        else:
            return str[next_index]
    else:
        return 0
def find_word_in_table(table, word):
    list_next_char =[]
    for row in table:
        if word in row:
            next_char = find_next_char(row,word)
            list_next_char.append(int(next_char))
    return list_next_char
    # return None
        
server_path = "/etc/ConfigInterfaces"
cmd = f"cat {server_path}"
ifname="eth3:WAN"
# cmd2="sudo sed -i '/{}/d' {}".format(ifname,server_path)
stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
# stdin, stdout, stderr = ssh.exec_command(sudo(cmd2))
if stderr.read().decode('utf-8') == '':
    lines = stdout.read().decode('utf-8').split('\n')
    lines.pop() 
    print({"lines":lines})
    list_next_char= find_word_in_table(lines,"WAN")
    print({"list_next_char":list_next_char})
    print({"max_coficient_next_char":max(list_next_char)})