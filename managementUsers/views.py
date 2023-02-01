from django.http import JsonResponse, HttpResponse 
from .models import *
import os 
import subprocess ,getpass
import sys
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
import json
import re
from rest_framework.parsers import JSONParser 
import pam
from cryptography.fernet import Fernet
import base64
import logging
import traceback
from django.conf import settings
# Create your views here.

### function to get UID from system
def getUidUser():
    return subprocess.run(["getent", "passwd"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]

### function to encrypted pwd
def encrypt(txt):
    try:
        # convert integer etc to string first
        txt = str(txt)
        # get the key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY) # key should be byte
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii") 
        return encrypted_text
    except Exception as e:
        # log the error if any
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

###### validation name of group and users (must content char and int)
def validInput(var):
    regexp = re.compile('[^0-9a-zA-Z-_]+')
    if regexp.search(var):
        return False
    else:
        return True

### validation password mustn't conetent " or '
def validPassword(password):
    if re.findall(r'["|\'|;|\|]',password):
        return False
    else:
        return True

### function to test if username exit
def username_exists(username):
    # Check if the username exists in the /etc/passwd file
    with open("/etc/passwd", "r") as passwd_file:
        for line in passwd_file:
            if line.startswith(username + ":"):
                return True
    return False

### function to add user    
def addUser(username, password):
     try:
        return os.system("useradd " + username +" && echo "+username+":"+password +" | chpasswd")
     except:
         print(f"Failed to add user.")                     
         sys.exit(1)
     
### function to delete user    
def deleteUser(username):
    return os.system("userdel " + "-r " +username)

### functio to change username
def changeUsername(oldusername, newusername):
    return os.system("usermod -l " + newusername +" "+oldusername)

### function to add user in group
def addUserToGroup(groupname,username):
    try:
        return os.system("usermod -aG " + groupname +" "+username)
    except:
         print(f"Failed to add user in group.")                     
         sys.exit(1)

### API to get all users  
@csrf_exempt
def getAllUsers(request):
    if(request.method == 'GET'):
        result = subprocess.run(["getent", "passwd"], capture_output=True)
        output = result.stdout.decode()
        tab_users= []
        for line in output.split("\n"):
            fields = line.split(":")
            if(len(fields) > 2 and fields[6]=='/bin/bash' and int(fields[2])>=1000):
                username = fields[0]
                uid = fields[2]
                tab_users.append({"username": username, "uid": uid})
        # get all the users
        # serialize the users data
        serializer = UserSerializerGet(tab_users, many=True)
        # return a Json response
        return JsonResponse(serializer.data,safe=False)

### API to create user 
from managementGroup.views import getGroupNameById
@csrf_exempt
def createUser(request):
    msg=''
    if(request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        username=data['username']
        password=data['password']
        groups = data['group']
        if(validInput(username)):
            if(validInput(password)):
                if addUser(username,password) == 0:
                    msg='user added succesfully'
                    for i in range(0,len(groups)):
                        addUserToGroup(getGroupNameById(groups[i]),username)
                    uid = getUidUser()
                    data['password'] = encrypt(password)
                    data['uid']=uid
                    serializer = UserSerializerPost(data=data)
                    # check if the sent information is okay
                    if(serializer.is_valid()):
                        # if okay, save it on the database
                        serializer.save()
                        # provide a Json Response with the data that was saved
                        return JsonResponse({"msg":msg}, status=201)
                    # provide a Json Response with the necessary error information
                    return JsonResponse(serializer.errors, status=400)
                else:
                    addUserToGroup("yy",username)
                    msg = "useradd: user '"+username+ "' already exists"
                    return JsonResponse({"msg":msg}, status=400)
        
### API to delete group
@csrf_exempt   
def delete_user(request):
    if(request.method == 'DELETE'):
        # get data from body
        data = json.loads(request.body)
        username = data['username']
        deleteUser(username)
        # return a no content response.
        return HttpResponse("delete succesfully",status=200) 
    
### API to get user details to delete or update
@csrf_exempt   
def userDetails(request):
    if(request.method == 'PUT'):
        data = json.loads(request.body)
        print(data['username'])
        # parse the incoming information
        # data = JSONParser().parse(request)  
        # instanciate with the serializer
        # serializer = UserSerializer(user, data=data)
        serializer = UserSerializerGet()
        # check whether the sent information is okay
        # if(serializer.is_valid()):  
            # if okay, save it on the database
            # serializer.save() 
            # provide a JSON response with the data that was submitted
        return JsonResponse(serializer.data, status=201)
        # provide a JSON response with the necessary error information
        # return JsonResponse(serializer.errors, status=400)
    elif(request.method == 'DELETE'):
        # delete the task
        data = json.loads(request.body)
        username = data['username']
        print(username) 
        deleteUser(username)
        # return a no content response.
        return HttpResponse("delete succesfully",status=200) 
    
### API to change password user
@csrf_exempt
def change_password(request):
    if(request.method == 'PUT'):
        data = json.loads(request.body)
        print(data)
        # instanciate with the serializer
        serializer = UserSerializerGet()
        current_password = data['current_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        if new_password != confirm_password:
            print("Passwords do not match. Please try again.")
            return JsonResponse({"msg":"Passwords do not match. Please try again."})
        
        subprocess.run(["echo", current_password, "|", "passwd", "--stdin", "username"])
        subprocess.run(["echo", new_password, "|", "passwd", "--stdin", "username", "--password"])
        print("Password changed successfully.")
        # check whether the sent information is okay
        # if(serializer.is_valid()):  
            # if okay, save it on the database
            # serializer.save() 
            # provide a JSON response with the data that was submitted
        return JsonResponse(serializer.data, status=201)
        # provide a JSON response with the necessary error information
        # return JsonResponse(serializer.errors, status=400)
    
### API to change username
@csrf_exempt
def change_username(request):
    msg=''
    if(request.method == 'PUT'):
        # parse the incoming information
        data = json.loads(request.body)
        oldusername =data['oldusername']
        newusername =data['newusername']
        if validInput(oldusername):
            if username_exists(oldusername):
                if validInput(newusername):
                    if username_exists(newusername):
                        msg = f"Username {newusername} exists."
                        return JsonResponse({"msg":msg})
                    else:
                        changeUsername(oldusername,newusername)
                        msg="updated succesfully"
                        return JsonResponse({"msg":msg})
                else:
                    msg = "invalid "+newusername
                    return JsonResponse({"msg":msg})
            else:
                msg = f"Username {oldusername} does not exist."
                return JsonResponse({"msg":msg})
        else:
            msg = "invalid "+oldusername
            return JsonResponse({"msg":msg})

### API de create permission 
@csrf_exempt
def createPermission(request):
    msg=''
    if(request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        name=data['name']
        context=data['context']
        serializer = PermissionSerializer(data=data)
        # check if the sent information is okay
        if(serializer.is_valid()):
            # if okay, save it on the database
            serializer.save()
            msg ='Permission added succesfully'
            # provide a Json Response with the data that was saved
            return JsonResponse({"msg":msg}, status=201)
            # provide a Json Response with the necessary error information
        return JsonResponse(serializer.errors, status=400)

### function to auth
def authenticate(username, password):
    service = 'login'
    try:
        authenticated = pam.authenticate(username, password, service)
        return authenticated
    except pam.exception as e:
        print(e)
        return False
    
### API1 to authentification
@csrf_exempt
def authentification(request):
    msg=''
    if(request.method == 'POST'):
        # parse the incoming information
        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        # run the command to check if the provided credentials are valid
        result = subprocess.run(["su", "-c", "id", username], input=password, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # result = subprocess.run(["su", username], input=password, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # check if the command succeeded (return code 0)
        if result.returncode == 0:
            msg = "Authentication successful!"
            return JsonResponse({"msg":msg})
        else:
            msg = "Authentication failed."
            return JsonResponse({"msg":msg})

### API2 to authentification
@csrf_exempt
def authentifacation2(request):
    msg=''
    if(request.method == 'POST'):
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        if authenticate(username, password):
            msg = "Authentication successful!"
            return JsonResponse({"msg":msg})
        else:
            msg = "Authentication failed."
            return JsonResponse({"msg":msg})
        