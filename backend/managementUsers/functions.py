import os
import subprocess
import sys
import re


def get_uid_user():
    """function to get UID from system"""
    return subprocess.run(["getent", "passwd"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]


def valid_input(var):
    """function to test name validation of group and users (must content char and int)"""
    regexp = re.compile('[^0-9a-zA-Z-_]+')
    if regexp.search(var):
        return False
    return True


def valid_password(password):
    """function to test validation password must not contain " or ' """
    if re.findall(r'["|\'|;|\|]', password):
        return False
    return True


def username_exists(username):
    """function to test if username exists in the /etc/passwd file"""
    with open("/etc/passwd", "r") as passwd_file:
        for line in passwd_file:
            if line.startswith(username + ":"):
                return True
    return False


def add_user(username, password):
    """function to add user"""
    result = subprocess.run(['sudo', 'useradd', '-m', username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    error_useradd  = result.stderr.decode('utf-8')
    print({"error_useradd":error_useradd})
    proc = subprocess.Popen(['sudo', 'chpasswd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_password, stderr_password = proc.communicate(input=f"{username}:{password}".encode())

    return error_useradd, stdout_password, stderr_password 


def delete_user_in_system(username):
    """function to delete user"""
    cmd = "sudo userdel " + "-r " + username
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error


def change_username(newusername, oldusername):
    """functio to change username"""
    return os.system("usermod -l " + newusername + " "+oldusername)


def add_user_group(groupname, username):
    """function to add user in group"""
    try:
        return os.system("usermod -aG " + groupname + " "+username)
    except:
        print("Failed to add user in group.")
        sys.exit(1)


def check_same_groupname_with_username(username):
    """function  to check if username=groupname"""
    out = os.popen("id "+username).readline().strip('\n').strip()
    if (out[out.find("groups")+len("groups")+1:len(out)].find(username) != -1):
        return True
    return False


def delete_user_group(groupname, username):
    """function to delete user from group"""
    return os.system("gpasswd -d "+username+" "+groupname)


def add_user_group(groupname, username):
    """function to add user to group"""
    return os.system("gpasswd -a "+username+" "+groupname)


def add_mail_spool(username):
    """function to auth"""
    cmd=[f"touch /var/mail/{username}",
         f"chown {username}:mail /var/mail/{username}",
         f"chmod 660 /var/mail/{username}"]
    for i in cmd:
        os.system(i)


def reset_password_by_admin_in_system(new_password, username):
    # run 'passwd' command to change password
    cmd = f"echo '{new_password}\n{new_password}\n' | sudo passwd {username}"
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout.split("\n")
    error = completed_process.stderr
    return output,error


def reset_password(username, new_password):
    cmd = f"echo '{username}:{new_password}' | sudo chpasswd"
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
