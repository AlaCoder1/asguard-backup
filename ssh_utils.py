import paramiko
from django.conf import settings
# def ssh_connect():
#     host = "remote_server_address"
#     port = 22
#     username = "your_username"
#     password = "your_password"

#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(host, port, username, password)

#     return ssh.connect(host, port, username, password)
class SSHConnection:
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=settings.SSH_HOST,
            username=settings.SSH_USERNAME,
            password=settings.SSH_PASSWORD,
            port=settings.SSH_PORT
        )

    def execute_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdin, stdout, stderr

    def close(self):
        self.ssh.close()