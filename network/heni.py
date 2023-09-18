import paramiko
import getpass
import psycopg2
from datetime import timezone, datetime

def sudo(cmd):
    return "sudo "+cmd
# def connect_ssh(host,port,username,password):
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(host, username=username,
#                 password=password, port=port)
#     return ssh
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
cmd = "nmcli con sh | awk '$3 != \"loopback\" {print $NF}'"
stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
list_interfaces = stdout.read().decode('utf-8').split('\n')
list_interfaces.pop(0)
list_interfaces.pop()
print("\n Choose interface?: ")
def choose_interface(list_interfaces):
    while True:
        for idx, choice in enumerate(list_interfaces, 1):
            print(f"{idx}. {choice}")

        try:
            selection = int(input("Enter your choice: "))

            if 1 <= selection <= len(list_interfaces):
                return list_interfaces[selection - 1]
            else:
                print("Invalid choice! Please try again.")
        except ValueError:
            print("Please enter a valid number.")

interface = choose_interface(list_interfaces)
print("\n Choose WAN or LAN?: ")
def choice_LAN_WAN():
    wan_lan = ['WAN','LAN']
    while True:
        for idx, choice in enumerate(wan_lan, 1):
            print(f"{idx}. {choice}")

        try:
            selection = int(input("Enter your choice: "))

            if 1 <= selection <= len(wan_lan):
                return wan_lan[selection - 1]
            else:
                print("Invalid choice! Please try again.")
        except ValueError:
            print("Please enter a valid choice.")

LAN_WAN = choice_LAN_WAN()  
def configurFile(ssh,choice,LAN_WAN):
    content=""
    server_path = "/etc/ConfigInterfaces"
    
    # Open an SFTP session
    sftp = ssh.open_sftp()

    # Open the remote file in write mode
    remote_file = sftp.open(server_path, 'w')
    #content
    content+="{}: {} \n".format(choice,LAN_WAN)
    remote_file.write(content)

    # Close the remote file
    remote_file.close()

    # Close the SFTP session
    sftp.close()
    
configurFile(ssh,interface,LAN_WAN)
def initDbInterface():
    server_path = "/etc/ConfigInterfaces"
    cmd = f"cat {server_path}"
    stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
    if stderr.read().decode('utf-8') == '':
        lines = stdout.read().decode('utf-8').split('\n')
        lines.pop()
        print({"lines":lines})
        print({"len(lines)":len(lines)})
        data_list= []
        try:
            # Establish the connection
            connection = psycopg2.connect(
                host="localhost",        
                port=5432,        
                user="postgres",
                password="mypassword",
                dbname="postgres"
            )

            # Create a new cursor
            cursor = connection.cursor()

            # Define your SELECT statement. This example assumes a table named 'my_table' and checks for a name 'John Doe'.
            select_query = """
            SELECT 1 FROM interface WHERE ifname = %s LIMIT 1;
            """
            for i in range(0,len(lines)):
                print({"i":i})
                print({"ifname":lines[i].split(':')[0]})
                # Data to be checked
                dataToCheck = (lines[i].split(':')[0],)
            
                # Execute the SELECT statement
                cursor.execute(select_query, dataToCheck)

                # Fetch the result
                exists = cursor.fetchone()
                
                if exists:
                    print("Data exists.")
                else:
                    print("Data does not exist.")
                    # Define your insert statement
                    insert_query = """
                    INSERT INTO interface (id, ifname, private_aux, bogon_aux, service_status, created_at, updated_at, name_interface, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
                # Interface.objects.create(ifname=lines[i].split(':')[0],name_interface=lines[i].split(':')[1].strip())

                    # List of data to be inserted
                    data_list =[(i+1,lines[i].split(':')[0],False,False,None,datetime.now(timezone.utc),datetime.now(timezone.utc),lines[i].split(':')[1],None)]
                    # data_list = [(1, 'John Doe'), (2, 'Jane Doe'), (3, 'Sam Smith')]
                    print({"data_list":data_list})
                    # Execute the insert statement
                    cursor.executemany(insert_query, data_list)

                    # Commit the transaction
                    connection.commit()

        except Exception as error:
            print("Error:", error)

        finally:
            # Close the cursor and the connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
initDbInterface()            
print("\n Choose Configuration STATIC or DHCP?: ")
def choice_STATIC_DHCP():
    static_dhcp = ['STATIC','DHCP']
    while True:
        for idx, choice in enumerate(static_dhcp, 1):
            print(f"{idx}. {choice}")

        try:
            selection = int(input("Enter your choice: "))

            if 1 <= selection <= len(static_dhcp):
                return static_dhcp[selection - 1]
            else:
                print("Invalid choice! Please try again.")
        except ValueError:
            print("Please enter a valid choice.")
            
STATIC_DHCP = choice_STATIC_DHCP()
    
def clean_old_config(config,typeConf):
    #test si les commentaires #start et #end exists
    if "#Start {}".format(typeConf) in config and "#End {}".format(typeConf) in config: 
        #indice #start
        i=config.index("#Start {}".format(typeConf))
        #indice #end
        j=config.index("#End {}".format(typeConf))
        #remove old config
        config=config[:i]+config[j+1:]
    return config

def get_old_config():
    cmd = "cat /etc/systemd/system/Asguard-Networking.service"
    ssh.exec_command(cmd)
    stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
    error = stderr.read().decode('utf-8')
    output = stdout.read().decode('utf-8').split('\n')
    if error!="":
        return error
    else:
        return output
    
##add requirement
def add_requirement(ifname,output):
    index=output.index('[Service]')
    values_to_add=['BindsTo=sys-subsystem-net-devices-{}.device'.format(ifname),
                    'After=sys-subsystem-net-devices-{}.device'.format(ifname)]
    values_to_add = [x for x in values_to_add if x not in output]
    output = output[:index] + values_to_add + output[index:]
    return output

###################    
##add exec_cmd
def add_cmd(output,commandes):
    index_cmd=output.index('[Install]') 
    output = output[:index_cmd] + commandes + output[index_cmd:]
    return output
###
########################
#function to get uuid from interface name 
def get_uuid(ifname):
    cmd = "sudo nmcli connection show | awk '$NF == \"{}\" {{print}}'".format(ifname)
      ##executer cette commande
    stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
    output = stdout.read().decode('utf-8').split('  ')
   
    print(output)
    if len(output)==0:
        return None
    else:
        output=[value for value in output if value]
        uuid=output[1]
        return uuid
#########################    
def update_conn_static_IPV4(ifname,ipaddress,netmask,gwaddr):
    uuid=get_uuid(ifname)
    # config=add_cmd(config,commands)
    cmd_final=[ 
    "sudo nmcli connection modify {} ipv4.method manual ipv4.addresses {}/{}".format(uuid,ipaddress,netmask),
    "sudo nmcli connection modify {} ipv4.gateway {} ipv4.route-metric 0 ".format(uuid,gwaddr),
    "sudo nmcli conn down {} && sudo nmcli conn up {}".format(uuid, uuid),
    ]
    for cmd in cmd_final:
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')
        if error!="":
            return error
    return get_old_config()

def update_conn_dhcp_IPV4(ifname):
    uuid=get_uuid(ifname)
    #la liste des commandes pour l'IPV4 dhcp
    cmd_final=[ 
        "sudo nmcli connection modify {} ipv4.method auto ipv4.addresses '' ipv4.gateway '' ipv4.route-metric '' ".format(uuid),
        "sudo nmcli conn down {} && sudo nmcli conn up {}".format(uuid, uuid),
        ]

    for cmd in cmd_final:
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')
        if error!="":
            return error
    return get_old_config()
def configuration_Static(interface,adress,gateway,mask):
    print(update_conn_static_IPV4(interface,adress,mask,gateway))

def configuration_DHCP(interface):
    print(update_conn_dhcp_IPV4(interface)) 
if STATIC_DHCP == "STATIC":
    print("\n PLZ ENter ur adress, gateway and mask")
    adress = input("adress?: ")
    gateway = input("gateway?: ")
    mask = input("mask?: ")
    configuration_Static(interface,adress,gateway,mask)
else:
    configuration_DHCP(interface)
    
    

             