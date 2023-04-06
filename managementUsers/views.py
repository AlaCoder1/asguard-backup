from django.http import JsonResponse
from .models import *
import subprocess
from .serializers import *
from managementGroup.serializers import *
from managementGroup.views import *
from .remoteFunctions import *
import json
from rest_framework.parsers import JSONParser
from django.core import serializers
from .functions import *
from authentification.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
@csrf_exempt
# Retrieve the model class dynamically
def handle(self, *args, **options):
    # Your code to add data to the database here
    User.objects.create(username='zied', password=make_password("zied"))
    msg = "user added succesffuly"
    return JsonResponse({"msg": msg}, status=201)
# API to get all users
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getAllUsers(request):
    list_users = []
    if (request.method == 'GET'):
        users = User.objects.all()
        userDict = serializers.serialize("json", users)
        res = json.loads(userDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('password')
            res[i]['fields']['id'] = id
            list_users.append(res[i]['fields'])
        return JsonResponse(list_users, safe=False)


# API to get one user
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getUser(request, id):
    if (request.method == 'GET'):
        user = User.objects.filter(id=id)
        userDict = serializers.serialize("json", user)
        res = json.loads(userDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields'].pop('password')
        res[0]['fields']['id'] = id
        userJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(userJson)


# API to create user
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def createUser(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        username = data['username']
        password = data['password']
        print(make_password(data['password']))
        if (validInput(username)):
            if (validInput(password)):
                # Execute the command on the remote machine
                stdin, stdout, stderr = addRemoteUser(username, password)
                # convert the stderr stream to a string
                error_str = stderr.read().decode('utf-8')
                if error_str == "":
                    msg = username+" added sucessfully"
                    uid = getRemoteUidUser()
                    data['password'] = make_password(data['password'])
                    data['uid'] = uid
                    if ('group' in data):
                        groups = data['group']
                        for i in range(0, len(groups)):
                            RemoteAddUserGroup(
                                getGroupNameById(groups[i]), username)
                        serializerUser = UserSerializerPost(data=data)
                    else:
                        serializerUser = UserSerializerPostWithoutGroupAndPermission(data=data)
                        gid = getRemoteGidGroup()
                        groupname = {"groupname": username}
                        groupname['gid'] = gid
                        groupname['createdBySystem'] = True
                        serializerGroup = GroupSerializer(data=groupname)
                        # check if the sent information is okay
                        if (serializerUser.is_valid()):
                            if (serializerGroup.is_valid()):
                                # if okay, save it on the database
                                serializerUser.save()
                                serializerGroup.save()
                                # provide a Json Response with the data that was saved
                                return JsonResponse({"msg": msg}, status=201)
                            # provide a Json Response with the necessary error information
                            return JsonResponse(serializerGroup.errors, status=400)
                        # provide a Json Response with the necessary error information
                        return JsonResponse(serializerUser.errors, status=400)
                else:
                    msg = error_str
                    return JsonResponse({"msg": msg}, status=400)
            else:
                msg = "invalid password"
                return JsonResponse({"msg": msg}, status=201)
        else:
            msg = "invalid username"
            return JsonResponse({"msg": msg}, status=201)


# API to delete group
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request, id):
    msg = ""
    if (request.method == 'DELETE'):
        user = User.objects.get(id=id)
        group = Group.objects.filter(groupname=user.username)
        # Execute the command on the remote machine
        stdin, stdout, stderr = deleteRemoteUser(user.username)
        # convert the stderr stream to a string
        error_str = stderr.read().decode('utf-8')
        if error_str == "":
            user.delete()
            group.delete()
            msg = "delete succesfully"
        else:
            msg = error_str
        # return a no content response.
        return JsonResponse({"msg": msg})


# API to update user
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def modifyUser(request, id):
    if (request.method == 'PUT'):
        userById = User.objects.filter(id=id)
        userDict = serializers.serialize("json", userById)
        res = json.loads(userDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields'].pop('password')
        res[0]['fields']['id'] = id
        userJson = res[0]['fields']
        oldusername = userJson['username']
        data = json.loads(request.body)
        newusername = data['username']
        newfullname = data['fullname']
        newmail = data['email']
        newrole = data['role']
        userObject = User.objects.get(id=id)
        user = userObject.__dict__
        user['group'] = userJson['group']
        user['permission'] = userJson['permission']
        if validInput(newusername):
            if RemoteUsernameExists(newusername) and newusername != oldusername:
                msg = f"newusername  exists."
                return JsonResponse({"msg": msg})
            else:
                userObject.username = newusername
                if checkSameGroupnameWithUsername(oldusername):
                    RemotechangeUsername(newusername, oldusername)
                    change_groupname_username(oldusername, newusername)
                    msg = "updated groupname and username succesfully"
                else:
                    RemotechangeUsername(newusername, oldusername)
                    msg = "updated only username succesfully"
        else:
            msg = "invalid "+newusername
        userObject.fullname = newfullname
        userObject.email = newmail
        userObject.role = newrole
        if ('group' in data):
            groups = data['group']
            userJson['group'] = groups
            testByGroup = Group.objects.filter(user__id=id)
            testByGroupDict = serializers.serialize("json", testByGroup)
            restestByGroup = json.loads(testByGroupDict)
            for k in restestByGroup:
                RemoteDeleteUserGroup(k['fields']['groupname'], newusername)
            for m in data['group']:
                gg = Group.objects.get(id=m)
                RemoteAddUserGroup(gg.groupname, newusername)
            userObject.group.set(userJson['group'])
        userObject.save()
        return JsonResponse({"data": data, "msg": msg})


# API de create permission
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def addPermission(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        name = data['name']
        context = data['context']
        serializer = PermissionSerializer(data=data)
        # check if the sent information is okay
        if (serializer.is_valid()):
            # if okay, save it on the database
            serializer.save()
            msg = 'Permission added succesfully'
            # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
            # provide a Json Response with the necessary error information
        return JsonResponse(serializer.errors, status=400)


# API to change password user
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def changePassword(request):
    if (request.method == 'PUT'):
        data = json.loads(request.body)
        print(data)
        # instanciate with the serializer
        serializer = UserSerializerGet()
        current_password = data['current_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        if new_password != confirm_password:
            print("Passwords do not match. Please try again.")
            return JsonResponse({"msg": "Passwords do not match. Please try again."})
        subprocess.run(["echo", current_password, "|",
                       "passwd", "--stdin", "username"])
        subprocess.run(["echo", new_password, "|", "passwd",
                       "--stdin", "username", "--password"])
        print("Password changed successfully.")
        # check whether the sent information is okay
        # if(serializer.is_valid()):
        # if okay, save it on the database
        # serializer.save()
        # provide a JSON response with the data that was submitted
        # provide a JSON response with the necessary error information
        # return JsonResponse(serializer.errors, status=400)
        return JsonResponse(serializer.data, status=201)


def whoami():
    # Run the getent group command and capture its output
    command = "whoami"
    # Execute the command on the remote machine
    stdin, stdout, stderr = settings.SSH.execute_command(sudo(command))
    # Split the output into lines and extract the last line
    lines = stdout.read().decode('utf-8').split("\n")
    last_line = lines[-2] if lines[-1] == "" else lines[-1]
    print(last_line)
    whoami = last_line
    return JsonResponse({"whoami": whoami}, status=201)


import paramiko
from pyroute2 import IPRoute
@csrf_exempt
def netlink(request):
    data = JSONParser().parse(request)
    interface_name = data['interface_name']
    address = data['address']
    # Create an SSH client object
    ssh = paramiko.SSHClient()

    # Automatically add host keys from unknown hosts
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh.connect(hostname='10.1.12.14', username='root', password='rootroot')
    # Create a Netlink socket
    ip = IPRoute()

    # Create a new network interface
    # ip.link("add", ifname=interface_name, kind="dummy")
    print(ip.link("add", ifname=interface_name, kind="dummy"))

    # Configure the IP address for the interface
    ip.addr("add", index=ip.link_lookup(ifname=interface_name)[0],
            address=address, mask=24)

    return JsonResponse({"msd": "done"}, status=201)
