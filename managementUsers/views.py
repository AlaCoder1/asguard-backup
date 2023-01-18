from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import *
import os 
import subprocess
import sys
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.
def deleteUser(username):
    # return subprocess.run(["userdel", "-r", username])
    return os.system("userdel " + "-r " +username)
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
        serializer = UserSerializer(tab_users, many=True)
        # print(serializer.data)
        # return a Json response
        return JsonResponse(serializer.data,safe=False)

from rest_framework.parsers import JSONParser  
@csrf_exempt
def createUser(request):
    if(request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        print(data['username'])
        serializer = UserSerializer(data=data)
        # check if the sent information is okay
        if(serializer.is_valid()):
            # if okay, save it on the database
            # serializer.save()
            # provide a Json Response with the data that was saved
            return JsonResponse(serializer.data, status=201)
            # provide a Json Response with the necessary error information
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt   
def userDetails(request):
    
    if(request.method == 'PUT'):
        data = json.loads(request.body)
        print(data['username'])
        # parse the incoming information
        # data = JSONParser().parse(request)  
        # instanciate with the serializer
        # serializer = UserSerializer(user, data=data)
        serializer = UserSerializer()
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
        return HttpResponse(status=204) 