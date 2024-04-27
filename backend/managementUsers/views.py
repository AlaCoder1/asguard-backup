from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from .models import *
from .serializers import *
from .functions import *
from backend.managementGroup.serializers import *
from backend.managementGroup.views import *
from backend.managementGroup.functions import *
from backend.subscription.views import *
import json
from django.core import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from backend.LdapServer.models import ADServer
import ldap
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING
from django.conf import settings
from rest_framework import status
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF Users",
                     operation_description="API TO GET LIST OF Users",)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllUsers(request):
    """Get all users from database"""
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

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getUser(request, id):
    """Get user  by ID from database"""
    if (request.method == 'GET'):
        user = User.objects.filter(id=id)
        userDict = serializers.serialize("json", user)
        res_user = json.loads(userDict)
        res_user[0]['fields']['id'] = res_user[0]['pk']
        userJson = res_user[0]['fields']
        
        profile=Profile.objects.filter(user_id=id)
        profile_user=serializers.serialize("json", profile)
        res_profile = json.loads(profile_user)
        res_profile[0]['fields']['id'] = res_profile[0]['pk']
        profileJson = res_profile[0]['fields']
        userJson['profile']=profileJson
        return JsonResponse(userJson)

@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO Create New USER",
                     operation_description="API TO Create New USER",)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def createUser(request):
    """Create user"""
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
                        
                        result = ldap_conn.search_s(ad_server.search_base, ldap.SCOPE_SUBTREE, "(|(userPrincipalName=*)(mail=*))", ['userPrincipalName', 'mail'])
                         # get the list of users email from AD server 
                        user_principal_names = [entry[1]['userPrincipalName'][0].decode('utf-8') for entry in result if 'userPrincipalName' in entry[1]]
                         # get the list of users email from openldap server 
                        user_emails = [entry[1]['mail'][0].decode('utf-8') for entry in result if 'mail' in entry[1]]
                        
                        if email.lower() in [user.lower() for user in user_principal_names] :
                            email_founded = True
                            data['dn_user'] = None

                        if email.lower() in [user.lower() for user in user_emails]: 
                            email_founded = True
                            for entry in result:
                                entry_email = entry[1].get('mail', [''])[0].decode('utf-8').lower()
                                if email.lower() == entry_email:
                                    data['dn_user'] = entry[0]
                                    
                                    break   
                        # Close LDAP connection
                        if not email_founded:
                            return JsonResponse({'msg': f"The email '{email}' does not exist in the directory server"}, status=400)
                        ldap_conn.unbind()
                    else:
                        return JsonResponse({'msg': "please verify your password of directory server"},status=400)   
                    
                except ldap.SERVER_DOWN:
                # LDAP authentication failed
                    return JsonResponse({'msg': 'directory server is unreachable'},status=500)    
                except ldap.LDAPError as e:
                    return JsonResponse({'msg': "Error connecting to directory server"},status=400)  
            else:    
                    return JsonResponse({'msg': "This directory server is not Exist"},status=400)  
       
        if User.objects.filter(email=email).exists():
            return JsonResponse({"msg": "Email allready exist"}, status=400)
        else:
            if validInput(username) and validPassword(password):
                # Execute the command on the remote machine
                error_useradd, stdout_password, stderr_password  = addUser(username, password)
                # Convert the stderr stream to a string
                if error_useradd == '':
                    addMailSpool(username)
                    if email_founded:
                        msg = username + " added successfully with their email in directory server"
                        data['id_server_id']= ad_server.id
                    else:
                        msg = username + " added successfully with simple System email "
                    uid = getUidUser()
                    data['password'] = make_password(data['password'])
                    data['uid'] = uid
                    if 'group' in data:
                        groups = data['group']
                        for i in range(0, len(groups)):
                            add_user_group(getGroupNameById(groups[i]), username)
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
                                Profile.objects.create(user=serializerUser.save())
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
                                Profile.objects.create(user=serializerUser.save())
                                # Provide a Json Response with the data that was saved
                                return JsonResponse({"msg": msg}, status=201)
                            # Provide a Json Response with the necessary error information
                            return JsonResponse(serializerGroup.errors, status=400)
                        # Provide a Json Response with the necessary error information
                        return JsonResponse(serializerUser.errors, status=400)
                    
                else:
                    error_msg = error_useradd.strip()
                    modified_error_msg = " " + error_msg.replace("useradd: ", "")
                    return JsonResponse({"msg": modified_error_msg}, status=400)
            else:
                msg = "invalid password"
                return JsonResponse({"msg": msg}, status=201)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE USER",
                     operation_description="API TO DELETE USER",)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user(request, id):
    """Delete group"""
    msg = ""
    if (request.method == 'DELETE'):
        user = User.objects.get(id=id)
        group = Group.objects.filter(groupname=user.username)
        print({"username":user.username})
        # # Execute the command on the remote machine
        _, stderr = deleteUser(user.username)
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
        data['dn_user'] = None
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
                    result = ldap_conn.search_s(ad_server.search_base, ldap.SCOPE_SUBTREE, "(|(userPrincipalName=*)(mail=*))", ['userPrincipalName', 'mail'])
                         # get the list of users email from AD server 
                    user_principal_names = [entry[1]['userPrincipalName'][0].decode('utf-8') for entry in result if 'userPrincipalName' in entry[1]]
                         # get the list of users email from openldap server 
                    user_emails = [entry[1]['mail'][0].decode('utf-8') for entry in result if 'mail' in entry[1]]

                    if data['email'].lower() in [user.lower() for user in user_principal_names]:
                        newmail = data['email']
                        email_founded=True

                    if data['email'].lower() in [user.lower() for user in user_emails]:
                        newmail = data['email']
                        email_founded=True
                        for entry in result:
                                entry_email = entry[1].get('mail', [''])[0].decode('utf-8').lower()
                                if data['email'].lower() == entry_email:
                                    data['dn_user'] = entry[0]
                                    break   
                    if not email_founded:
                            return JsonResponse({'msg': "The email does not exist in the directory server"}, status=400)
                    ldap_conn.unbind()
                else:
                    return JsonResponse({'msg': "please verify your password of directory server"},status=400)    
            except ldap.SERVER_DOWN:
                # LDAP authentication failed
                return JsonResponse({'msg': 'directory server is unreachable'},status=500)        
            except ldap.LDAPError as e:
                return JsonResponse({'msg': "Error connecting to directory server"},status=400)  
            
        if User.objects.filter(email=data['email']).exclude(id=id).exists():
            return JsonResponse({"msg": "Email allready exist"}, status=400)    
        newmail = data['email']
        newrole = data['role']
        userObject = User.objects.get(id=id)
        user = userObject.__dict__
        user['group'] = userJson['group']
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
                userObject.dn_user=data['dn_user']
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
    
