from django.shortcuts import render, redirect
from django.db.models.query import InstanceCheckMeta
from django.http import request
from django.http import HttpResponse, JsonResponse
# from .models import *
# from .form import *
from django.contrib import messages
import os 
import subprocess
import sys
import getpass
import re
import traceback
# from .serializers import *

# def validInput(var):
#     regexp = re.compile('[^0-9a-zA-Z]+')
#     special_char = False
#     if regexp.search(var):
#         special_char = True
#     if special_char == True:
#         # print('INVALID')
#         return False
#     else:
#         # print('VALID')
#         return True
    
# def validPassword(password):
#     if re.findall(r'["|\'|;|\|]',password):
#         # print('invalid password')
#         return False
#     else:
#         # print('valid password') 
#         return True
    
# def addUser(username, password):
#      try:
#         # subprocess.run(['useradd', username , '&& echo ', username, ':', password , '| chpasswd'])   
#         return os.system("useradd " + username +" && echo "+username+":"+password +" | chpasswd")
#      except:
#          print(f"Failed to add user.")                     
#          sys.exit(1)

# def addGroup(groupName):
#     try:
#         return os.system("groupadd {}".format(groupName))
#     except:
#         print(f"Failed to add group.")                     
#         sys.exit(1)

# def deleteUser(username):
#     # return subprocess.run(["userdel", "-r", username])
#     return os.system("userdel " + "-r " +username)
    
def home(request):
    return render(request, 'home.html')

# def add_user(request):
#     msg=''
#     form = AddUser()
#     if request.method == 'POST':
#         form = AddUser(request.POST)
#         print(form)
#         if form.is_valid():
#             username = form['username'].value()
#             password = form['password'].value()
#             if(validInput(username)):
#                 if(validInput(password)):
#                     # form.save()
#                     if addUser(username,password) == 0:
#                         msg='user added succesfully'
#                     else:
#                         msg = "useradd: user '"+username+ "' already exists"
                    
#     context = {'form': form,'msg':msg}
#     return render(request, 'add_user.html', context)

# def add_group(request):
#     msg=''
#     form = AddGroup()
#     if request.method == 'POST':
#         form = AddGroup(request.POST)
#         if form.is_valid():
#             namegroup = form['namegroup'].value()
#             if(validInput(namegroup)):
#                 if addGroup(namegroup) == 0:
#                     msg='group added succesfully'
#                 else:
#                     msg = "groupadd: group '"+namegroup+ "' already exists"
#                 #form.save()
#                 # return redirect('home')
#                 print(msg)
#     context = {'formAddGroup': form}
#     return render(request, 'add_group.html', context)

# def all_users(request):
#     # output = subprocess.run(['getent', 'passwd'], capture_output=True, text=True)
#     # users = output.stdout.strip().split('\n')
#     # user_list = [user.split(':')[0] for user in users]
#     # context = {"list_of_users": user_list}
#     result = subprocess.run(["getent", "passwd"], capture_output=True)
#     output = result.stdout.decode()
#     # print(output)
#     users = []
#     usersId = []
#     tab= []
#     for line in output.split("\n"):
#         fields = line.split(":")
#         # if len(fields) > 2:
#         if(len(fields) > 2 and fields[6]=='/bin/bash'):
#             username = fields[0]
#             uid = fields[2]
#             users.append(username)
#             usersId.append(uid)
#             tab.append({"username": username, "uid": uid})
#             # print(f"Username: {username}, UID: {uid}")
#     context = {"username": users, "uid": usersId, 'tab':tab}
#     return render(request, 'all_users.html', context)

# def delete_user(request,pk):
#     print(pk)
#     deleteUser(pk)
#     return render(request,'add_user.html')


# def all_users_by_directory(request):
#     tab_username=[]
#     tab_userId=[]
#     tab =[]
#     with open('/etc/passwd','r') as f:
#         for line in f:
#             tab_username.append(line.split(':')[0])     
#             tab_userId.append(line.split(':')[2]) 
#             tab.append(line)
#     return render(request,'all_user_by_directory.html', {"tab_username":tab_username, 'tab_userId':tab_userId, 'tab':tab})  
