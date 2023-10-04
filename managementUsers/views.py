from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_protect

from .serializers import *
from managementGroup.serializers import *
from managementGroup.views import *
from subscription.views import *
# Version without SSh connection
from .functions import *
# end Version without SSh connection
# Version SSh connection
# from .remoteFunctions import *
# end Version SSh connection
import json
from rest_framework.parsers import JSONParser
from django.core import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

# API to get all users


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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
        # return list_users
        return JsonResponse(list_users, safe=False)


# API to get one user
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createUser(request):
    msg = ''
    if (request.method == 'POST'):
        if has_subscription():
            if is_valid():
                # test index of feature by plan e.g 1,2 index of management users in our BD
                if if_subscribed([1]):
                    # parse the incoming information
                    data = request.data
                    username = data['username']
                    password = data['password']
                    organisation = organization.objects.get(id=1)
                    print({"organisation": organisation.id})
                    data['organisation'] = organisation.id
                    if (validInput(username)):
                        if (validInput(password)):
                            # Execute the command on the remote machine
                            stdin, stdout, stderr = addUser(
                                username, password)
                            addMailSpool(username)
                            # convert the stderr stream to a string
                            error_str = stderr.read().decode('utf-8')
                            if error_str == "":
                                msg = username+" added sucessfully"
                                uid = getUidUser()
                                data['password'] = make_password(
                                    data['password'])
                                data['uid'] = uid

                                if ('group' in data):
                                    groups = data['group']
                                    for i in range(0, len(groups)):
                                        add_user_group(
                                            getGroupNameById(groups[i]), username)
                                    serializerUser = UserSerializerPost(
                                        data=data)
                                    gid = getUidGroup()
                                    groupname = {"groupname": username}
                                    groupname['gid'] = gid
                                    groupname['createdBySystem'] = True
                                    serializerGroup = GroupSerializer(
                                        data=groupname)
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
                                    serializerUser = UserSerializerPostWithoutGroupAndPermission(
                                        data=data)
                                    gid = getUidGroup()
                                    groupname = {"groupname": username}
                                    groupname['gid'] = gid
                                    groupname['createdBySystem'] = True
                                    serializerGroup = GroupSerializer(
                                        data=groupname)
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
                else:
                    return JsonResponse({"msg": "your plan dosn't satisfy your requerement"}, status=400)
            else:
                return JsonResponse({"msg": "your subscription has expired"}, status=400)
        else:
            return JsonResponse({"msg": "your havn't a subscription"}, status=400)


# API to delete group
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def delete_user(request, id):
    msg = ""
    if (request.method == 'DELETE'):
        user = User.objects.get(id=id)
        group = Group.objects.filter(groupname=user.username)
        # Execute the command on the remote machine
        stdin, stdout, stderr = deleteUser(user.username)
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
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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
        data = request.data
        newusername = data['username']
        newfullname = data['fullname']
        newmail = data['email']
        newrole = data['role']
        userObject = User.objects.get(id=id)
        user = userObject.__dict__
        print({"user": user})
        print({"userJson": userJson})
        print({"userObject.username": userObject.username})
        user['group'] = userJson['group']
        # user['permission'] = userJson['permission']
        if validInput(newusername):
            if username_exists(newusername) and newusername != oldusername:
                msg = f"newusername  exists."
                return JsonResponse({"msg": msg})
            else:
                userObject.username = newusername
                print("checkSameGroupnameWithUsername")
                checkSameGroupnameWithUsername(oldusername)
                if checkSameGroupnameWithUsername(oldusername):
                    changeUsername(newusername, oldusername)
                    change_groupname_username(oldusername, newusername)
                    msg = "updated groupname and username succesfully"
                else:
                    changeUsername(newusername, oldusername)
                    msg = "updated only username succesfully"
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
        else:
            msg = "invalid "+newusername
        
        return JsonResponse({"data": data, "msg": msg})





# API to change password user


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def changePasswordByAdmin(request, id):
    if (request.method == 'PUT'):
        userObject = User.objects.get(id=id)
        print({'username': userObject.username})
        data = request.data
        # instanciate with the serializer
        serializer = UserSerializerGet()
        # current_password = data['current_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        if new_password != confirm_password:
            print("Passwords do not match. Please try again.")
            return JsonResponse({"msg": "Passwords do not match. Please try again."})
        else:
            # run 'passwd' command to change password
            stdout, stderr = changePW_byAdmin(
                new_password, userObject.username)
            # check if password change was successful
            if stdout.channel.recv_exit_status() == 0:
                userObject.password = make_password(new_password)
                userObject.save()
                print("Password change successful")
            else:
                print(f"Error changing password: {stderr.read().decode()}")
        return JsonResponse(serializer.data, status=201)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def changePassword(request, id):
    msg = ""
    if (request.method == 'PUT'):
        userObject = User.objects.get(id=id)
        if userObject.is_verified == True:
            return JsonResponse({"msg": "your account is verified"})
        else:
            # print({'username': userObject.username})
            # print({'vérifier': userObject.is_verified})
            # print({'password': userObject.password})
            data = request.data
            current_password = data['current_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']
            if check_password(current_password, userObject.password):
                print('Passwords match!')
                if new_password != confirm_password:
                    print("Passwords do not match. Please try again.")
                    msg = "Passwords do not match. Please try again."
                    return JsonResponse({"msg": "Passwords do not match. Please try again."})
                else:
                    # run 'passwd' command to change password
                    stdin, stdout, stderr = changePW(
                        current_password, new_password, userObject.username)
                    # check if password change was successful
                    if stdout.channel.recv_exit_status() == 0:
                        userObject.password = make_password(new_password)
                        userObject.is_verified = True
                        userObject.save()
                        print("Password change successful")
                        msg = "Password change successful"
                    else:
                        print(
                            f"Error changing password: {stderr.read().decode()}")
                        msg = f"Error changing password: {stderr.read().decode()}"
            else:
                print('Passwords do not match')
                msg = 'Passwords do not match'

            return JsonResponse({"msg": msg})


# API de create permission
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def addPermission(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
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