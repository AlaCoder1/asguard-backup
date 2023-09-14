from managementUsers.models import *
from django.http import JsonResponse
from .models import *
from .serializers import *
import json
from rest_framework.parsers import JSONParser
from rest_framework.authentication import SessionAuthentication
from .functions import *
from .remoteFunctions import *
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from authentification.authentication import JWTAuthentication
from django.core import serializers
# Create your views here.


# API to get all groups
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getGroup(request, id):
    if (request.method == 'GET'):
        group = Group.objects.get(id=id)
        groupDict = group.__dict__
        groupDict.pop("_state")
        # return a no content response.
        return JsonResponse(groupDict)


# API to create group
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createGroup(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
        groupname = data['groupname']
        if (validInput(groupname)):
            if addGroup(groupname) == 0:
                msg = groupname+" added sucessfully"
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
                msg = "Failed to add group."
        else:
            msg = "groupname invalid"
            return JsonResponse({"msg": msg}, status=201)
    return JsonResponse({"msg": msg}, status=201)


# API to delete group
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteGroup(request, id):
    msg = ''
    if (request.method == 'DELETE'):
        group = Group.objects.get(id=id)
        if delete_group(group.groupname) == 0:
            group.delete()
            msg = "delete succesfully"
        else:
            msg = "delete failed"
        # return a no content response.
        return JsonResponse({"msg": msg})


# API to change groupname
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def changeGroupname(request, id):
    msg = ''
    if (request.method == 'PUT'):
        group = Group.objects.get(id=id)
        groupDict = group.__dict__
        # parse the incoming information
        data = request.data
        oldgroupname = groupDict['groupname']
        Newgroupname = data['Newgroupname']
        if validInput(Newgroupname):
            if group_exists(Newgroupname):
                msg = f"Username {Newgroupname} exists."
                return JsonResponse({"msg": msg})
            else:
                change_groupname(oldgroupname, Newgroupname)
                msg = "updated succesfully"
                group.groupname = Newgroupname
                group.save()
                return JsonResponse({"msg": msg})
        else:
            msg = "invalid "+Newgroupname
            return JsonResponse({"msg": msg})
