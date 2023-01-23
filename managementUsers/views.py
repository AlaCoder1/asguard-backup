from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import *
import os 
import subprocess
import sys
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
import json
import re
from rest_framework.parsers import JSONParser 
# Create your views here.

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
def changeUsername(oldusername, Newusername):
    return os.system("usermod -l " + Newusername +" "+oldusername)

### API to get all users       
@csrf_exempt
def getAllUsers(request):
    if(request.method == 'GET'):
        result = subprocess.run(["getent", "passwd"], capture_output=True)
        output = result.stdout.decode()
        tab_users= []
        for line in output.split("\n"):
            fields = line.split(":")
            if(len(fields) > 2 and fields[6]=='/bin/bash'):
                username = fields[0]
                uid = fields[2]
                tab_users.append({"username": username, "uid": uid})
        # get all the tasks
        # serialize the task data
        serializer = UserSerializerGet(tab_users, many=True)
        # return a Json response
        return JsonResponse(serializer.data,safe=False)

### API to create user 
@csrf_exempt
def createUser(request):
    msg=''
    if(request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        username=data['username']
        password=data['password']
        serializer = UserSerializerPost(data=data)
        # check if the sent information is okay
        if(serializer.is_valid()):
            # if okay, save it on the database
            # serializer.save()
            if(validInput(username)):
                if(validInput(password)):
                    # form.save()
                    if addUser(username,password) == 0:
                        msg='user added succesfully'
                    else:
                        msg = "useradd: user '"+username+ "' already exists"
            # provide a Json Response with the data that was saved
            return JsonResponse({"msg":msg}, status=201)
            # provide a Json Response with the necessary error information
        return JsonResponse(serializer.errors, status=400)

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
    if(request.method == 'PUT'):
        # parse the incoming information
        data = json.loads(request.body)
        oldusername =data['oldusername']
        Newusername =data['Newusername']
        # instanciate with the serializer
        if(changeUsername(oldusername,Newusername)!=0):
             # provide a JSON response with the necessary error information
            return JsonResponse({"msg":"updated failed"}, status=400)
        else:
            # provide a JSON response with the data that was submitted
            return JsonResponse({"msg":"updated succesfully"}, status=201)
       
