import paramiko
import getpass
import psycopg2
from datetime import timezone, datetime
import socket

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
    
def find_word_in_table(table, word):
    for row in table:
        if word in row:
            index = row.index(word)
            rest_of_line = row[index + len(word):]
            return rest_of_line
    return None 

def getListOfNextCharByWord(table, word):
    list_next_char =[]
    for row in table:
        if word in row:
            next_char = find_next_char(row,word)
            list_next_char.append(int(next_char))
    return list_next_char

def create_ssh_client(host, username, password, port=22, max_retries=3):
    retries = 0
    while retries < max_retries:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(host, username=username, password=password, port=port)
            return ssh
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials.")
            # host = input("host to connect?: ")
            username = input("username?: ")
            password = getpass.getpass("password?: ")
        except paramiko.SSHException as sshException:
            print(f"Unable to establish SSH connection: {sshException}")
        except paramiko.BadHostKeyException as badHostKeyException:
            print(f"Unable to verify server's host key: {badHostKeyException}")
        except socket.gaierror:
            print(f"Unable to resolve hostname or invalid address provided: {host}")
            host = input("Please enter a valid host address: ")
            username = input("username?: ")
            password = getpass.getpass("password?: ")
        except Exception as e:
            print(f"Error occurred: {e}")
        
        retries += 1
        if retries < max_retries:
            print(f"Retrying... (Attempt {retries}/{max_retries})")
    
    print(f"Max retries reached. Unable to establish SSH connection to {host}")
    return None

