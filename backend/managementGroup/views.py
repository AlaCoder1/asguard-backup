from backend.managementUsers.models import *
from django.http import JsonResponse
from .models import *
from .serializers import *
import json
from rest_framework.authentication import SessionAuthentication
from .functions import *
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
# Create your views here.


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getAllGroups(request):
    """Get all group from database"""
    list_group = []
    if (request.method == 'GET'):
        groups = Group.objects.filter(created_by_system=0)
        groupDict = serializers.serialize("json", groups)
        res = json.loads(groupDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('created_by_system')
            res[i]['fields']['id'] = id
            list_group.append(res[i]['fields'])
        return JsonResponse(list_group, safe=False)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def getGroup(request, id):
    """Get group by ID"""
    if (request.method == 'GET'):
        group = Group.objects.get(id=id)
        groupDict = group.__dict__
        groupDict.pop("_state")
        return JsonResponse(groupDict)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createGroup(request):
    """Create a group"""
    msg = ''
    if (request.method == 'POST'):
        data = request.data
        groupname = data['groupname']
        if (validInput(groupname)):
            _, stderr = addGroup(groupname)
            if stderr == "":
                gid = getUidGroup()
                data['gid'] = gid
                serializer = GroupSerializer(data=data)
                if (serializer.is_valid()):
                    serializer.save()
                    msg = groupname+" added sucessfully"
                    return JsonResponse({"msg": msg}, status=201)
                return JsonResponse(serializer.errors, status=400)
            else:
                msg = stderr
        else:
            msg = "groupname invalid"
            return JsonResponse({"msg": msg}, status=201)
    return JsonResponse({"msg": msg}, status=201)


# API to delete group
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def deleteGroup(request, id):
    """Delete a group"""
    msg = ''
    if (request.method == 'DELETE'):
        group = Group.objects.get(id=id)
        _, stderr = delete_group(group.groupname)
        if stderr == "":
            group.delete()
            msg = "delete succesfully"
        else:
            msg = stderr
        return JsonResponse({"msg": msg})

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def changeGroupname(request, id):
    """Change groupname in database"""
    msg = ''
    if (request.method == 'PUT'):
        group = Group.objects.get(id=id)
        groupDict = group.__dict__
        data = request.data
        oldgroupname = groupDict['groupname']
        Newgroupname = data['Newgroupname']
        description = data['description']
        if validInput(Newgroupname):
            if group_exists(Newgroupname):
                msg = f"Group {Newgroupname} exists."
                return JsonResponse({"msg": msg})
            else:
                change_groupname(oldgroupname, Newgroupname)
                msg = "updated succesfully"
                group.groupname = Newgroupname
                group.description = description
                group.save()
                return JsonResponse({"msg": msg})
        else:
            msg = "invalid "+Newgroupname
            return JsonResponse({"msg": msg})