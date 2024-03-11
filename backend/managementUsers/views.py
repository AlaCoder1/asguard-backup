from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_protect

from .serializers import *
from backend.managementGroup.serializers import *
from backend.managementGroup.views import *
from backend.subscription.views import *
# Version without SSh connection
from .functions import *
from backend.managementGroup.functions import *
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
import requests
from backend.LdapServer.models import ADServer
from backend.LdapServer.serializers import ADServerSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
import ldap

from drf_yasg.utils import swagger_auto_schema
import ast




@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF Users",
                     operation_description="API TO GET LIST OF Users",)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllUsers(request):
    list_users = []
    if (request.method == 'GET'):
        users = User.objects.all()
        print(users)
        userDict = serializers.serialize("json", users)
        res = json.loads(userDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('password')
            res[i]['fields']['id'] = id
            list_users.append(res[i]['fields'])
        return list_users
        #return JsonResponse(list_users, safe=False)




@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET USER BY ID",
                     operation_description="API TO GET USER BY ID",)

# API to get one user
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
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


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO Create New USER",
                     operation_description="API TO Create New USER",)



@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createUser(request):
    msg = ''
    email_founded = False
    if request.method == 'POST':
        data = request.data
        username = data['username']
        password = data['password']
        organisation = organization.objects.get(id=1)
        data['organisation'] = organisation.id
        email = data['email']
        
        if data['password_ad'] != "":
            id_server = data['id_server']
            ad_server = ADServer.objects.get(id=id_server)
            if ad_server:
                try:
                    is_password_matched = check_password(data['password_ad'],ad_server.bind_user_password)
                    if is_password_matched:
                        ldap_uri = f"{'ldaps' if ad_server.ssl_tls_activation else 'ldap'}://{ad_server.server_url}:{ad_server.port}"
                        ldap_conn = ldap.initialize(ldap_uri)
                        ldap_conn.simple_bind_s(ad_server.bind_user_dn,data['password_ad'])
                        
                        # Retrieve user details from AD
                        result = ldap_conn.search_s(ad_server.search_base, ldap.SCOPE_SUBTREE, "(objectClass=user)", ['userPrincipalName'])
                        user_principal_names = [
                            entry[1].get('userPrincipalName', [])[0].decode('utf-8')
                            for entry in result
                            if 'userPrincipalName' in entry[1]
                        ]
                       
                        # Check if the email exists in the list of userPrincipalNames
                        if email.lower() in [user.lower() for user in user_principal_names]:
                            email_founded=True

                        # Close LDAP connection
                       
                        ldap_conn.unbind()
                    else:
                        return JsonResponse({'msg': "please verify you password of Ldap server"},status=400)   
                except ldap.LDAPError as e:
                    return JsonResponse({'msg': "Error connecting to Active Directory"},status=400)  
            else:    
                    return JsonResponse({'msg': "This AD Server is not Exist"},status=400)  
        exist_email = User.objects.filter(email=email).exists()
        print({"exist_email":exist_email})
        if User.objects.filter(email=email).exists():
            return JsonResponse({"msg": "email allready exist"}, status=400)
        else:
            if validInput(username) and validPassword(password):
                # Execute the command on the remote machine
                error_useradd, stdout_password, stderr_password  = addUser(username, password)
                print({"error_useradd":error_useradd})
                print({"stdout_password": stdout_password.decode('utf-8')})
                print({"stderr_password": stderr_password.decode('utf-8')})

                # Convert the stderr stream to a string
                if error_useradd == '':
                    addMailSpool(username)
                    if email_founded:
                        msg = username + " added successfully with their email in AD"
                        data['id_server_id']= ad_server.id
                    else:
                        msg = username + " added successfully with simple System email "
                    uid = getUidUser()
                    data['password'] = make_password(data['password'])
                    data['uid'] = uid
                    if 'group' in data:
                        groups = data['group']
                        print({"groups": groups})
                        for i in range(0, len(groups)):
                            add_user_group(getGroupNameById(groups[i]), username)
                        print({"data":data})
                        serializerUser = UserSerializerPost(data=data)
                        gid = getUidGroup()
                        groupname = {"groupname": username}
                        groupname['gid'] = gid
                        groupname['created_by_system'] = True
                        serializerGroup = GroupSerializer(data=groupname)

                        # Check if the sent information is okay
                        if serializerUser.is_valid():
                            if serializerGroup.is_valid():
                                # If okay, save it on the database
                                serializerUser.save()
                                serializerGroup.save()
                                # Provide a Json Response with the data that was saved
                                return JsonResponse({"msg": msg}, status=201)
                            # Provide a Json Response with the necessary error information
                            error_message_Group = next(iter(serializerGroup.errors.values()))[0]
                            return JsonResponse({"msg":error_message_Group}, status=400)
                        # Provide a Json Response with the necessary error information
                        error_message = next(iter(serializerUser.errors.values()))[0]
                        return JsonResponse({"msg":error_message}, status=400)
                    else:
                       
                        serializerUser = UserSerializerPostWithoutGroupAndPermission(data=data)
                        gid = getUidGroup()
                        groupname = {"groupname": username}
                        groupname['gid'] = gid
                        groupname['created_by_system'] = True
                        serializerGroup = GroupSerializer(data=groupname)

                        # Check if the sent information is okay
                        if serializerUser.is_valid():
                            if serializerGroup.is_valid():
                                # If okay, save it on the database
                                serializerUser.save()
                                serializerGroup.save()
                                # Provide a Json Response with the data that was saved
                                return JsonResponse({"msg": msg}, status=201)
                            # Provide a Json Response with the necessary error information
                            return JsonResponse(serializerGroup.errors, status=400)
                        # Provide a Json Response with the necessary error information
                        return JsonResponse(serializerUser.errors, status=400)
                else:
                    return JsonResponse({"msg": error_useradd}, status=400)
            else:
                msg = "invalid password"
                return JsonResponse({"msg": msg}, status=201)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE USER",
                     operation_description="API TO DELETE USER",)

