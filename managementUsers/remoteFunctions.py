from django.conf import settings
import base64
import logging
import traceback
from cryptography.fernet import Fernet
import re
import pam
import hashlib
from authentification.views import *

def sudo(cmd):
    return "sudo "+cmd

# function to get UID from system
def getRemoteUidUser():
    # Run the getent group command and capture its output
    command = "getent passwd"
    # Execute the command on the remote machine
    stdin, stdout, stderr = ssh.exec_command(sudo(command))
    # Split the output into lines and extract the last line
    lines = stdout.read().decode('utf-8').split("\n")
    last_line = lines[-2] if lines[-1] == "" else lines[-1]
    print(last_line)
    # Split the last line into fields and extract the group name (the first field)
    fields = last_line.split(":")
    uid = fields[2]

    return uid


# function to hash pwd
def Hash(text):
    hash_sha3_512 = hashlib.new("sha3_512", text.encode())
    return (hash_sha3_512.hexdigest())


# function to encrypted pwd
def encrypt(txt):
    try:
        # convert integer etc to string first
        txt = str(txt)
        # get the key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY)  # key should be byte
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(
            encrypted_text).decode("ascii")
        return encrypted_text
    except Exception as e:
        # log the error if any
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


# validation name of group and users (must content char and int)
def validInput(var):
    regexp = re.compile('[^0-9a-zA-Z-_]+')
    if regexp.search(var):
        return False
    else:
        return True

# validation password mustn't conetent " or '
def validPassword(password):
    if re.findall(r'["|\'|;|\|]', password):
        return False
    else:
        return True

# function to test if username exit
def RemoteUsernameExists(username):
    # Check if the username exists in the /etc/passwd file
    with open("/etc/passwd", "r") as passwd_file:
        for line in passwd_file:
            if line.startswith(username + ":"):
                return True
    return False

# function to add user
def addRemoteUser(username, password):
    # Run the getent group command and capture its output
    command = "sudo useradd " + username + " && sudo echo " + \
        username+":"+password + " | sudo chpasswd"
    # Execute the command on the remote machine
    return ssh.exec_command(command)
    return ssh.exec_command(command)

# function to delete user
def deleteRemoteUser(username):
    # Run the getent group command and capture its output
    command = "userdel -r"+username
    # Execute the command on the remote machine
    return ssh.exec_command(sudo(command))

# functio to change username
def RemotechangeUsername(newusername, oldusername):
    # Run the getent group command and capture its output
    command = "usermod -l " + newusername + " "+oldusername
    # Execute the command on the remote machine
    return ssh.exec_command(sudo(command))

# function to add user in group
def RemoteAddUserGroup(groupname, username):
    # Run the getent group command and capture its output
    command = "usermod -aG " + groupname + " "+username
    # Execute the command on the remote machine
    return ssh.exec_command(sudo(command))


# function  to check if username=groupname
def checkSameGroupnameWithUsername(username):
    # Run the getent group command and capture its output
    command = "id " + username
    # Execute the command on the remote machine
    stdin, stdout, stderr = ssh.exec_command(sudo(command))
    out = stdout.read().decode('utf-8')
    if (out[out.find("groups")+len("groups")+1:len(out)].find(username) != -1):
        return True
    return False


# function to delete user from group
def RemoteDeleteUserGroup(groupname, username):
    # Run the getent group command and capture its output
    command = "gpasswd -d "+username+" "+groupname
    # Execute the command on the remote machine
    return ssh.exec_command(sudo(command))


# function to add user to group
def RemoteAddUserGroup(groupname, username):
    # Run the getent group command and capture its output
    command = "gpasswd -a "+username+" "+groupname
    # Execute the command on the remote machine
    return ssh.exec_command(sudo(command))


# function to auth
def authenticate(username, password):
    service = 'login'
    try:
        authenticated = pam.authenticate(username, password, service)
        return authenticated
    except pam.exception as e:
        print(e)
        return False


def decrypt(encrypted_text):
    try:
        # get the key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY)  # key should be byte
        # decode from urlsafe base64 format
        encrypted_text = base64.urlsafe_b64decode(encrypted_text)
        # decrypt the text and convert it to string
        decrypted_text = cipher_suite.decrypt(encrypted_text).decode('ascii')
        return decrypted_text
    except Exception as e:
        # log the error if any
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


# who i'am
def whoami():
    # Run the getent group command and capture its output
    command = "whoami"
    # Execute the command on the remote machine
    stdin, stdout, stderr = ssh.exec_command(sudo(command))
    # Split the output into lines and extract the last line
    lines = stdout.read().decode('utf-8').split("\n")
    last_line = lines[-2] if lines[-1] == "" else lines[-1]
    return last_line