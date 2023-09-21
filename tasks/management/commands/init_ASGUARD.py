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
            

            file_path = "/etc/systemd/system/Asguard-Networking.service"
            #content
            content="""
[Unit]
Description=Asguard Config interfaces
[Service]
Type=oneshot

[Install]
WantedBy=multi-user.target
            """
            # Write content to the local file
            with open(file_path, 'w') as local_file:
                local_file.write(content)

        except IntegrityError as e:
            return "Error: " + str(e)