# API to delete group
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user(request, id):
    msg = ""
    if (request.method == 'DELETE'):
        user = User.objects.get(id=id)
        group = Group.objects.filter(groupname=user.username)
        print({"username":user.username})
        # # Execute the command on the remote machine
        stdout, stderr = deleteUser(user.username)
        # # convert the stderr stream to a string
        if stderr == "":
            user.delete()
            group.delete()
            msg = "delete succesfully"
        else:
            msg = stderr
        # return a no content response.
        return JsonResponse({"msg": msg})


@swagger_auto_schema(
    method='PUT',
    request_body=UserSerializerPost,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE User",
    operation_description="This API help us to update User added ",
)

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def modifyUser(request, id):
    if (request.method == 'PUT'):
        userById = User.objects.filter(id=id)
        userDict = serializers.serialize("json", userById)
        res = json.loads(userDict)
        print(res)
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
        
        email_founded=False
        if data['password_ad'] != "":
            id_server = data['id_server']
            ad_server = ADServer.objects.get(id=id_server)
            try:
                is_password_matched = check_password(data['password_ad'],ad_server.bind_user_password)
                if is_password_matched:
                    ldap_uri = f"{'ldaps' if ad_server.ssl_tls_activation else 'ldap'}://{ad_server.server_url}:{ad_server.port}"
                    ldap_conn = ldap.initialize(ldap_uri)
                    ldap_conn.simple_bind_s(ad_server.bind_user_dn,data['password_ad'])
                    
                    # Retrieve user details from AD
                    result = ldap_conn.search_s(ad_server.search_base, ldap.SCOPE_SUBTREE, "(objectClass=user)", ['userPrincipalName'])
                    user_principal_names = [
                        entry[1].get('userPrincipalName', [])[0].decode('utf-8')
                        for entry in result
                        if 'userPrincipalName' in entry[1]
                    ]

                    # Check if the email exists in the list of userPrincipalNames
                    if data['email'].lower() in [user.lower() for user in user_principal_names]:
                        newmail = data['email']
                        email_founded=True
                    # Close LDAP connection
                    ldap_conn.unbind()
                else:
                    return JsonResponse({'msg': "please verify you password of Ldap server"},status=400)   
            except ldap.LDAPError as e:
                return JsonResponse({'msg': "Error connecting to Active Directory"},status=400)  
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
                msg = f"username or email already Used."
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
                if email_founded:
                    userObject.id_server=ad_server
                else:
                    userObject.id_server=None
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




@swagger_auto_schema(
    method='PUT',
    request_body=UserSerializerGet,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE Change Password User By Admin",
    operation_description="This API help us to update User's password added By admin",
)
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
            print({"stderr":stderr})
            print({"stdout":stdout})
            # check if password change was successful
            if stderr == "":
                userObject.password = make_password(new_password)
                userObject.save()
                print("Password change successful")
            else:
                print(f"Error changing password: {stderr}")
        return JsonResponse(serializer.data, status=201)


@swagger_auto_schema(
    method='PUT',
    request_body=UserSerializerPost,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE Change Password User ",
    operation_description="This API help us to update User's password added ",
)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def changePassword(request, id):
    msg = ""
    if (request.method == 'PUT'):
            userObject = User.objects.get(id=id)
        # if userObject.is_verified == True:
        #     return JsonResponse({"msg": "your account is verified"})
        # else:
            data = request.data
            # current_password = data['current_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']
            # if check_password(current_password, userObject.password):
            #     print('Passwords match!')
            if new_password != confirm_password:
                print("Passwords do not match. Please try again.")
                msg = "Passwords do not match. Please try again."
            else:
                stdout, stderr = resetPW (userObject.username,new_password )
                print({"str":stderr})
                print({"std":stdout})
                # check if password change was successful
                if stderr == "":
                    userObject.password = make_password(new_password)
                    userObject.is_verified = True
                    userObject.save()
                    print("Password change successful")
                    msg = "Password change successful"
                    status=200

                else:
                    msg = f"Error changing password"
                    status=400

            # else:
            #     print('Passwords do not match')
            #     msg = 'Passwords do not match'
            #     status=400
            return JsonResponse({"msg": msg},status=status)





@swagger_auto_schema(
    method='POST',
    request_body=PermissionSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD Permission ",
    operation_description="This API help us to ADD Permission",
)
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