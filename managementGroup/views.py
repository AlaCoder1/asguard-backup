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
import grp
import mysql.connector  
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
        groupname=data['groupname']
        if(validInput(groupname)):
            if addGroup(groupname) == 0:
                msg='group added succesfully'
                gid = getUidGroup()
                data['gid']=gid
                serializer = GroupSerializer(data=data)
                # check if the sent information is okay
                if(serializer.is_valid()):
                    # if okay, save it on the database
                    serializer.save()
                    # provide a Json Response with the data that was saved
                    return JsonResponse({"msg":msg}, status=201)
                # provide a Json Response with the necessary error information
                return JsonResponse(serializer.errors, status=400)
            else:
                msg = "groupadd: group '"+groupname+ "' already exists"
                return JsonResponse({"msg":msg}, status=201)
            
### function to test if groupname exit
def group_exists(group_name):
    try:
        grp.getgrnam(group_name)
        return True
    except KeyError:
        return False

### API to get all groups   

    
@csrf_exempt
def getAllGroups(request):
    if(request.method == 'GET'):
        print(getAllUsersFromGroup(6))
        result = subprocess.run(["getent", "group"], capture_output=True)
        output = result.stdout.decode()
        tab_groups= []
        list_group = []
        for line in output.split("\n"):
            fields = line.split(":")
            if(len(fields) > 2):
                groupname = fields[0]
                gid = fields[2]
                if int(gid) >=1000:
                    tab_groups.append({"groupname": groupname, "gid": gid})
                    list_group.append(groupname+":"+gid)
        # get all groups
        # val = [tuple(line.split(":")[:3]) for line in list_group]
        # print(val)
        # # a = [('terry', '1000'), ('sudo', '1002'), ('mysql', '1019'), ('amani', '1020'), ('heni', '1001')]
        # a = ('terry', '1000')
        # # Create the cursor and execute the INSERT statement
        # cursor = cnx.cursor()
        # query = "INSERT INTO Group (groupname , gid) VALUES (%s, %s)"
        # try:
        #     cursor.execute(query, a)
        #     # Commit the changes to the database
        #     cnx.commit()
        #     print("Data inserted successfully")
        # except Exception as e:
        #     # Rollback in case there is any error
        #     cnx.rollback()
        #     print("Error: ", e)
        # # cursor.executemany(query, a)

        # # Commit the changes to the database
        # # cnx.commit()
        # # Close the cursor and connection
        # cursor.close()
        # cnx.close()
        # serialize the groups data
        serializer = GroupSerializer(tab_groups, many=True)
        # return a Json response
        return JsonResponse(serializer.data,safe=False)

### API to delete group
@csrf_exempt   
def deleteGroup(request):
    if(request.method == 'DELETE'):
        # delete group
        data = json.loads(request.body)
        groupname = data['groupname'] 
        delete_group(groupname)
        # id = data['id']
        # group = Group.objects.filter(id=id)
        # group.delete()
        # return a no content response.
        return HttpResponse("delete succesfully",status=200) 
    
### API to change groupname
@csrf_exempt
def change_groupname(request):
    msg=''
    if(request.method == 'PUT'):
        # parse the incoming information
        data = json.loads(request.body)
        oldgroupname =data['oldgroupname']
        Newgroupname =data['Newgroupname']
        if validInput(oldgroupname):
            if group_exists(oldgroupname):
                if validInput(Newgroupname):
                    if group_exists(Newgroupname):
                        msg = f"Username {Newgroupname} exists."
                        return JsonResponse({"msg":msg})
                    else:
                        changeGroupname(oldgroupname,Newgroupname)
                        msg="updated succesfully"
                        return JsonResponse({"msg":msg})
                else:
                    msg = "invalid "+Newgroupname
                    return JsonResponse({"msg":msg})
            else:
                msg = f"Username {oldgroupname} does not exist."
                return JsonResponse({"msg":msg})
        else:
            msg = "invalid "+oldgroupname
            return JsonResponse({"msg":msg})
    
### function to get UID from system
def getLastGroupName():
    return subprocess.run(["getent", "group"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[0]

### function de get id group
def getUidGroup():
    return subprocess.run(["getent", "group"], capture_output=True).stdout.decode().strip().split('\n')[-1].split(':')[2]

### function de get all groupname by id
def getGroupNameById(pk):
        group = Group.objects.get(id=pk)
        return str(group)
    

from dms.settings import DATABASES
cnx  = mysql.connector.connect(
        host=DATABASES['default']['HOST'],
        user=DATABASES['default']['USER'],
        password=DATABASES['default']['PASSWORD'],
        database=DATABASES['default']['NAME']
    )
def getAllUsersFromGroup(id):
    mycursor = cnx.cursor()
    sql  = "SELECT username FROM `User_group` INNER JOIN User on User_group.user_id = User.id where User_group.group_id = %s"
    adr = (id, )
    mycursor.execute(sql, adr)
    myresult = mycursor.fetchall()
    list = []
    for x in myresult:
            list.append(x[0])

    return(list)
    
#change groupname if groupname=username
def change_groupname_username(oldgroupname,Newgroupname):
        msg=''
        if validInput(oldgroupname):
            if group_exists(oldgroupname):
                if validInput(Newgroupname):
                    if group_exists(Newgroupname):
                        msg = f"Username {Newgroupname} exists."
                        return JsonResponse({"msg":msg})
                    else:
                        changeGroupname(oldgroupname,Newgroupname)
                        reporter = Group.objects.get(groupname=oldgroupname)
                        reporter.groupname =Newgroupname
                        reporter.save()
                        msg="updated succesfully"
                        return JsonResponse({"msg":msg})
                else:
                    msg = "invalid "+Newgroupname
                    return JsonResponse({"msg":msg})
            else:
                msg = f"Username {oldgroupname} does not exist."
                return JsonResponse({"msg":msg})
        else:
            msg = "invalid "+oldgroupname
            return JsonResponse({"msg":msg})
        
        
