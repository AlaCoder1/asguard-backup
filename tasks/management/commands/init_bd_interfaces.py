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
            server_path = "/etc/ConfigInterfaces"
            cmd = f"sudo cat {server_path}"
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