host = input("host to connect?: ")
username = input("username?: ")
password = getpass.getpass("password?: ")
ssh  = create_ssh_client(host,username,password)
# Example usage:
if ssh:
    # Successfully connected to SSH, you can use ssh_client for further operations
    def getListInterfaces(ssh):
        cmd = "nmcli con sh | awk '$3 != \"loopback\" {print $NF}'"
        stdin, stdout, stderr = ssh.exec_command('{}'.format(sudo(cmd)))
        list_interfaces = stdout.read().decode('utf-8').split('\n')
        list_interfaces.pop(0)
        list_interfaces = [x for x in list_interfaces if x]
        return list_interfaces
    list_interfaces = getListInterfaces(ssh)
    # print({"list_interfaces":list_interfaces})
    print("\n Choose interface?: ")
    def choose_interface(list_interfaces):
        while True:
            for idx, choice in enumerate(list_interfaces, 1):
                print(f"{idx}. {choice}")
            try:
                selection = int(input("Enter your choice: "))
                if 1 <= selection <= len(list_interfaces):
                    print(f"You chose: {list_interfaces[selection - 1]}")
                    return list_interfaces[selection - 1]
                else:
                    print("Invalid choice! Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    interface = choose_interface(list_interfaces)
    # print({"interface":interface})
    print("\n Choose WAN or LAN?: ")
    def choice_LAN_WAN():
        wan_lan = ['WAN','LAN']
        while True:
            for idx, choice in enumerate(wan_lan, 1):
                print(f"{idx}. {choice}")
            try:
                selection = int(input("Enter your choice: "))
                if 1 <= selection <= len(wan_lan):
                    # print(f"You chose: {wan_lan[selection - 1]}")
                    return wan_lan[selection - 1]
                else:
                    print("Invalid choice! Please try again.")
            except ValueError:
                print("Please enter a valid choice.")

    ########
    def initDbInterface(ssh,interface):
        print({"interface":interface})
        server_path = "/etc/ConfigInterfaces"
        cmd = f"cat {server_path}"
        stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
        if stderr.read().decode('utf-8') == '':
            lines = stdout.read().decode('utf-8').split('\n')
            lines = [x for x in lines if x]
            print({"lines":lines})
            print({"len(lines)":len(lines)})
            # data_list= []
            try:
                print('hello pg admin')
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
                # LAN_WAN_in_file = find_word_in_table(lines,interface)
                # print({"LAN_WAN_in_file":LAN_WAN_in_file})
                for i in range(0,len(lines)):
                    # Define your SELECT statement. This example assumes a table named 'my_table' and checks for a name 'John Doe'.
                    select_query = """
                        SELECT 1 FROM interface WHERE ifname = %s LIMIT 1;
                        """
                    print({"i":i})
                    print({"ifname":interface})
                    # Data to be checked
                    dataToCheck = (lines[i].split(':')[0],)
                    print({"dataToCheck":dataToCheck})
                    # Execute the SELECT statement
                    cursor.execute(select_query, dataToCheck)

                    # Fetch the result
                    exists = cursor.fetchone()
                    print({"exists":exists})
                    if exists:
                        print("Data exists.")
                        id = exists[0]
                        print({"id":id})
                        update_sql = "UPDATE interface SET updated_at = %s, name_interface = %s WHERE ifname = %s"
                        updated_at = datetime.now(timezone.utc)
                        new_value_for_column2 = lines[i].split(':')[1]
                        condition_value = interface
                        data = (updated_at, new_value_for_column2,condition_value)
                        cursor.execute(update_sql, data)
                        connection.commit()
                    else:
                        print("Data does not exist.")
                        cursor.execute("SELECT id FROM interface ORDER BY id DESC LIMIT 1;")
                        last_id = cursor.fetchone()
                        if last_id:
                            print("The last ID is:", last_id[0])
                            id = last_id[0]
                        else:
                            print("The table is empty!")
                            id =0
                        # Define your insert statement
                        print({"ididid":id})
                        insert_query = """
                        INSERT INTO interface (id, ifname, private_aux, bogon_aux, service_status, created_at, updated_at, name_interface, description)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """
                        # List of data to be inserted
                        data_list =[(id+1,lines[i].split(':')[0],False,False,None,datetime.now(timezone.utc),datetime.now(timezone.utc),lines[i].split(':')[1],None)]
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
    ########
    LAN_WAN = choice_LAN_WAN()
    # print({"LAN_WAN":LAN_WAN})
    # cmd2="sudo sed -i '/{}/d' {}".format(interface,"/etc/ConfigInterfaces")
    cmd2=f"sed -i '/{interface}/d' /etc/ConfigInterfaces"
    stdin2, stdout2, stderr2 = ssh.exec_command(sudo(cmd2))
    print({"stdout2":stdout2.read().decode('utf-8')})

    def configurFile(ssh,choice,LAN_WAN):
        # print({"choice in configurFile function":choice})
        content=""
        server_path = "/etc/ConfigInterfaces"
        # Open an SFTP session
        sftp = ssh.open_sftp()
        # Open the remote file in write mode
        remote_file = sftp.open(server_path, 'a')
        cmd_cat = f"cat {server_path}"
        stdincat, stdoutcat, stderrcat = ssh.exec_command(sudo(cmd_cat))
        if stderrcat.read().decode('utf-8') == '':
            lines = stdoutcat.read().decode('utf-8').split('\n')
            lines = [x for x in lines if x]
            list_next_char= getListOfNextCharByWord(lines,LAN_WAN)
            # print({"list_next_char":list_next_char})
            if list_next_char == []:
                #content
                next_LAN_WAN= LAN_WAN
            else:
                #content
                next_LAN_WAN= LAN_WAN+str(max(list_next_char)+1) 
            # print({"next_LAN_WAN":next_LAN_WAN})
            content+="{}: {}\n".format(choice,next_LAN_WAN)
            lines.append(content)
            cmdWrite=""" sudo cat <<EOF > /etc/ConfigInterfaces
{}
EOF""".format('\n'.join(lines))
            # print({"content to write": content})
            stdincat2, stdoutcat2, stderrcat2 = ssh.exec_command(cmdWrite)
            remote_file.write(content)
            # Close the remote file
            remote_file.close()
            # Close the SFTP session
            sftp.close()
            if stderrcat2.read().decode('utf-8')=='':
                initDbInterface(ssh,interface)
        
    configurFile(ssh,interface,LAN_WAN)
        

    initDbInterface(ssh,interface)            
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
        
    def update_conn_static_IPV4(ifname,ip_address,netmask,addrgw):
        config=get_old_config()
        config=clean_old_config(config,"IP4Config {}".format(ifname))
        #la liste des commandes pour l'IPV4 static
        commands=[
            "#Start IP4Config {}".format(ifname),
            "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
            "ExecStart=/usr/bin/ip addr add {}/{} dev {}".format(ip_address,netmask,ifname),
            "ExecStart=/usr/bin/sudo ip route add default via {} dev {} proto static metric 1200".format(addrgw,ifname),
            "#End IP4Config {}".format(ifname)
        ]
        config=add_requirement(ifname,list(config))
        config=add_cmd(config,commands)
        cmd_final=[ 
            "sudo ip addr flush dev {}".format(ifname),
            "sudo ip addr add {}/{} dev {}".format(ip_address,netmask,ifname),
            "sudo ip route add default via {} dev {} proto static onlink metric 1200".format(addrgw,ifname),
            """sudo cat <<EOF > /etc/systemd/system/Asguard-Networking.service
    {}
    EOF""".format('\n'.join(config)),
    ]
        for cmd in cmd_final:
            stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
            error = stderr.read().decode('utf-8')
            output = stdout.read().decode('utf-8').split('\n')
            if error!="":
                return error
        return get_old_config()

    def update_conn_dhcp_IPV4(ifname):
        #lancer la fonction de "remove old config"
        config=get_old_config()
        config=clean_old_config(config,"IP4Config {}".format(ifname))
        #la liste des commandes pour l'IPV4 dhcp
        commandes=[
        "#Start IP4Config {}".format(ifname),   
        "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
        "ExecStart=/usr/bin/dhclient -4 {}".format(ifname),
        "#End IP4Config {}".format(ifname)
        ]
        config=add_requirement(ifname,list(config))
        config=add_cmd(config,commandes)
        cmd_final=[ 
        "sudo ip addr flush dev {}".format(ifname),
        "sudo dhclient -4 {}".format(ifname),
        """sudo cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(config)),
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
else:
    # Handle the case where max retries were reached
    print(f"Max retries reached. Unable to establish SSH connection to {host}")