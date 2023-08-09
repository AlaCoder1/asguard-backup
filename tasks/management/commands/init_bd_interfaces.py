from network.models import *
from django.core.management.base import BaseCommand
from django.db import IntegrityError
import paramiko
from django.conf import settings

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
            server_path = "/etc/ConfigInterfaces"
            ssh = connect_ssh()
            cmd = f"cat {server_path}"
            stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
            if stderr.read().decode('utf-8') == '':
                lines = stdout.read().decode('utf-8').split('\n')
                lines.pop(0)
                lines.pop()
                for i in range(0,len(lines)):
                    # print({"loul":lines[i].split(':')[0],"thani":lines[i].split(':')[1].strip()})
                    Interface.objects.create(ifname=lines[i].split(':')[0],name_interface=lines[i].split(':')[1].strip())
                return "ALL Interfaces from ConfigInterfaces added succesffuly"
            else:
                return "erreur: "+stderr.read().decode('utf-8')
        except IntegrityError as e:
            return "Error: " + str(e)