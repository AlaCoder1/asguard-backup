import os
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from backend.managementUsers.models import Profile, User
from backend.managementUsers.serializers import PermissionSerializer, ProfileSerializer, UserSerializerGet, UserSerializerPost, UserSerializerPostWithoutGroupAndPermission
from backend.managementUsers.functions import add_user_group, add_mail_spool, add_user, change_password_by_admin, change_username, check_same_groupname_with_username, delete_user_group, delete_user_in_system, get_uid_user, reset_password, username_exists, valid_input, valid_password
from backend.managementGroup.serializers import GroupSerializer
from backend.managementGroup.functions import change_groupname_username, getGroupNameById, getUidGroup
from backend.managementGroup.models import Group
from backend.subscription.models import Organization
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


# Constants
CONSTANT_USER = _("User")
CONSTANT_USERNAME = _("username")
CONSTANT_PASSWORD = _("password")
CONSTANT_PERMISSION = _("permission")
CONSTANT_GROUPNAME = _("groupname")
CONSTANT_DIRECTORY_SERVER = _("directory server")
CONSTANT_METHOD_ADD_USER_EMAIL_SERVER = _("with their email in directory server")
CONSTANT_METHOD_ADD_USER_EMAIL_SYSTEM = _("with simple System email")
CONSTANT_OR = _("or")
CONSTANT_AND = _("and")
CONSTANT_LANGUAGE = _('Language')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("Error in creating")
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_EXISTANT = _("already exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_CREDENTIALS = _("Invalid credentials")
ERROR_MESSAGES_INVALID_PASSWORD = _("Invalid password")
ERROR_MESSAGES_CONNECTION = _("Error connecting to directory server")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF Users",
                     operation_description="API TO GET LIST OF Users")
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    """Get all users from database"""
    list_users = []
    if (request.method == 'GET'):
        users = User.objects.all()
        user_dict = serializers.serialize("json", users)
        res = json.loads(user_dict)
        for i in range(0, len(res)):
            res[i].pop('model')
            user_id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('password')
            res[i]['fields']['id'] = user_id
            list_users.append(res[i]['fields'])
        return list_users


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET USER BY ID",
                     operation_description="API TO GET USER BY ID")
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request, id):
    """Get user  by ID from database"""
    if (request.method == 'GET'):
        user = User.objects.filter(id=id)
        user_dict = serializers.serialize("json", user)
        res_user = json.loads(user_dict)
        res_user[0]['fields']['id'] = res_user[0]['pk']
        user_json = res_user[0]['fields']
        
        profile=Profile.objects.filter(user_id=id)
        profile_user=serializers.serialize("json", profile)
        res_profile = json.loads(profile_user)
        res_profile[0]['fields']['id'] = res_profile[0]['pk']
        profile_json = res_profile[0]['fields']
        user_json['profile']=profile_json
        return JsonResponse(user_json)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO Create New USER",
                     operation_description="API TO Create New USER")
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_user(request):
    """Create user"""
    msg = ''
    email_founded = False
    if request.method == 'POST':
        data = request.data
        username = data['username']
        password = data['password']
        organisation = Organization.objects.get(id=1)
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
                            return JsonResponse({'msg': f"{email} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
                        ldap_conn.unbind()
                    else:
                        return JsonResponse({'msg': ERROR_MESSAGES_INVALID_PASSWORD}, status=400)   
                    
                except ldap.SERVER_DOWN:
                # LDAP authentication failed
                    return JsonResponse({'msg': ERROR_MESSAGES_INVALID_CREDENTIALS}, status=400)
                except ldap.LDAPError:
                    return JsonResponse({'msg': ERROR_MESSAGES_CONNECTION}, status=400)
            else:
                return JsonResponse({'msg': f"{CONSTANT_DIRECTORY_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
       
        if User.objects.filter(email=email).exists():
            return JsonResponse({"msg": f"Email {ERROR_MESSAGES_EXISTANT}"}, status=400)
        else:
            if valid_input(username) and valid_password(password):
                # Execute the command on the remote machine
                error_useradd, stdout_password, stderr_password  = add_user(username, password)
                # Convert the stderr stream to a string
                if error_useradd == '':
                    add_mail_spool(username)
                    if email_founded:
                        msg = f"{username} {SUCCESS_MESSAGES_CREATING} {CONSTANT_METHOD_ADD_USER_EMAIL_SERVER}"
                        data['id_server_id']= ad_server.id
                    else:
                        msg = f"{username} {SUCCESS_MESSAGES_CREATING} {CONSTANT_METHOD_ADD_USER_EMAIL_SYSTEM}"
                    uid = get_uid_user()
                    data['password'] = make_password(data['password'])
                    data['uid'] = uid
                    if 'group' in data:
                        groups = data['group']
                        for i in range(0, len(groups)):
                            add_user_group(getGroupNameById(groups[i]), username)
                        serializer_user = UserSerializerPost(data=data)
                        gid = getUidGroup()
                        groupname = {"groupname": username}
                        groupname['gid'] = gid
                        groupname['created_by_system'] = True
                        serializer_group = GroupSerializer(data=groupname)

                        # Check if the sent information is okay
                        if serializer_user.is_valid():
                            if serializer_group.is_valid():
                                # If okay, save it on the database
                                serializer_user.save()
                                serializer_group.save()
                                Profile.objects.create(user=serializer_user.save())
                                # Provide a Json Response with the data that was saved
                                return JsonResponse({"msg": msg}, status=201)
                            # Provide a Json Response with the necessary error information
                            error_message_group = next(iter(serializer_group.errors.values()))[0]
                            return JsonResponse({"msg":error_message_group}, status=400)
                        # Provide a Json Response with the necessary error information
                        error_message = next(iter(serializer_user.errors.values()))[0]
                        return JsonResponse({"msg":error_message}, status=400)
                    else:
                       
                        serializer_user = UserSerializerPostWithoutGroupAndPermission(data=data)
                        gid = getUidGroup()
                        groupname = {"groupname": username}
                        groupname['gid'] = gid
                        groupname['created_by_system'] = True
                        serializer_group = GroupSerializer(data=groupname)

                        # Check if the sent information is okay
                        if serializer_user.is_valid():
                            if serializer_group.is_valid():
                                # If okay, save it on the database
                                
                                serializer_user.save()
                                serializer_group.save()
                                Profile.objects.create(user=serializer_user.save())
                                # Provide a Json Response with the data that was saved
                                return JsonResponse({"msg": msg}, status=201)
                            # Provide a Json Response with the necessary error information
                            return JsonResponse(serializer_group.errors, status=400)
                        # Provide a Json Response with the necessary error information
                        return JsonResponse(serializer_user.errors, status=400)
                    
                else:
                    return JsonResponse({"msg": f"{ERROR_MESSAGES_CREATING} {CONSTANT_USER}"}, status=400)
            else:
                return JsonResponse({"msg": ERROR_MESSAGES_INVALID_PASSWORD}, status=201)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE USER",
                     operation_description="API TO DELETE USER")
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user(request, id):
    """Delete group"""
    msg = ""
    if (request.method == 'DELETE'):
        user = User.objects.get(id=id)
        group = Group.objects.filter(groupname=user.username)
        # # Execute the command on the remote machine
        _, stderr = delete_user_in_system(user.username)
        # # convert the stderr stream to a string
        if stderr == "":
            user.delete()
            group.delete()
            msg = f"{user.username} {SUCCESS_MESSAGES_DELETING}"
        else:
            msg = f"{ERROR_MESSAGES_DELETING} {CONSTANT_USER}"
        # return a no content response.
        return JsonResponse({"msg": msg})


@swagger_auto_schema(
    method='PUT',
    request_body=UserSerializerPost,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE User",
    operation_description="This API help us to update User added")
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def modify_user(request, id):
    if (request.method == 'PUT'):
        user_by_id = User.objects.filter(id=id)
        user_dict = serializers.serialize("json", user_by_id)
        res = json.loads(user_dict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields'].pop('password')
        res[0]['fields']['id'] = id
        user_json = res[0]['fields']
        oldusername = user_json['username']
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
                            return JsonResponse({'msg': f"Email {ERROR_MESSAGES_INEXISTANT}"}, status=400)
                    ldap_conn.unbind()
                else:
                    return JsonResponse({'msg': ERROR_MESSAGES_INVALID_PASSWORD}, status=400)    
            except ldap.SERVER_DOWN:
                # LDAP authentication failed
                return JsonResponse({'msg': ERROR_MESSAGES_INVALID_CREDENTIALS}, status=400)        
            except ldap.LDAPError:
                return JsonResponse({'msg': ERROR_MESSAGES_CONNECTION}, status=400)  
            
        if User.objects.filter(email=data['email']).exclude(id=id).exists():
            return JsonResponse({"msg": f"Email {ERROR_MESSAGES_EXISTANT}"}, status=400)    
        newmail = data['email']
        newrole = data['role']
        user_object = User.objects.get(id=id)
        user = user_object.__dict__
        user['group'] = user_json['group']
        if valid_input(newusername):
            if username_exists(newusername) and newusername != oldusername:
                msg = f"{CONSTANT_USERNAME} {CONSTANT_OR} {CONSTANT_PASSWORD} {ERROR_MESSAGES_EXISTANT}"
                return JsonResponse({"msg": msg})

            user_object.username = newusername
            change_username(newusername, oldusername)
            if check_same_groupname_with_username(oldusername):
                change_groupname_username(oldusername, newusername)
            msg = f"{CONSTANT_USER} {SUCCESS_MESSAGES_UPDATING}"
            user_object.fullname = newfullname
            user_object.email = newmail
            user_object.role = newrole
            user_object.dn_user=data['dn_user']
            if email_founded:
                user_object.id_server=ad_server
            else:
                user_object.id_server=None
            if 'group' in data:
                groups = data['group']
                user_json['group'] = groups
                test_by_group = Group.objects.filter(user__id=id)
                test_by_group_dict = serializers.serialize("json", test_by_group)
                restest_by_group = json.loads(test_by_group_dict)
                for k in restest_by_group:
                    delete_user_group(k['fields']['groupname'], newusername)
                for m in data['group']:
                    gg = Group.objects.get(id=m)
                    add_user_group(gg.groupname, newusername)
                user_object.group.set(user_json['group'])
            user_object.save()
        else:
            msg = f"{ERROR_MESSAGES_UPDATING} {CONSTANT_USERNAME}"
        
        return JsonResponse({"data": data, "msg": msg})


@swagger_auto_schema(
    method='PUT',
    request_body=ProfileSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UpdateProfile",
    operation_description="This API help us to update profile of user ")
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    if (request.method == 'PUT'):
        try:
            data = request.data
            user = request.user
            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return JsonResponse({"msg": f"Email {ERROR_MESSAGES_EXISTANT}"}, status=400)          
            user_object = User.objects.get(id=user.id)
            if valid_input(user.username):
                if username_exists(data['username']) and  data['username'] != user.username:
                    msg = f"{CONSTANT_USERNAME} {CONSTANT_OR} email {ERROR_MESSAGES_EXISTANT}"
                    return JsonResponse({"msg": msg})
                else:
                    change_username(data['username'], user.username)
                    if check_same_groupname_with_username(user.username):
                        change_groupname_username(user.username, data['username'])
                        msg = f"{CONSTANT_GROUPNAME} {CONSTANT_AND} {CONSTANT_USERNAME} {SUCCESS_MESSAGES_UPDATING}"
                    else:
                        msg = f"{CONSTANT_USERNAME} {SUCCESS_MESSAGES_UPDATING}"
                    user_object.username = data['username']
                    user_object.fullname = data['fullname']
                    user_object.email = data['email']
                    user_object.save()
                    
            else:
                msg = "invalid "+ user.username

            # Update profile fields
            profile = Profile.objects.get(user=user_object)

            if 'photo' in request.FILES:
                
                photo = request.FILES['photo']
                # Create or update the user-specific folder
                user_folder = os.path.join(settings.MEDIA_ROOT, str(user.id))
                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)
                
                photo_path = os.path.join(user_folder, photo.name)
                photo_url = '/media/'+os.path.relpath(photo_path, settings.MEDIA_ROOT)
                old_photo_url_path = os.path.join(user_folder,profile.photo_url.split('/')[3])
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
                return JsonResponse({'message': f"Profile {SUCCESS_MESSAGES_UPDATING}"})
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          
        except ValidationError as e:
            return JsonResponse({'msg': e.message}, status=400)
        except Exception as e:
            return JsonResponse({'msg': str(e)}, status=400)
        

@swagger_auto_schema(
    method='PUT',
    request_body=UserSerializerGet,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE Change Password User By Admin",
    operation_description="This API help us to update User's password added By admin")
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def change_password_by_admin(request, id):
    """Change password user"""
    if (request.method == 'PUT'):
        user_object = User.objects.get(id=id)
        data = request.data
        # instanciate with the serializer
        serializer = UserSerializerGet()
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        if new_password != confirm_password:
            return JsonResponse({"msg": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_PASSWORD}"})
        else:
            # run 'passwd' command to change password
            _, stderr = change_password_by_admin(
                new_password, user_object.username)
            # check if password change was successful
            if stderr == "":
                user_object.password = make_password(new_password)
                user_object.save()
        return JsonResponse(serializer.data, status=201)


@swagger_auto_schema(
    method='PUT',
    request_body=UserSerializerPost,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE Change Password User ",
    operation_description="This API help us to update User's password added ")
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    if (request.method == 'PUT'):
            user = request.user
            data = request.data
            current_password = data['current_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']
            if new_password == confirm_password and check_password(current_password, user.password):
                _, stderr = reset_password (user.username,new_password )
                # check if password change was successful
                if stderr == "":
                    user.password = make_password(new_password)
                    user.is_verified = True
                    user.save()
                    return JsonResponse({"msg": f"{CONSTANT_PASSWORD} {SUCCESS_MESSAGES_UPDATING}"}, status=200)

            return JsonResponse({"msg": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_PASSWORD}"}, status=400)


@swagger_auto_schema(
    method='POST',
    request_body=PermissionSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD Permission ",
    operation_description="This API help us to ADD Permission",)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def add_permission(request):
    """API de create permission"""
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
        # instanciate with the serializer
        serializer = PermissionSerializer(data=data)
        # check if the sent information is okay
        if serializer.is_valid():
            # if okay, save it on the database
            serializer.save()
            # provide a Json Response with the data that was saved
            return JsonResponse({"msg": f"{CONSTANT_PERMISSION} {SUCCESS_MESSAGES_CREATING}"}, status=201)
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
            return JsonResponse({"msg":f"{CONSTANT_LANGUAGE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
        return JsonResponse({"error": list(serializer_profile.errors.values())[0][0]}, status=400)
    except (User.DoesNotExist, Profile.DoesNotExist):
        return JsonResponse({"error":f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=400)