from django.core.exceptions import ValidationError

@swagger_auto_schema(
    method='PUT',
    request_body=ProfileSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UpdateProfile",
    operation_description="This API help us to update profile of user ",
)



@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    if (request.method == 'PUT'):
        try:
            data = request.data
            user = request.user
            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return JsonResponse({"msg": "Email allready exist"}, status=400)          
            userObject = User.objects.get(id=user.id)
            if validInput(user.username):
                if username_exists(data['username']) and  data['username'] != user.username:
                    msg = f"username or email already Used."
                    return JsonResponse({"msg": msg})
                else:
                    if checkSameGroupnameWithUsername(user.username):
                        changeUsername(data['username'], user.username)
                        change_groupname_username(user.username, data['username'])
                        
                        msg = "updated groupname and username succesfully"
                    else:
                        changeUsername(data['username'], user.username)
                        msg = "updated only username succesfully"
                    userObject.username = data['username']
                    userObject.fullname = data['fullname']
                    userObject.email = data['email']
                    userObject.save()
                    
            else:
                msg = "invalid "+ user.username

            # Update profile fields
            profile = Profile.objects.get(user=userObject)

            if 'photo' in request.FILES:
                
                photo = request.FILES['photo']
                # Create or update the user-specific folder
                user_folder = os.path.join(settings.MEDIA_ROOT, str(user.id))
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                
                photo_path = os.path.join(user_folder, photo.name)
                photo_url = '/media/'+os.path.relpath(photo_path, settings.MEDIA_ROOT)
                print('photo_url',photo_url)
                old_photo_url_path = os.path.join(user_folder,profile.photo_url.split('/')[3])
                print("path:",old_photo_url_path)
                # Delete the old photo_url file if it exists
                if os.path.exists(old_photo_url_path):
                    os.remove(old_photo_url_path)
                with open(photo_path, 'wb+') as destination:
                    for chunk in photo.chunks():
                        destination.write(chunk)
            data['photo_url']  = photo_url
            serializer = ProfileSerializer(profile, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'message': 'Profile updated successfully'})
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          
        except ValidationError as e:
            return JsonResponse({'msg': e.message}, status=400)
        except Exception as e:
            return JsonResponse({'msg': str(e)}, status=500)
        


@swagger_auto_schema(
    method='PUT',
    request_body=UserSerializerGet,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE Change Password User By Admin",
    operation_description="This API help us to update User's password added By admin",
)

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def changePasswordByAdmin(request, id):
    """Change password user"""
    if (request.method == 'PUT'):
        userObject = User.objects.get(id=id)
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
            _, stderr = changePW_byAdmin(
                new_password, userObject.username)
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
@permission_classes([IsAuthenticated])
def changePassword(request):
    msg = ""
    if (request.method == 'PUT'):
            user = request.user
            data = request.data
            current_password = data['current_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']
            if check_password(current_password, user.password):
                print('Passwords match!')
            if new_password != confirm_password:
                print("Passwords do not match. Please try again.")
                msg = "Passwords do not match. Please try again."
            else:
                _, stderr = resetPW (user.username,new_password )
                # check if password change was successful
                if stderr == "":
                    user.password = make_password(new_password)
                    user.is_verified = True
                    user.save()
                    print("Password change successful")
                    msg = "Password change successful"
                    status=200

                else:
                    msg = f"Error changing password"
                    status=400
                    
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


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET PROFILE LANGUAGE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_profile_language(request, id):
    """Getting Profile language"""
    profile = Profile.objects.get(user=User.objects.get(id=id))
    return JsonResponse({"language": profile.language})


@swagger_auto_schema(
        method='PUT', 
        responses={200: 'Created', 400: 'Bad Request'}, 
        operation_summary="API TO UPDATE PROFILE LANGUAGE",
        request_body=Schema(type=TYPE_OBJECT, required=['language'], properties={'language': Schema(type=TYPE_STRING)}))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_language(request, id):
    """Update profile language"""
    try:
        data = request.data
        profile = Profile.objects.get(user=User.objects.get(id=id))
        serializer_profile = ProfileSerializer(profile, data=data, partial=True)
        if serializer_profile.is_valid():
            serializer_profile.save()
            return JsonResponse({"msg": "Language is updated"}, status=200)
        return JsonResponse({"error": list(serializer_profile.errors.values())[0][0]}, status=400)
    except (User.DoesNotExist, Profile.DoesNotExist):
        return JsonResponse({"error": "User does not exist"}, status=400)
