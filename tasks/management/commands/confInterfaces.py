from openvpn.models import *
from django.core.management.base import BaseCommand
from django.db import IntegrityError
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
            file_path = "/etc/ConfigInterfaces"
            #content
            content="""
eth2: WAN
eth1: LAN
            """
            # Write content to the local file
            with open(file_path, 'w') as local_file:
                local_file.write(content)

        except IntegrityError as e:
            return "Error: " + str(e)