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
            ssh = connect_ssh()
            commandes_final = ["pacman -Syu --noconfirm","pacman -S iptables --noconfirm","pacman -S nftables --noconfirm","pacman -S dhclient --noconfirm","pacman -S ethtool --noconfirm","mkdir /etc/Dhcp4Config","mkdir /etc/nftables"]
            for cmd in commandes_final:
                stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
                if stderr.read().decode('utf-8') != "":
                    print(stderr.read().decode('utf-8'))

        except IntegrityError as e:
            return "Error: " + str(e)