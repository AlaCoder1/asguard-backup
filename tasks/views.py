from django.shortcuts import render, redirect
from django.db.models.query import InstanceCheckMeta
from django.http import request

from .models import *
from .form import *
from django.contrib import messages
import os 
import subprocess
import sys
import getpass
import re

#from usermanagement import *

def validInput(var):
    regexp = re.compile('[^0-9a-zA-Z]+')
    special_char = False
    if regexp.search(var):
        special_char = True
    if special_char == True:
        # print('INVALID')
        return False
    else:
        # print('VALID')
        return True
    
def validPassword(password):
    if re.findall(r'["|\'|;|\|]',password):
        # print('invalid password')
        return False
    else:
        # print('valid password') 
        return True
    
def addUser(username, password):
     try:
        # subprocess.run(['useradd', username , '&& echo ', username, ':', password , '| chpasswd'])   
        return os.system("useradd " + username +" && echo "+username+":"+password +" | chpasswd")
     except:
         print(f"Failed to add user.")                     
         sys.exit(1)

def addGroup(groupName):
    return os.system("groupadd {}".format(groupName))

def home(request):
    return render(request, 'home.html')

def add_user(request):
    # length_of_file = sum(1 for _ in open('/etc/passwd'))
    index_of_last_user=''
    with open('/etc/passwd','r') as f:
        list_from_file=[]
        for line in f:
            list_from_file.append(line)
        length_of_file = len(list_from_file)
        for i in range(length_of_file-1,-1,-1):
            if(list_from_file[i].find('/bin/bash')!=-1):
                index_of_last_user+=list_from_file[i].split(':')[2]
                break
    print(int(index_of_last_user))
    form = AddUser()
    if request.method == 'POST':
        form = AddUser(request.POST)
        if form.is_valid():
            username = form['username'].value()
            password = form['password'].value()
            if(validInput(username)):
                if(validInput(password)):
                    # form.save()
                    # addUser(username,password)
                    with open('/etc/passwd','a') as f:
                        # last_line = f.readlines()[-1]
                        # print(last_line)
                        # for line in f:
                        f.write(username+':x:'+str(int(index_of_last_user)+1)+':'+str(int(index_of_last_user)+1)+'::/home/'+username+':/bin/bash')
                    # return redirect('home')
    context = {'form': form}
    return render(request, 'add_user.html', context)

def add_group(request):
    form = AddGroup()
    if request.method == 'POST':
        form = AddGroup(request.POST)
        if form.is_valid():
            namegroup = form['namegroup'].value()
            if(validInput(namegroup)):
                addGroup(namegroup)
                form.save()
                return redirect('home')
    context = {'formAddGroup': form}
    return render(request, 'add_group.html', context)

def all_users(request):

    # output = subprocess.run(['getent', 'passwd'], capture_output=True, text=True)
    # users = output.stdout.strip().split('\n')
    # user_list = [user.split(':')[0] for user in users]
    # context = {"list_of_users": user_list}
    result = subprocess.run(["getent", "passwd"], capture_output=True)
    output = result.stdout.decode()
    print(output)
    users = []
    usersId = []
    for line in output.split("\n"):
        fields = line.split(":")
        if len(fields) > 2:
            username = fields[0]
            uid = fields[2]
            users.append(username)
            usersId.append(uid)
            print(f"Username: {username}, UID: {uid}")
    context = {"username": users, "uid": usersId}
    return render(request, 'all_users.html', context)

def delete_user(username):
    subprocess.run(["userdel", "-r", username])

# username = input("Enter the username of the user to delete: ")
# delete_user(username)
# print("User deleted successfully.")

 

def all_users_by_directory(request):
    tab_username=[]
    tab_userId=[]
    tab =[]
    with open('/etc/passwd','r') as f:
        for line in f:
            tab_username.append(line.split(':')[0])     
            tab_userId.append(line.split(':')[2]) 
            tab.append(line)
    return render(request,'all_user_by_directory.html', {"tab_username":tab_username, 'tab_userId':tab_userId, 'tab':tab})  
