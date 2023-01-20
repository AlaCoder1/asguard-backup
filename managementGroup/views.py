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

### function to add group  
def addGroup(groupname):
    try:
        return os.system("groupadd {}".format(groupname))
    except:
        print(f"Failed to add group.")                     
        sys.exit(1)

### function to delete group
def delete_group(groupname):
    return os.system("groupdel " + groupname)

### functio to change username
def changeGroupname(oldgroupname, Newgroupname):
    return os.system("groupmod -n " + Newgroupname +" "+oldgroupname)

### API to create group 
@csrf_exempt
def createGroup(request):
    msg=''
    if(request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        groupname=data['groupname']
        serializer = GroupSerializerPost(data=data)
        # check if the sent information is okay
        if(serializer.is_valid()):
            # if okay, save it on the database
            # serializer.save()
            if(validInput(groupname)):
                # form.save()
                if addGroup(groupname) == 0:
                    print('succes addgroup')
                    msg='group added succesfully'
                else:
                    print('faild addgroup')
                    msg = "groupadd: group '"+groupname+ "' already exists"
            # provide a Json Response with the data that was saved
            return JsonResponse({"msg":msg}, status=201)
            # provide a Json Response with the necessary error information
        return JsonResponse(serializer.errors, status=400)
    
### API to get all groups       
@csrf_exempt
def getAllGroups(request):
    if(request.method == 'GET'):
        result = subprocess.run(["getent", "group"], capture_output=True)
        output = result.stdout.decode()
        tab_groups= []
        for line in output.split("\n"):
            fields = line.split(":")
            if(len(fields) > 2):
                groupname = fields[0]
                gid = fields[2]
                tab_groups.append({"groupname": groupname, "gid": gid})
        # get all the tasks
        # serialize the task data
        serializer = GroupSerializerGet(tab_groups, many=True)
        # print(serializer.data)
        # return a Json response
        return JsonResponse(serializer.data,safe=False)

### API to delete group
@csrf_exempt   
def deleteGroup(request):
    if(request.method == 'DELETE'):
        # delete the task
        data = json.loads(request.body)
        groupname = data['groupname'] 
        delete_group(groupname)
        # return a no content response.
        return HttpResponse("delete succesfully",status=200) 
    
### API to change groupname
@csrf_exempt
def change_groupname(request):
    if(request.method == 'PUT'):
        data = json.loads(request.body)
        oldgroupname =data['oldgroupname']
        Newgroupname =data['Newgroupname']
        # parse the incoming information
        # data = JSONParser().parse(request)  
        # instanciate with the serializer
        # serializer = UserSerializer(user, data=data)
        serializer = GroupSerializerGet()
        if(validInput(Newgroupname)):
            changeGroupname(oldgroupname,Newgroupname)
            # check whether the sent information is okay
            # if(serializer.is_valid()):  
                # if okay, save it on the database
                # serializer.save() 
                # provide a JSON response with the data that was submitted
            return JsonResponse({"msg":"updated succesfully"}, status=201)
        else:
            return JsonResponse({"msg":"invalid groupname"})
        # provide a JSON response with the necessary error information
        # return JsonResponse(serializer.errors, status=400)