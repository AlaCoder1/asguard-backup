from openvpn.models import *
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
            file_path = "/etc/systemd/system/Asguard-Networking.service"
            ssh = connect_ssh()
            # Open an SFTP session
            sftp = ssh.open_sftp()

            # Open the remote file in write mode
            remote_file = sftp.open(file_path, 'w')
            #content
            content="""
[Unit]
Description=Asguard Config interfaces
[Service]
Type=oneshot

[Install]
WantedBy=multi-user.target
            """
            # Write content to the remote file
            remote_file.write(content)

            # Close the remote file
            remote_file.close()

            # Close the SFTP session
            sftp.close()

        except IntegrityError as e:
            return "Error: " + str(e)


def writeFile():
    # Open the file in write mode
    file = open("example.txt", "w")

    # Write content to the file
    file.write("Hello, world!\n")
    file.write("This is a sample file.")

    # Close the file
    file.close()