import grp
import re
from .models import *
from django.conf import settings
from authentification.views import *

# function to add sudo to command


def sudo(cmd):
    return "sudo "+cmd

# validation name of group and users (must content char and int)


def validInput(var):
    regexp = re.compile('[^0-9a-zA-Z-_]+')
    if regexp.search(var):
        return False
    else:
        return True

# function to add group


def addRemoteGroup(groupname):
    # Run the getent group command and capture its output
    command = "groupadd "+groupname
    cmd = sudo(command)
    # Execute the command on the remote machine
    return ssh.exec_command(cmd)

# function to delete group


def deleteRemoteGroup(groupname):
    # Run the getent group command and capture its output
    command = "groupdel "+groupname
    # Execute the command on the remote machine
    return ssh.exec_command(command)

# functio to change username


def changeRemoteGroupname(oldgroupname, Newgroupname):
    # Run the getent group command and capture its output
    command = "groupmod -n " + Newgroupname + " "+oldgroupname
    # Execute the command on the remote machine
    return ssh.exec_command(command)

# function to get UID from system


def getRemoteLastGroupName():
    # Run the getent group command and capture its output
    command = "getent group"
    # Execute the command on the remote machine
    stdin, stdout, stderr = ssh.exec_command(command)
    # Split the output into lines and extract the last line
    lines = stdout.read().decode('utf-8').split("\n")
    last_line = lines[-2] if lines[-1] == "" else lines[-1]
    # Split the last line into fields and extract the group name (the first field)
    fields = last_line.split(":")
    group_name = fields[0]
    return group_name

# function de get id group


def getRemoteGidGroup():
    # Run the getent group command and capture its output
    command = "getent group"
    # Execute the command on the remote machine
    stdin, stdout, stderr = ssh.exec_command(command)
    # Split the output into lines and extract the last line
    lines = stdout.read().decode('utf-8').split("\n")
    last_line = lines[-2] if lines[-1] == "" else lines[-1]
    # Split the last line into fields and extract the group name (the first field)
    fields = last_line.split(":")
    gid = fields[2]
    return gid

# function to test if groupname exit


def RemoteGroupExists(group_name):
    try:
        grp.getgrnam(group_name)
        return True
    except KeyError:
        return False

# function de get all groupname by id


def getGroupNameById(pk):
    group = Group.objects.get(id=pk)
    return str(group)


# function to change groupname if groupname=username
def remote_change_groupname_username(oldgroupname, Newgroupname):
    msg = ''
    if RemoteGroupExists(Newgroupname):
        msg = f"Username {Newgroupname} exists."
        return JsonResponse({"msg": msg})
    else:
        stdin, stdout, stderr = changeRemoteGroupname(oldgroupname, Newgroupname) 
        if stderr.read().decode()=='':
            reporter = Group.objects.get(groupname=oldgroupname)
            reporter.groupname = Newgroupname
            reporter.save()
            msg = "updated succesfully"
            return JsonResponse({"msg": msg})
