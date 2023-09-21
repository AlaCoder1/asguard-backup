import os
import subprocess
import re


# function to get UID from system
def getUidUser():
    return subprocess.run(["sudo", "getent", "passwd"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]

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
    return os.system("sudo useradd " + username + " && sudo echo "+username+":"+password + " | sudo chpasswd")

def addMailSpool(username):
    cmd=["touch /var/mail/"+username,"chown "+username+":mail /var/mail/"+username,"chmod 660 /var/mail/"+username]
    for i in cmd:
        os.system(i)
        
# function to delete user
def deleteUser(username):
    return os.system("sudo userdel " + "-r " + username)

# functio to change username
def changeUsername(newusername, oldusername):
    return os.system("sudo usermod -l " + newusername + " "+oldusername)

# function to add user in group
def add_user_group(groupname, username):
    return os.system("sudo usermod -aG " + groupname + " "+username)

# function  to check if username=groupname
def checkSameGroupnameWithUsername(username):
    out = os.popen("id "+username).readline().strip('\n').strip()
    print(out)
    if (out[out.find("groups")+len("groups")+1:len(out)].find(username) != -1):
        return True
    return False

# function to delete user from group
def delete_user_group(groupname, username):
    return os.system("sudo gpasswd -d "+username+" "+groupname)

# function to add user to group
def add_user_group(groupname, username):
    return os.system("sudo gpasswd -a "+username+" "+groupname)

def changePW_byAdmin(newPassword, username):
    # run 'passwd' command to change password
    cmd = f"echo '{newPassword}\n{newPassword}\n' | sudo passwd {username}"
    return os.system(cmd)

def changePW(currentPassword, newPassword, username):
    # run 'passwd' command to change password
    cmd = f"echo '{currentPassword}\n{newPassword}\n{newPassword}' | passwd"
    return os.system(cmd)

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
