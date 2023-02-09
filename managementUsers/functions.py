import os
import subprocess
import sys
import base64
import logging
import traceback
from django.conf import settings
from cryptography.fernet import Fernet
import re
import pam

# function to get UID from system


def getUidUser():
    return subprocess.run(["getent", "passwd"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]

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


def username_exists(username):
    # Check if the username exists in the /etc/passwd file
    with open("/etc/passwd", "r") as passwd_file:
        for line in passwd_file:
            if line.startswith(username + ":"):
                return True
    return False

# function to add user


def addUser(username, password):
    try:
        return os.system("useradd " + username + " && echo "+username+":"+password + " | chpasswd")
    except:
        print(f"Failed to add user.")
        sys.exit(1)

# function to delete user


def deleteUser(username):
    return os.system("userdel " + "-r " + username)

# functio to change username


def changeUsername(newusername, oldusername):
    return os.system("usermod -l " + newusername + " "+oldusername)

# function to add user in group


def add_user_group(groupname, username):
    try:
        return os.system("usermod -aG " + groupname + " "+username)
    except:
        print(f"Failed to add user in group.")
        sys.exit(1)

# function  to check if username=groupname


def checkSameGroupnameWithUsername(username):
    out = os.popen("id "+username).readline().strip('\n').strip()
    print(out)
    if (out[out.find("groups")+len("groups")+1:len(out)].find(username) != -1):
        return True
    return False


# function to delete user from group


def delete_user_group(groupname, username):
    return os.system("gpasswd -d "+username+" "+groupname)


# function to add user to group


def add_user_group(groupname, username):
    return os.system("gpasswd -a "+username+" "+groupname)


# function to auth


def authenticate(username, password):
    service = 'login'
    try:
        authenticated = pam.authenticate(username, password, service)
        return authenticated
    except pam.exception as e:
        print(e)
        return False

    # function to get group users
# def getGroupByUsers(groupname):
#     result = subprocess.run(["getent", "group"], capture_output=True)
#     output = result.stdout.decode()
#     for line in output.split("\n"):
#         fields = line.split(":")
#         if (len(fields) > 2) and fields[0] == groupname:
#             groups_users = fields[-1].split(',')
#     # groups_users.append(groupname)
#     return groups_users
