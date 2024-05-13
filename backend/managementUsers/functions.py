import os
import subprocess
import sys
import base64
import logging
import traceback
from django.conf import settings
from cryptography.fernet import Fernet
import re

# function to get UID from system


def getUidUser():
    return subprocess.run(["getent", "passwd"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]


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
    result = subprocess.run(['sudo', 'useradd', '-m', username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    error_useradd  = result.stderr.decode('utf-8')
    print({"error_useradd":error_useradd})
    proc = subprocess.Popen(['sudo', 'chpasswd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_password, stderr_password = proc.communicate(input=f"{username}:{password}".encode())

    return error_useradd, stdout_password, stderr_password 

# function to delete user


def deleteUser(username):
    cmd = "userdel " + "-r " + username
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output,error
    # return os.system("userdel " + "-r " + username)

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
def addMailSpool(username):
    cmd=["touch /var/mail/"+username,"chown "+username+":mail /var/mail/"+username,"chmod 660 /var/mail/"+username]
    for i in cmd:
        os.system(i)

def changePW_byAdmin(newPassword, username):
    # run 'passwd' command to change password
    cmd = f"echo '{newPassword}\n{newPassword}\n' | sudo passwd {username}"
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout.split("\n")
    error = completed_process.stderr
    return output,error

def changePW(currentPassword, newPassword, username):
    # Use the subprocess module to run the passwd command
    process = subprocess.Popen(['sudo','passwd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Provide the current and new passwords
    process.stdin.write(currentPassword + '\n')
    process.stdin.write(newPassword + '\n')
    process.stdin.write(newPassword + '\n')

    # Close the stdin to signal the end of input
    process.stdin.close()

    # Wait for the command to complete
    process.wait()
    stdout, stderr = process.communicate()
    print({"str from function":stderr})
    print({"std from function":stdout})
    return stdout, stderr

def resetPW(username,newPassword):
    cmd = f"echo '{username}:{newPassword}' | sudo chpasswd"
    process = subprocess.Popen(
            cmd,
            shell=True,  
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True 
        )
    stdout, stderr = process.communicate()
    print(process.returncode)
    print ( stdout, stderr)
    if process.returncode == 0:
        return (stdout, stderr)
    

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
