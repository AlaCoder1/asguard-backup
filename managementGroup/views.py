from django.core import serializers
from dms.settings import DATABASES
from django.http import JsonResponse
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.parsers import JSONParser
from django.core import serializers
from .functions import *
from .remoteFunctions import *
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from managementUsers.authentication import JWTAuthentication
# Create your views here.


# API to get all groups

#done✔
# @api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def getAllGroups(request):
    list_group = []
    if (request.method == 'GET'):
        groups = Group.objects.filter(createdBySystem=0)
        groupDict = serializers.serialize("json", groups)
        res = json.loads(groupDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('createdBySystem')
            res[i]['fields']['id'] = id
            list_group.append(res[i]['fields'])

        # return a Json response
        return JsonResponse(list_group, safe=False)



# API to get one group

#done✔
# @api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def getGroup(request, id):
    if (request.method == 'GET'):
        group = Group.objects.get(id=id)
        groupDict = group.__dict__
        groupDict.pop("_state")
        # return a no content response.
        return JsonResponse(groupDict)


# API to create group

#done✔
# @api_view(['POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def createGroup(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        groupname = data['groupname']
        if (validInput(groupname)):
            # command = "groupadd "+groupname

            # Execute the command on the remote machine
            # stdin, stdout, stderr = settings.SSH.execute_command(command)
            stdin, stdout, stderr = addRemoteGroup(groupname)
            # convert the stderr stream to a string
            error_str = stderr.read().decode('utf-8')

            if error_str=="":
                msg=groupname+" added sucessfully"
                gid = getRemoteGidGroup()
                data['gid'] = gid
                serializer = GroupSerializer(data=data)
                # check if the sent information is okay
                if (serializer.is_valid()):
                    # if okay, save it on the database
                    serializer.save()
                    # provide a Json Response with the data that was saved
                    return JsonResponse({"msg": msg}, status=201)
                # provide a Json Response with the necessary error information
                return JsonResponse(serializer.errors, status=400)
            else:
                msg=error_str
        else:
            msg="groupname invalid"
            return JsonResponse({"msg": msg}, status=201)
    return JsonResponse({"msg": msg}, status=201)




# API to delete group

#done✔
# @api_view(['DELETE'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def deleteGroup(request,id):
    msg=''
    if (request.method == 'DELETE'):
        group = Group.objects.get(id=id)
        
        # Execute the command on the remote machine
        stdin, stdout, stderr = deleteRemoteGroup(group.groupname)
        # convert the stderr stream to a string
        error_str = stderr.read().decode('utf-8')
        print(stdout.read().decode('utf-8'))
        if error_str=="":
            group.delete()
            msg = "delete succesfully"
        else:
            msg="delete failed"
        # return a no content response.
        return JsonResponse({"msg": msg})


# API to update group


def updateGroup(request,id):
    return True

# API to change groupname

from managementUsers.models import *
# @api_view(['PUT'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def changeGroupname(request,id):
    msg = ''
    if (request.method == 'PUT'):
        group = Group.objects.get(id=id)
        groupDict = group.__dict__
        # parse the incoming information
        data = json.loads(request.body)
        oldgroupname = groupDict['groupname']
        Newgroupname = data['Newgroupname']

        if validInput(Newgroupname):
            if RemoteGroupExists(Newgroupname):
                msg = f"Username {Newgroupname} exists."
                return JsonResponse({"msg": msg})
            else:
                changeRemoteGroupname(oldgroupname, Newgroupname)
                msg = "updated succesfully"
                group.groupname=Newgroupname
                group.save()
                return JsonResponse({"msg": msg})
        else:
            msg = "invalid "+Newgroupname
            return JsonResponse({"msg": msg})



# function to change groupname if groupname=username


def change_groupname_username(oldgroupname, Newgroupname):
    msg = ''
    if RemoteGroupExists(Newgroupname):
        msg = f"Username {Newgroupname} exists."
        return JsonResponse({"msg": msg})
    else:
        if changeRemoteGroupname(oldgroupname, Newgroupname) ==0:
            reporter = Group.objects.get(groupname=oldgroupname)
            reporter.groupname = Newgroupname
            reporter.save()
            msg = "updated succesfully"
            return JsonResponse({"msg": msg})

   





from django.conf import settings



@csrf_exempt
def createGroupToAnotherMachine(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        groupname = data['groupname']
        if (validInput(groupname)):
            # command = "groupadd "+groupname

            # Execute the command on the remote machine
            # stdin, stdout, stderr = settings.SSH.execute_command(command)
            stdin, stdout, stderr = addRemoteGroup(groupname)
            # convert the stderr stream to a string
            error_str = stderr.read().decode('utf-8')

            if error_str=="":
                msg=groupname+" added sucessfully"
                gid = getRemoteGidGroup()
                data['gid'] = gid
                serializer = GroupSerializer(data=data)
                # check if the sent information is okay
                if (serializer.is_valid()):
                    # if okay, save it on the database
                    serializer.save()
                    # provide a Json Response with the data that was saved
                    return JsonResponse({"msg": msg}, status=201)
                # provide a Json Response with the necessary error information
                return JsonResponse(serializer.errors, status=400)
            else:
                msg=error_str
        else:
            msg="groupname invalid"
            return JsonResponse({"msg": msg}, status=201)
    return JsonResponse({"msg": msg}, status=201)
