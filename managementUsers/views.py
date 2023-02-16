from django.http import JsonResponse, HttpResponse
from .models import *
import subprocess
from .serializers import *
from managementGroup.serializers import *
from managementGroup.views import *
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.parsers import JSONParser
from django.core import serializers
from .functions import *
# Create your views here.

# API to get all users

# done✔


@csrf_exempt
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

# done✔


@csrf_exempt
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
# done✔
@csrf_exempt
def createUser(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        username = data['username']
        password = data['password']
        if (validInput(username)):
            if (validInput(password)):
                if addUser(username, password) == 0:
                    msg = 'user added succesfully'
                    uid = getUidUser()
                    data['password'] = encrypt(password)
                    data['uid'] = uid
                    if ('group' in data):
                        groups = data['group']
                        for i in range(0, len(groups)):
                            add_user_group(
                                getGroupNameById(groups[i]), username)
                        serializerUser = UserSerializerPost(data=data)
                    else:
                        serializerUser = UserSerializerPostWithoutGroupAndPermission(
                            data=data)
                    gid = getUidGroup()
                    groupname = {"groupname": username}
                    groupname['gid'] = gid
                    groupname['createdBySystem'] = True
                    print(groupname)
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
                        return JsonResponse(serializerUser.errors, status=400)
                    # provide a Json Response with the necessary error information
                    return JsonResponse(serializerUser.errors, status=400)
                else:
                    msg = "useradd: user '"+username + "' already exists"
                    return JsonResponse({"msg": msg}, status=400)

# API to delete group

# done✔


@csrf_exempt
def delete_user(request, id):
    msg=""
    if (request.method == 'DELETE'):
        user = User.objects.get(id=id)
        group = Group.objects.filter(groupname=user.username)
        if deleteUser(user.username) == 0:
            user.delete()
            group.delete()
            msg = "delete succesfully"
        else:
            msg="delete failed"
        # return a no content response.
        return JsonResponse({"msg": msg})


# API to update user
# done✔


@csrf_exempt
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
            if username_exists(newusername) and newusername != oldusername:
                msg = f"newusername  exists."
                return JsonResponse({"msg": msg})
            else:
                userObject.username = newusername
                if checkSameGroupnameWithUsername(oldusername):
                    changeUsername(newusername, oldusername)
                    change_groupname_username(oldusername, newusername)
                    msg = "updated groupname and username succesfully"
                else:
                    changeUsername(newusername, oldusername)
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
                delete_user_group(k['fields']['groupname'], newusername)
            for m in data['group']:
                gg = Group.objects.get(id=m)
                add_user_group(gg.groupname, newusername)
            userObject.group.set(userJson['group'])
        userObject.save()
    return JsonResponse({"data": data, "msg": msg})


# API de create permission
# done✔

@csrf_exempt
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


@csrf_exempt
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


# API1 to authentification


@csrf_exempt
def authentification(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        # run the command to check if the provided credentials are valid
        result = subprocess.run(["su", "-c", "id", username], input=password,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # result = subprocess.run(["su", username], input=password, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # check if the command succeeded (return code 0)
        if result.returncode == 0:
            msg = "Authentication successful!"
            return JsonResponse({"msg": msg})
        else:
            msg = "Authentication failed."
            return JsonResponse({"msg": msg})

# API2 to authentification


@csrf_exempt
def authentifacation2(request):
    msg = ''
    if (request.method == 'POST'):
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        if authenticate(username, password):
            msg = "Authentication successful!"
            return JsonResponse({"msg": msg})
        else:
            msg = "Authentication failed."
            return JsonResponse({"msg": msg})
