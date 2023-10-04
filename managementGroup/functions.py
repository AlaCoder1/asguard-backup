import grp
import os
import subprocess
import sys
import re

from django.http import JsonResponse
from .models import *

# validation name of group and users (must content char and int)


def validInput(var):
    regexp = re.compile('[^0-9a-zA-Z-_]+')
    if regexp.search(var):
        return False
    else:
        return True

# function to add group


def addGroup(groupname):
    try:
        return os.system("groupadd {}".format(groupname))
    except:
        print(f"Failed to add group.")
        sys.exit(1)

# function to delete group


def delete_group(groupname):
    return os.system("groupdel " + groupname)

# functio to change username


def change_groupname(oldgroupname, Newgroupname):
    cmd = "groupmod -n " + Newgroupname + " "+oldgroupname
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout.split("\n")
    error = completed_process.stderr
    return output,error
    # return os.system("groupmod -n " + Newgroupname + " "+oldgroupname)

# function to get UID from system


def getLastGroupName():
    return subprocess.run(["getent", "group"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[0]

# function de get id group


def getUidGroup():
    return subprocess.run(["getent", "group"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]

# function to test if groupname exit


def group_exists(group_name):
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
def change_groupname_username(oldgroupname, Newgroupname):
    msg = ''
    if group_exists(Newgroupname):
        msg = f"Username {Newgroupname} exists."
        return JsonResponse({"msg": msg})
    else:
        stdout, stderr = change_groupname(oldgroupname, Newgroupname) 
        if stderr.read().decode()=='':
            reporter = Group.objects.get(groupname=oldgroupname)
            reporter.groupname = Newgroupname
            reporter.save()
            msg = "updated succesfully"
            return JsonResponse({"msg": msg})