import subprocess
from django.core.management.base import BaseCommand
from backend.proxy.views import run_command

def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        file_paths = [
            '/etc/squid/blocked_domain.acl',
            '/etc/squid/blocked_ip.acl',
            '/etc/squid/blocked_subnet.acl',
            '/etc/squid/allowed_domain_by_auth.acl',
            '/etc/squid/allowed_ip_by_auth.acl',
            '/etc/squid/allowed_subnet_by_auth.acl',
            '/etc/squid/squid_passwd',
        ]
        for path in file_paths:
            command = "touch " + path
            stdout, stderr = run_command(command)
        if(stderr == ''):
            print ("files created successfully.")
        else:
            print("erreur.")
