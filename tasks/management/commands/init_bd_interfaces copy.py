import subprocess
from network.models import *
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
            
            liste_interfaces =[]
            cmd1="sudo ip route list | grep default | cut -d ' ' -f 3-5"
            completed_process1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)
            output1 = completed_process1.stdout
            error1 = completed_process1.stderr
            print({'stderr1':error1})
            output_getway_interface=output1.split('\n')
            output_getway_interface.pop()
            print({'output_getway_interface':output_getway_interface})
            print({'len_output_getway_interface':len(output_getway_interface)})
            for i in output_getway_interface:
                liste_interfaces.append(i.split(' ')[2])
            server_path = "/etc/ConfigInterfaces"
            print({"liste_interfaces":liste_interfaces})
            
            
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
            # Write content to the local file
            with open(server_path, 'w') as local_file:
                local_file.write(content)
                
            cmd = f"cat {server_path}"
            completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = completed_process.stdout
            error = completed_process.stderr
            if error == '':
                lines = output.split('\n')
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
                return "erreur: "+error          
        except IntegrityError as e:
            return "Error: " + str(e)