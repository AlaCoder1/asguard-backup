from backend.managementUsers.models import *
from django.http import JsonResponse
from .models import *
from .serializers import *
import json
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from .functions import *
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING
# Constants
CONSTANT_GROUPE_NAME= _('Groupe name')
CONSTANT_GROUPE_DESCRIPTION= _('Groupe description')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")

# Error messages
ERROR_MESSAGES_INVALID = _("Invalid")
ERROR_MESSAGES_EXISTANT = _("Already exist")



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve all user groups",
    responses={200: openapi.Response("List of groups", GroupSerializer(many=True))}
)
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

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a group by ID",
    responses={200: openapi.Response("Group details", GroupSerializer())}
)
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

@swagger_auto_schema(
    method='post',
    operation_description="Create a new group",
    request_body=GroupSerializer,
    responses={
        201: openapi.Response("Group created", GroupSerializer()),
        400: "Validation Error"
    }
)
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
                    msg = f"{groupname} {SUCCESS_MESSAGES_CREATING}"
                    return JsonResponse({"msg": msg}, status=201)
                return JsonResponse(serializer.errors, status=400)
            else:
                msg = stderr
        else:
            msg =f"{CONSTANT_GROUPE_NAME} {ERROR_MESSAGES_INVALID}"
            return JsonResponse({"msg": msg}, status=201)
    return JsonResponse({"msg": msg}, status=201)


@swagger_auto_schema('DELETE', responses={200: 'Deleted', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE Group",)
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
            msg = f"{group.groupname} {SUCCESS_MESSAGES_DELETING}"
        else:
            msg = stderr
        return JsonResponse({"msg": msg})

@swagger_auto_schema(
    method='PUT',
    operation_summary="Change Group Name and Description",
    operation_description=(
        "This API allows updating the name and description of an existing group. "
        "It validates the new group name before making changes."
    ),
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['Newgroupname', 'description'],
        properties={
            'Newgroupname': Schema(
                type=TYPE_STRING,
                description="The new name for the group.",
                example="NewGroupName123"
            ),
            'description': Schema(
                type=TYPE_STRING,
                description="The updated description of the group.",
                example="Updated group description."
            ),
        },
    ),
    responses={
        200: "Group name and description updated successfully.",
        400: "Invalid input or group already exists.",
        404: "Group not found.",
    },
)
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
            if oldgroupname == Newgroupname:
                group.description = description
                group.save()
                msg = f"{CONSTANT_GROUPE_DESCRIPTION} {SUCCESS_MESSAGES_UPDATING}"
                return JsonResponse({"msg": msg})
            elif group_exists(Newgroupname):
                msg = f"{Newgroupname} {ERROR_MESSAGES_EXISTANT}"
                return JsonResponse({"msg": msg})
            else:
                change_groupname(oldgroupname, Newgroupname)
                msg = f"{CONSTANT_GROUPE_NAME} {SUCCESS_MESSAGES_UPDATING}"
                group.groupname = Newgroupname
                group.description = description
                group.save()
                return JsonResponse({"msg": msg})
        else:
            msg =f"{ERROR_MESSAGES_INVALID} {Newgroupname}"
            return JsonResponse({"msg": msg})