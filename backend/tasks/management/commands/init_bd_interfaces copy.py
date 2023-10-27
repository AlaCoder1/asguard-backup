from backend.network.models import *
from django.core.management.base import BaseCommand
from django.db import IntegrityError
import paramiko
from django.conf import settings
import random

def sudo(cmd):
    return "sudo "+cmd
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-u', '--name', type=str, help='Define a username name')
        parser.add_argument('-p', '--pw', type=str, help='Define a username password')

    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            name = kwargs['name']
            pw = kwargs['pw']
            def connect_ssh():
                ssh = paramiko.SSHClient()
                # automatically add host key when connecting to a new host
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # connect to SSH server
                ssh.connect(settings.SSH_HOST, username=name,
                            password=pw, port=settings.SSH_PORT)
                return ssh
            ssh = connect_ssh()
            liste_interfaces =[]
            cmd1="ip route list | grep default | cut -d ' ' -f 3-5"
            stdin1, stdout1, stderr1 = ssh.exec_command(cmd1)
            print({'stderr1':stderr1.read().decode('utf-8')})
            output_getway_interface=stdout1.read().decode('utf-8').split('\n')
            output_getway_interface.pop()
            print({'output_getway_interface':output_getway_interface})
            print({'len_output_getway_interface':len(output_getway_interface)})
            for i in output_getway_interface:
                liste_interfaces.append(i.split(' ')[2])
            server_path = "/etc/ConfigInterfaces"
            print({"liste_interfaces":liste_interfaces})
            
            # Open an SFTP session
            sftp = ssh.open_sftp()

            # Open the remote file in write mode
            remote_file = sftp.open(server_path, 'w')
            list_LAN_WAN = ['LAN', 'WAN', "LAN1", "WAN1","LAN2"]
            content=""
            num_elements_to_select=len(liste_interfaces)
            print({"num_elements_to_select":num_elements_to_select})
            for i in liste_interfaces:
                if num_elements_to_select <= len(list_LAN_WAN):
                    random_element = random.choice(list_LAN_WAN)
                    print({"random_element":random_element})
                #content
                content+="{}: {} \n".format(i,random_element)
            # Write content to the remote file
            print({"content":content})
            remote_file.write(content)

            # Close the remote file
            remote_file.close()

            # Close the SFTP session
            sftp.close()
            cmd = f"cat {server_path}"
            stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
            if stderr.read().decode('utf-8') == '':
                lines = stdout.read().decode('utf-8').split('\n')
                lines.pop()
                print({"lines":lines})
                for i in range(0,len(lines)):
                    
                    # Check if an object with the same ifname exists
                    existing_interface = Interface.objects.filter(ifname=lines[i].split(':')[0]).exists()
                    print(existing_interface)
                    # print({"loul":lines[i].split(':')[0],"thani":lines[i].split(':')[1].strip()})
                    if existing_interface != True:
                        Interface.objects.create(ifname=lines[i].split(':')[0],name_interface=lines[i].split(':')[1].strip())
                        return "ALL Interfaces from ConfigInterfaces added succesffuly"
                        
                    
            else:
                return "erreur: "+stderr.read().decode('utf-8')           
        except IntegrityError as e:
            return "Error: " + str(e)