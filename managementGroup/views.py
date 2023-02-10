from django.core import serializers
from dms.settings import DATABASES
from django.http import JsonResponse, HttpResponse
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.parsers import JSONParser
from django.core import serializers
from .functions import *
# Create your views here.


# API to get all groups

#done✔
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
        # print(getAllUsersFromGroup(6))
        # return a Json response
        return JsonResponse(list_group, safe=False)



# API to get one group

#done✔
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
@csrf_exempt
def createGroup(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        groupname = data['groupname']
        if (validInput(groupname)):
            if addGroup(groupname) == 0:
                msg = 'group added succesfully'
                gid = getUidGroup()
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
                msg = "groupadd: group '"+groupname + "' already exists"
                return JsonResponse({"msg": msg}, status=201)



# API to delete group

#done✔
@csrf_exempt
def deleteGroup(request,id):
    if (request.method == 'DELETE'):
        group = Group.objects.get(id=id)
        if delete_group(group.groupname)==0:
            group.delete()
            msg = "delete succesfully"
        # return a no content response.
        return JsonResponse({"msg": msg})


# API to update group


def updateGroup(request,id):
    return True

# API to change groupname

from managementUsers.models import *
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
        if validInput(oldgroupname):
            if group_exists(oldgroupname):
                if validInput(Newgroupname):
                    if group_exists(Newgroupname):
                        msg = f"Username {Newgroupname} exists."
                        return JsonResponse({"msg": msg})
                    else:
                        change_groupname(oldgroupname, Newgroupname)
                        msg = "updated succesfully"
                        group.groupname=Newgroupname
                        group.save()
                        return JsonResponse({"msg": msg})
                else:
                    msg = "invalid "+Newgroupname
                    return JsonResponse({"msg": msg})
            else:
                msg = f"Username {oldgroupname} does not exist."
                return JsonResponse({"msg": msg})
        else:
            msg = "invalid "+oldgroupname
            return JsonResponse({"msg": msg})





def getAllUsersFromGroup(id):
    mycursor = cnx.cursor()
    sql = "SELECT username FROM `User_group` INNER JOIN User on User_group.user_id = User.id where User_group.group_id = %s"
    adr = (id, )
    mycursor.execute(sql, adr)
    myresult = mycursor.fetchall()
    list = []
    for x in myresult:
        list.append(x[0])
    return (list)

# function to change groupname if groupname=username


def change_groupname_username(oldgroupname, Newgroupname):
    msg = ''
    if validInput(oldgroupname):
        if group_exists(oldgroupname):
            if validInput(Newgroupname):
                if group_exists(Newgroupname):
                    msg = f"Username {Newgroupname} exists."
                    return JsonResponse({"msg": msg})
                else:
                    change_groupname(oldgroupname, Newgroupname)
                    reporter = Group.objects.get(groupname=oldgroupname)
                    reporter.groupname = Newgroupname
                    reporter.save()
                    msg = "updated succesfully"
                    return JsonResponse({"msg": msg})
            else:
                msg = "invalid "+Newgroupname
                return JsonResponse({"msg": msg})
        else:
            msg = f"Username {oldgroupname} does not exist."
            return JsonResponse({"msg": msg})
    else:
        msg = "invalid "+oldgroupname
        return JsonResponse({"msg": msg})
