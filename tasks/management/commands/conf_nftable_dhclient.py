import subprocess
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
            commandes_final = ["pacman -Syu --noconfirm","pacman -S iptables --noconfirm","pacman -S nftables --noconfirm","pacman -S dhclient --noconfirm","pacman -S ethtool --noconfirm","mkdir /etc/Dhcp4Config","mkdir /etc/nftables"]
            for cmd in commandes_final:
                command = "sudo "+cmd
                completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = completed_process.stdout
                error = completed_process.stderr
                if error != "":
                    print(error)

        except IntegrityError as e:
            return "Error: " + str(e)