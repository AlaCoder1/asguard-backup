import grp
import subprocess
import re
from django.http import JsonResponse
from .models import *


def validInput(var):
    """Check if the input string contains only alphanumeric characters, hyphens, and underscores."""
    regexp = re.compile('[^0-9a-zA-Z-_]+')
    if regexp.search(var):
        return False
    else:
        return True

def addGroup(groupname):
    """Add a new group to the system."""
    cmd = "groupadd " + groupname
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout.split("\n")
    error = completed_process.stderr
    return output,error

def delete_group(groupname):
    """DElete a group from the system."""
    cmd = "groupdel " + groupname
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout.split("\n")
    error = completed_process.stderr
    return output,error 

def change_groupname(oldgroupname, Newgroupname):
    """Change groupname in the system."""
    cmd = "groupmod -n " + Newgroupname + " "+oldgroupname
    completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = completed_process.stdout.split("\n")
    error = completed_process.stderr
    return output,error


def getLastGroupName():
    """Get the last groupname from the system."""
    return subprocess.run(["getent", "group"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[0]

def getUidGroup():
    """Get a Uuid group from the system."""
    return subprocess.run(["getent", "group"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]

def group_exists(group_name):
    """Check if a group exists on the system."""
    try:
        grp.getgrnam(group_name)
        return True
    except KeyError:
        return False

def getGroupNameById(pk):
    """Get groupname from database."""
    group = Group.objects.get(id=pk)
    return str(group)

def change_groupname_username(oldgroupname, Newgroupname):
    """Change groupname if groupname=username in the system."""
    msg = ''
    if group_exists(Newgroupname):
        msg = f"Username {Newgroupname} exists."
        return JsonResponse({"msg": msg})
    else:
        _, stderr = change_groupname(oldgroupname, Newgroupname) 
        if stderr=='':
            reporter = Group.objects.get(groupname=oldgroupname)
            reporter.groupname = Newgroupname
            reporter.save()
            msg = "updated succesfully"
            return JsonResponse({"msg": msg})
