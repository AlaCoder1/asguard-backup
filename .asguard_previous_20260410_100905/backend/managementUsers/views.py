import os
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from backend.managementUsers.models import Profile, User, Roles
from backend.managementUsers.serializers import PermissionSerializer, ProfileSerializer, UserSerializerGet, UserSerializerPost, UserSerializerPostWithoutGroupAndPermission,RoleSerializer
from backend.managementUsers.functions import add_user_group, add_user, reset_password_by_admin_in_system, change_username, check_same_groupname_with_username, delete_user_group, delete_user_in_system, get_uid_user, reset_password, reset_password_by_admin_in_system, username_exists, valid_input, valid_password,delete_directory,change_directory_name
from backend.managementGroup.serializers import GroupSerializer
from backend.managementGroup.functions import change_groupname_username, getGroupNameById, getUidGroup
from backend.managementGroup.models import Group
from backend.subscription.models import Organization
import json
from django.core import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from backend.LdapServer.models import ADServer
import ldap
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING
from django.conf import settings
from rest_framework import status
from backend.waf.models import RulesWaf
from drf_yasg.openapi import TYPE_ARRAY, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Schema
from django.core.exceptions import ObjectDoesNotExist

from utils.utils_email import is_valid_email
from django.views.decorators.http import require_http_methods

# Constants
CONSTANT_USER = _("User")
CONSTANT_ROLE = _("Role")
CONSTANT_AD_SERVER= _("AD Server")
CONSTANT_GROUP= _("Group")
CONSTANT_FUNCTIONALITY = _("functionality")
CONSTANT_USERNAME = _("username")
CONSTANT_PASSWORD = _("password")
CONSTANT_EMAIL_FORMAT = _("email format")
CONSTANT_PERMISSION = _("permission")
CONSTANT_GROUPNAME = _("groupname")
CONSTANT_DIRECTORY_SERVER = _("directory server")
CONSTANT_DATA = _("data")
CONSTANT_TYPE = _("Type")
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
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UPDATING = _("System error in updating")
ERROR_MESSAGES_EXISTANT = _("already exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_CONNECTION = _("System error in connecting to directory server")
ERROR_MESSAGES_INVALID = _("Invalid")
ERROR_MESSAGES_LDAP_UNREACHABLE = _("Directory Server unreachable")
ERROR_MESSAGES_DELETE_ROLE = _("You can't delete this role. It is used by other users")
ERROR_MESSAGES_GROUP_NOT_MATCHING = _('No group found matching the username')


@swagger_auto_schema('GET', responses={200: 'List of all users', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF Users",
                     operation_description="API TO GET LIST OF Users")

@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    """
    Retrieves all users from the database and returns them in a formatted JSON response.

    This function queries the `User` model for all users and serializes the results,
    removing sensitive fields such as the password, and restructuring the data to 
    include only relevant user details.

    Args:
        request (HttpRequest): The HTTP request used to trigger the retrieval.

    Returns:
        JsonResponse: A JSON response containing a list of all users' details without passwords.

    Workflow:
        1. Checks if the request method is 'GET'.
        2. Retrieves all user objects from the `User` model.
        3. Serializes the user data into JSON format.
        4. Removes unnecessary fields (`model`, `password`, `pk`), and restructures the data.
        5. Returns the list of users as a JSON response.

    HTTP Status:
        - 200: Successful retrieval of all users.

    Dependencies:
        - `User`: Django's user model.
        - `serializers.serialize()`: Serializes the user data into JSON format.
        - `json.loads()`: Parses the serialized JSON data into Python objects.
        
    Notes:
        - The `password` field is explicitly removed to ensure sensitive information is not exposed.
    """
    """Get all users from database"""
    list_users = []
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
    return JsonResponse(list_users, safe=False,status=200)
    
@swagger_auto_schema('GET', responses={200: 'List of all roles', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF roles",
                     operation_description="API TO GET LIST OF roles")

@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_roles(request):
    """
    Retrieves all roles from the database and returns them in a formatted JSON response.

    This function queries the `Roles` model for all roles and serializes the results,
    restructuring the data to include only relevant role details.

    Args:
        request (HttpRequest): The HTTP request used to trigger the retrieval.

    Returns:
        JsonResponse: A JSON response containing a list of all roles' details.

    Workflow:
        1. Checks if the request method is 'GET'.
        2. Retrieves all role objects from the `Roles` model.
        3. Serializes the role data into JSON format.
        4. Removes unnecessary fields (`model`, `pk`), and restructures the data.
        5. Returns the list of roles as a JSON response.

    HTTP Status:
        - 200: Successful retrieval of all roles.

    Dependencies:
        - `Roles`: The model representing roles in the application.
        - `serializers.serialize()`: Serializes the role data into JSON format.
        - `json.loads()`: Parses the serialized JSON data into Python objects.
        
    Notes:
        - The `pk` and `model` fields are explicitly removed as they are not needed in the response.
    """
    list_roles = []
    roles = Roles.objects.all()
    role_dict = serializers.serialize("json", roles)
    res = json.loads(role_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        role_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = role_id
        list_roles.append(res[i]['fields'])
    
    return JsonResponse({"list_roles":list_roles},status=200)


@swagger_auto_schema(
    method='post',
    operation_summary="Create Role API",
    operation_description="Creates a new role in the database after validating the request data.",
    request_body=Schema(
        type=TYPE_OBJECT,
        required=["role_name"],
        properties={
            "name": Schema(type=TYPE_STRING, example="Admin"),
            'fonctionalities': Schema(
                type=TYPE_STRING,  
                description="The functionalities of the role, serialized as a JSON array of strings.",
                example="['sdwan', 'ztna', 'proxy']"  
            )
        },
    ),
    responses={200: 'Create Role successfully', 400: 'Bad Request'}, 
    security=[{"session_auth": []}],
)


@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_role(request):
    """
    Creates a new role in the database.

    This function accepts data for a new role, validates it using the `RoleSerializer`,
    and saves the role to the database. If validation fails, an error message is returned.

    Args:
        request (HttpRequest): The HTTP request containing the data for the new role.

    Returns:
        JsonResponse:
            - 200: If the role is successfully created.
            - 400: If the provided data is invalid, with error messages.

    Workflow:
        1. Checks if the request method is 'POST'.
        2. Extracts the data from the request.
        3. Uses `RoleSerializer` to validate and serialize the data.
        4. If the data is valid, saves the new role to the database.
        5. Returns a success message or validation error message based on the outcome.

    HTTP Status:
        - 200: Successful creation of the new role.
        - 400: If the data is invalid, including a list of error messages.

    Dependencies:
        - `RoleSerializer`: Serializer for validating and serializing role data.
        - `CONSTANT_ROLE`: A constant representing the role in the success message.
        - `SUCCESS_MESSAGES_CREATING`: A constant for the success message.
    """
    data = request.data
    print({"data": data})
    data['name'] = data['name'].strip().lower()
    if type(data['fonctionalities']) is not str:
        return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} {CONSTANT_TYPE}"}, status=400)

    # List of valid functionalities
    valid_functionalities = ["ipsec", "openvpn", "suricata", "proxy", "sdwan", "waf", "ztna"]

    # Get the string with single quotes
    fonctionalities_str = data.get('fonctionalities', '').strip()

    # Replace single quotes with double quotes for JSON format
    fonctionalities_str = fonctionalities_str.replace("'", '"')

    # Parse the string to a list
    fonctionalities_list = json.loads(fonctionalities_str)

    # Capitalize the first character of each functionality
    fonctionalities_list = [f.strip().capitalize() for f in fonctionalities_list]

    # Check if any element in the list is a valid functionality
    if not any(f.lower() in valid_functionalities for f in fonctionalities_list):
        return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} {CONSTANT_FUNCTIONALITY}"}, status=400)

    # Update the data with the capitalized functionality list
    data['fonctionalities'] = str(fonctionalities_list)
    serializer = RoleSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'msg': f"{CONSTANT_ROLE} {SUCCESS_MESSAGES_CREATING}"}, status=200) 
    return JsonResponse({'errors': serializer.errors}, status=400)


@swagger_auto_schema(
    method='put',
    operation_description="Modify an existing role in the database.",
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'name': Schema(type=TYPE_STRING, description="Updated name of the role"),
            'fonctionalities': Schema(
                type=TYPE_STRING,  
                description="The functionalities of the role, serialized as a JSON array of strings.",
                example="['sdwan', 'ztna', 'proxy']"  
            )
        },
        required=['name', 'description']
    ),
    responses={200: 'Role successfully updated', 400: 'Bad Request'}, 
)

@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def modify_role(request,id):
    """
    Modifies an existing role in the database.

    This function retrieves an existing role by its ID, validates the updated data using 
    the `RoleSerializer`, and saves the changes to the role in the database. If validation fails, 
    an error message is returned.

    Args:
        request (HttpRequest): The HTTP request containing the updated data for the role.
        id (int): The ID of the role to be modified.

    Returns:
        JsonResponse:
            - 200: If the role is successfully updated.
            - 400: If the provided data is invalid, with error messages.

    Workflow:
        1. Checks if the request method is 'PUT'.
        2. Retrieves the role to be modified from the `Roles` model by its ID.
        3. Validates and serializes the updated data using `RoleSerializer`.
        4. If the data is valid, saves the changes to the database.
        5. Returns a success message or validation error message based on the outcome.

    HTTP Status:
        - 200: Successful modification of the role.
        - 400: If the data is invalid, including a list of error messages.

    Dependencies:
        - `Roles`: The model representing roles in the application.
        - `RoleSerializer`: Serializer for validating and serializing role data.
        - `CONSTANT_ROLE`: A constant representing the role in the success message.
        - `SUCCESS_MESSAGES_UPDATING`: A constant for the success message.
    """
    try:
        role = Roles.objects.get(id=id)
    except Roles.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ROLE} {ERROR_MESSAGES_INEXISTANT}"},status=400)
    
    data = request.data
    if type(data['fonctionalities']) is not str:
        return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} {CONSTANT_TYPE}"}, status=400)

    # List of valid functionalities
    valid_functionalities = ["ipsec", "openvpn", "suricata", "proxy", "sdwan", "waf", "ztna"]

    # Get the string with single quotes
    fonctionalities_str = data.get('fonctionalities', '').strip()

    # Replace single quotes with double quotes for JSON format
    fonctionalities_str = fonctionalities_str.replace("'", '"')

    # Parse the string to a list
    fonctionalities_list = json.loads(fonctionalities_str)

    # Capitalize the first character of each functionality
    fonctionalities_list = [f.strip().capitalize() for f in fonctionalities_list]

    # Check if every element in the list is a valid functionality
    if not all(f.lower() in valid_functionalities for f in fonctionalities_list):
        return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} {CONSTANT_FUNCTIONALITY}"}, status=400)

    # Update the data with the capitalized functionality list
    data['fonctionalities'] = str(fonctionalities_list)
    serializer = RoleSerializer(role, data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'msg': f"{CONSTANT_ROLE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    return JsonResponse({'msg': serializer.errors}, status=400) 
    


@swagger_auto_schema(
    method='delete',
    operation_description="Delete an existing role from the database.",
    responses={200: 'Role successfully deleted', 400: 'Bad Request'}, 
)
@api_view(['DELETE'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_role(request, id):
    """
    Deletes a role from the database.

    This function checks if any users are currently assigned to the specified role.
    If there are users associated with the role, it returns an error message.
    If no users are assigned, it deletes the role and returns a success message.

    Args:
        request (HttpRequest): The HTTP request to delete a role.
        id (int): The ID of the role to be deleted.

    Returns:
        JsonResponse:
            - 400: If there are users linked to the role, with a message detailing the error.
            - 200: If the role is successfully deleted.

    Workflow:
        1. Retrieves the role to be deleted from the `Roles` model by its ID.
        2. Checks if any users are currently assigned to this role.
        3. If users are assigned to the role, returns an error message with the usernames.
        4. If no users are assigned to the role, proceeds with deletion.
        5. Returns a success message upon successful deletion of the role.

    HTTP Status:
        - 400: If the role is in use by any users.
        - 200: Successful deletion of the role.

    Dependencies:
        - `Roles`: The model representing roles in the application.
        - `User`: The model representing users in the application.
        - `CONSTANT_DELETE_ROLE`: A constant for the error message when the role cannot be deleted.
        - `CONSTANT_ROLE`: A constant representing the role in the success message.
        - `SUCCESS_MESSAGES_DELETING`: A constant for the success message.
    """
    try:
        role = Roles.objects.get(id=id)
    except Roles.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ROLE} {ERROR_MESSAGES_INEXISTANT}"},status=400)
    
    # Check if any users are linked to this role
    users_with_role = User.objects.filter(role=role)
    if users_with_role.exists():
        # If the role is in use, return an error message with the usernames
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETE_ROLE}"}, status=400)
    
    # If no users are using the role, proceed with deletion
    role.delete()
    return JsonResponse({"msg": f"{CONSTANT_ROLE} {SUCCESS_MESSAGES_DELETING}"})
    

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a user by ID from the database.",
    responses={200: 'User retrieved successfully', 400: 'Bad Request'}, 
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request, id):
    """
    Retrieves a user by ID from the database.

    This function fetches the user details along with their profile information 
    by the provided user ID. It combines the user and profile data into a single 
    response before returning it as a JSON response.

    Args:
        request (HttpRequest): The HTTP request to fetch a user's data.
        id (int): The ID of the user to be retrieved.

    Returns:
        JsonResponse:
            - A JSON response containing the user details along with their profile information.

    Workflow:
        1. Fetches the user from the `User` model using the provided ID.
        2. Serializes the user data into JSON format and extracts the user fields.
        3. Fetches the profile associated with the user from the `Profile` model.
        4. Serializes the profile data into JSON format and extracts the profile fields.
        5. Combines the user and profile data into a single dictionary.
        6. Returns a JSON response containing the combined user and profile data.

    HTTP Status:
        - 200: Returns the user data with profile information.

    Dependencies:
        - `User`: The model representing users in the application.
        - `Profile`: The model representing user profiles.
        - `serializers.serialize`: A method used to serialize model instances into JSON format.
    """
    try:
        user = User.objects.filter(id=id)
    except User.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
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
    return JsonResponse(user_json,status=200)


@swagger_auto_schema(
    method='post',
    operation_description="Create a new user in the system.",
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['username', 'password', 'email'],
        properties={
            'username': Schema(type=TYPE_STRING, description="The username of the user",example="testuser"),
            'password': Schema(type=TYPE_STRING, description="Password for the user",example="Password@@123456789@@"),
            'fullname': Schema(type=TYPE_STRING, description="fullname for the user",example="testuser"),
            'role': Schema(type=TYPE_INTEGER, description="Role of the user"),
            'email': Schema(type=TYPE_STRING, description="Email address of the user",example="testuser@email.com"),
            'password_ad': Schema(type=TYPE_STRING, description="Password for Active Directory (if applicable)"),
            'id_server': Schema(type=TYPE_INTEGER, description="ID of the AD server (if applicable)"),
            'group': Schema(
                type=TYPE_ARRAY,
                items=Schema(type=TYPE_INTEGER, description="Group ID(s) the user belongs to"),
                description="List of group IDs the user is assigned to"
            ),
        }
    ),
    responses={200: 'User created successfully', 400: 'Bad Request'}, 
)

@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_user(request):
    """
    Creates a new user in the system and synchronizes with an LDAP server if required.

    This function handles the user creation process, including validation of the username, password,
    and email. It also integrates with an LDAP server for authentication and email checking if required.
    The function performs several checks, such as verifying that the email does not already exist, ensuring
    the password meets security criteria, and creating a user in the database. Additionally, it interacts
    with an Active Directory (AD) server if an `id_server` is provided for the user.

    Args:
        request (HttpRequest): The HTTP request containing the user creation data.

    Returns:
        JsonResponse:
            - A JSON response containing the result of the user creation, including any error messages
              or success messages.

    Workflow:
        1. Checks if the method is POST and extracts the data from the request.
        2. Validates if the password and username are in a valid format.
        3. Verifies the email against the database and LDAP servers (if provided).
        4. If the email is found on the LDAP server, the function adds the corresponding DN information.
        5. Creates a user record in the system and associates it with the provided organization and groups.
        6. Returns a JSON response indicating success or failure.

    HTTP Status Codes:
        - 201: Successfully created the user.
        - 400: Invalid input, such as email already existing, password mismatch, or LDAP errors.
    
    Dependencies:
        - `User`: The model representing the user in the application.
        - `ADServer`: The model representing Active Directory servers.
        - `ldap`: Python's LDAP library for LDAP server communication.
        - `UserSerializerPost`: The serializer used to create user records.
        - `Profile`: The model representing user profiles.
        - `GroupSerializer`: The serializer used to manage user groups.

    Example Response:
        - Success: {"msg": "Username successfully created on email system."}
        - Failure: {"msg": "Email already exists."}
    """
    msg = ''
    email_founded = False
    if request.method == 'POST':
        data = request.data
        username = data['username']
        password = data['password']
        email = data['email']
        if not is_valid_email(email):
            return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} {CONSTANT_EMAIL_FORMAT}"}, status=400) 
        organisation = Organization.objects.get(id=1)
        data['organisation'] = organisation.id
        email = data['email']
        
        if data['password_ad'] != "":
            id_server = data['id_server']
            try:
                ad_server = ADServer.objects.get(id=id_server)
            except ADServer.DoesNotExist:
                return JsonResponse({"error": f"{CONSTANT_AD_SERVER} {ERROR_MESSAGES_INEXISTANT}"},status=400)
            if ad_server:
                try:
                    is_password_matched = check_password(data['password_ad'],ad_server.bind_user_password)
                    if is_password_matched:
                        ldap_uri = f"{'ldaps' if ad_server.ssl_tls_activation else 'ldap'}://{ad_server.server_url}:{ad_server.port}"
                        ldap_conn = ldap.initialize(ldap_uri)
                        ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
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
                        return JsonResponse({'msg': f"{ERROR_MESSAGES_INVALID} {CONSTANT_PASSWORD}"}, status=400)   
                    
                except ldap.SERVER_DOWN:
                    return JsonResponse({'msg': f"{ERROR_MESSAGES_LDAP_UNREACHABLE}"}, status=400)
                except ldap.LDAPError:
                    return JsonResponse({'msg': f"{ERROR_MESSAGES_CONNECTION}"}, status=400)
            else:
                return JsonResponse({'msg': f"{CONSTANT_DIRECTORY_SERVER} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
       
        if User.objects.filter(email=email).exists():
            return JsonResponse({"msg": f"Email {ERROR_MESSAGES_EXISTANT}"}, status=400)
        else:
            data['id_server']= None
            if valid_input(username) and valid_password(password):
                # Execute the command on the remote machine
                error_useradd, _, _  = add_user(username, password)
                # Convert the stderr stream to a string
                if error_useradd == '':
                    # add_mail_spool(username)
                    if email_founded:
                        msg = f"{username} {SUCCESS_MESSAGES_CREATING} {CONSTANT_METHOD_ADD_USER_EMAIL_SERVER}"
                    else:
                        msg = f"{username} {SUCCESS_MESSAGES_CREATING} {CONSTANT_METHOD_ADD_USER_EMAIL_SYSTEM}"
                    uid = get_uid_user()
                    data['password'] = make_password(data['password'])
                    data['uid'] = uid
                    # data['role_id'] = 
                    if 'group' in data:
                        groups = data['group']
                        for group in groups:
                            try:
                                Group.objects.get(id=group)
                            except Group.DoesNotExist:
                                return JsonResponse({"error": f"{CONSTANT_GROUP} {ERROR_MESSAGES_INEXISTANT}"},status=400)
                            add_user_group(getGroupNameById(group), username)
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
                            # error_message_group = next(iter(serializer_group.errors.values()))[0]
                            return JsonResponse({"error":serializer_group.errors}, status=400)
                        # Provide a Json Response with the necessary error information
                        # error_message = next(iter(serializer_user.errors.values()))[0]
                        return JsonResponse({"error":serializer_user.errors}, status=400)
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
                return JsonResponse({"msg": f"{ERROR_MESSAGES_INVALID} {CONSTANT_PASSWORD}"}, status=400)


@swagger_auto_schema(
    method='delete',
    operation_description="Deletes a user and their associated group(s). If the user and associated group(s) are deleted successfully, a success message is returned.",
    responses={200: 'User and group deleted successfully', 400: 'Bad Request'}, 
)
@api_view(['DELETE'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user(request, id):
    """
    Deletes a user and their associated group from the system.

    This function handles the deletion of a user from the database, along with their associated group.
    It performs necessary checks and executes commands to remove the user from the system and delete
    any associated directories. The function returns a success message if the deletion is successful,
    or an error message if there is an issue during the process.

    Args:
        request (HttpRequest): The HTTP request for the deletion operation.
        id (int): The unique identifier of the user to be deleted.

    Returns:
        JsonResponse:
            - A JSON response containing the result of the user deletion, either a success message or
              an error message.

    Workflow:
        1. Retrieves the user object and associated group based on the provided user ID.
        2. Executes the command to delete the user from the system.
        3. Deletes any associated directories.
        4. If both the user deletion and directory deletion are successful, removes the user and group
           from the database.
        5. Returns a JSON response indicating success or failure.

    HTTP Status Codes:
        - 200: Successfully deleted the user and their group.
        - 400: Error during user deletion, such as issues with system commands or deletion failures.
    
    Dependencies:
        - `User`: The model representing the user in the application.
        - `Group`: The model representing the user group associated with the user.
        - `delete_user_in_system`: Function that deletes the user from the system.
        - `delete_directory`: Function that deletes the user directory.
    
    Example Response:
        - Success: {"msg": "username successfully deleted."}
        - Failure: {"error": "Error deleting user."}
    """
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
        # raise ValidationError(f"{CONSTANT_USER} {NOT_FOUND}")

    if not Group.objects.filter(groupname=user.username).exists():
        return JsonResponse({"error": f"{ERROR_MESSAGES_GROUP_NOT_MATCHING} '{user.username}"}, status=400)
        # raise ValidationError(f"{GROUP_NOT_MATCHING} '{user.username}'.")
    else:
        group = Group.objects.filter(groupname=user.username)
    # # Execute the command on the remote machine
    _, stderr = delete_user_in_system(user.username)
    _, stderr_dir = delete_directory(user.username)
    # # convert the stderr stream to a string
    if stderr == "":
        if stderr_dir == "":
            user.delete()
            group.delete()
            return JsonResponse({"msg": f"{user.username} {SUCCESS_MESSAGES_DELETING}"})
    return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_USER}"}, status=400)


@swagger_auto_schema(
    method='put',
    operation_description="Modify an existing user's details, including username, email, role, and Active Directory authentication.",
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['username', 'email', 'role'],
        properties={
            'username': Schema(type=TYPE_STRING, description="New username for the user",example="usertest"),
            'fullname': Schema(type=TYPE_STRING, description="Full name of the user",example="UserTest"),
            'email': Schema(type=TYPE_STRING, description="New email address",example="usertest@email.com"),
            'role': Schema(type=TYPE_INTEGER, description="Role ID associated with the user"),
            'password_ad': Schema(type=TYPE_STRING, description="Password for Active Directory authentication (if applicable)"),
            'id_server': Schema(type=TYPE_INTEGER, description="ID of the Active Directory server (if applicable)"),
            'group': Schema(
                type=TYPE_ARRAY,
                items=Schema(type=TYPE_INTEGER),
                description="List of group IDs to which the user belongs"
            ),
        }
    ),
    responses={200: "User modified successfully", 400: "Bad Request"},
)

@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def modify_user(request, id):
    """
    Modifies user details, including username, full name, email, and role.

    This function updates user information in the database, handles Active Directory (AD) authentication
    for email validation, and manages group assignments. It also renames the user's system account 
    and associated directories when the username is changed.

    Args:
        request (HttpRequest): The HTTP request containing updated user information.
        id (int): The unique identifier of the user to be modified.

    Returns:
        JsonResponse:
            - On success: JSON response containing updated user data and a success message.
            - On failure: JSON response with an error message and HTTP status 400.

    Workflow:
        1. Fetches the user object from the database.
        2. Serializes the user data to JSON and removes unnecessary fields (e.g., password).
        3. Extracts old username and processes incoming request data.
        4. If an AD password is provided, attempts to authenticate with the AD server:
           - Checks if the given email exists in the AD server.
           - If found, assigns `dn_user` to the user.
           - Returns an error if the email is not found in the AD.
        5. Validates email uniqueness within the database.
        6. Updates the username, email, role, and other user attributes.
        7. Renames system directories and groups if the username changes.
        8. Updates the user’s group memberships.
        9. Saves the updated user object and returns a success response.

    HTTP Status Codes:
        - 200: User successfully modified.
        - 400: Errors encountered during update (e.g., invalid email, LDAP connection failure, username conflict).

    Dependencies:
        - `User`: The model representing the user in the application.
        - `Group`: The model representing user groups.
        - `ADServer`: The model storing Active Directory server configurations.
        - `check_password`: Function to verify passwords.
        - `valid_input`: Function to validate username format.
        - `username_exists`: Function to check for duplicate usernames.
        - `change_username`, `change_directory_name`, `change_groupname_username`: Functions for renaming system entities.
        - `delete_user_group`, `add_user_group`: Functions for managing user-group associations.

    Example Response:
        - Success: {"data": {...}, "msg": "User successfully updated."}
        - Failure: {"msg": "Error updating username."}
    """
    try:
        User.objects.get(id=id)
    except User.DoesNotExist:
        return JsonResponse({'error': f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
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
    try:
        Roles.objects.get(id=data["role"])
    except Roles.DoesNotExist:
        return JsonResponse({'error': f"{CONSTANT_ROLE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    if not is_valid_email(data['email']):
        return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} {CONSTANT_EMAIL_FORMAT}"}, status=400) 
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
                return JsonResponse({'msg': f"{ERROR_MESSAGES_INVALID} {CONSTANT_PASSWORD}"}, status=400)    
        except ldap.SERVER_DOWN:
            # LDAP authentication failed
            return JsonResponse({'msg':f"{ERROR_MESSAGES_LDAP_UNREACHABLE}"}, status=400)        
        except ldap.LDAPError:
            return JsonResponse({'msg':f"{ERROR_MESSAGES_CONNECTION}"}, status=400)  
        
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
        change_directory_name(oldusername, newusername)
        if check_same_groupname_with_username(oldusername):
            change_groupname_username(oldusername, newusername)
        msg = f"{CONSTANT_USER} {SUCCESS_MESSAGES_UPDATING}"
        user_object.fullname = newfullname
        user_object.email = newmail
        user_object.role_id = newrole
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
                try:
                    gg = Group.objects.get(id=m)
                except Group.DoesNotExist:
                    return JsonResponse({"error": f"{CONSTANT_GROUP} {ERROR_MESSAGES_INEXISTANT}"},status=400)
                add_user_group(gg.groupname, newusername)
            user_object.group.set(user_json['group'])
        user_object.save()
    else:
        msg = f"{ERROR_MESSAGES_UPDATING} {CONSTANT_USERNAME}"
    
    return JsonResponse({"data": data, "msg": msg})


@swagger_auto_schema(
    method='put',
    operation_description="Update a user's profile, including username, group name, and profile photo.",
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['username'],
        properties={
            'username': Schema(type=TYPE_STRING, description="New username",example="newusername"),
            'email': Schema(type=TYPE_STRING, description="User's email",example="newusername@email.com"),
            'phone_number': Schema(type=TYPE_STRING, description="User's phone number",example="123456789"),
            'photo': Schema(type=TYPE_STRING, description="Profile picture file",example="profile.jpg"),
        }
    ),
    responses={200: "Profile updated successfully", 400: "Bad Request"},
)

@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request, id):
    """
    Updates a user's profile, including username changes and profile picture updates.

    This function:
    - Updates user attributes such as `username`.
    - Modifies the associated profile data.
    - Handles profile picture uploads by storing them in a user-specific directory.
    - Ensures old profile pictures are deleted when a new one is uploaded.

    Args:
        request (HttpRequest): The HTTP request containing user update data.
        id (int): The unique identifier of the user whose profile is being updated.

    Returns:
        JsonResponse:
            - On success: JSON response with a success message.
            - On failure: JSON response with an error message and HTTP status 400.

    Workflow:
        1. Retrieves user data from the database.
        2. Serializes and validates user update data.
        3. If the username is changed:
            - Calls `change_username()` to update system-level username references.
            - Calls `change_groupname_username()` to update group-related username references.
        4. Saves the updated user data.
        5. Retrieves the associated `Profile` instance.
        6. If a new profile picture is provided:
            - Stores the new image in a dedicated user-specific folder.
            - Deletes the previous profile picture file.
        7. Serializes and saves profile updates.
        8. Returns success or error responses.

    Profile Picture Handling:
        - The uploaded image is stored in `/media/{user_id}/` directory.
        - The old profile picture is deleted before saving a new one.

    Exceptions:
        - `ValidationError`: Raised when provided data is invalid.
        - `Exception`: Catches other unexpected errors.

    HTTP Status Codes:
        - 200: Profile successfully updated.
        - 400: Validation or processing error.

    Dependencies:
        - `User`: The model representing the user.
        - `Profile`: The model storing additional profile information.
        - `UserSerializerPost`: Serializer for user updates.
        - `ProfileSerializer`: Serializer for profile updates.
        - `change_username`: Function to update system username references.
        - `change_groupname_username`: Function to update username references in groups.
        - `os`: Used for file management.
        - `settings.MEDIA_ROOT`: Django media root for file storage.

    Example Response:
        - Success: {"message": "Profile successfully updated."}
        - Failure: {"msg": "Error message describing the failure."}
    """
    try:
        data = request.data
        user_object = User.objects.get(id=id)

        serializer_user = UserSerializerPost(user_object, data=data, partial=True)
        if serializer_user.is_valid():
            change_username(data['username'][0], user_object.username)
            change_groupname_username(user_object.username, data['username'])
            serializer_user.save()
        else:
            return JsonResponse({"msg": list(serializer_user.errors.values())[0][0]}, status=400)
                
        # Update profile fields
        profile = Profile.objects.get(user=user_object)

        if 'photo' in request.FILES:
            
            photo = request.FILES['photo']
            # Create or update the user-specific folder
            user_folder = os.path.join(settings.MEDIA_ROOT, str(id))
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
    method='put',
    operation_description="Allows an admin to reset a user's password. The new password must match the confirmation password.",
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'new_password': Schema(type=TYPE_STRING, description="The new password to set for the user",example="newpassword"),
            'confirm_password': Schema(type=TYPE_STRING, description="Confirmation of the new password",example="newpassword"),
        }
    ),
    responses={200: "Password reset successfully by admin", 400: "Bad Request"},
)

@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def reset_password_by_admin(request, id):
    """
    Allows an admin to reset the password of a user by their ID.

    Args:
        request (HttpRequest): The HTTP request object containing the admin's request data.
        id (int): The ID of the user whose password is being reset.

    Returns:
        JsonResponse: A JSON response indicating success or failure of the password reset.

    Behavior:
        - Accepts a PUT request to change the password for a specific user.
        - Retrieves the user object using the provided `id`.
        - Extracts `new_password` and `confirm_password` from the request data.
        - Verifies that the new password matches the confirmation password.
        - If the passwords match, attempts to reset the user's password by calling the `reset_password_by_admin_in_system` function.
        - If the password reset is successful, securely hashes the new password and updates the user object.
        - Returns a success message if the password reset was successful.
        - If any condition fails, returns an error message with a 400 status code.

    Notes:
        - `reset_password_by_admin_in_system(new_password, user_object.username)` runs a system-level command to reset the user's password.
        - `make_password(new_password)` securely hashes the new password before saving it to the user object.
    """
    if (request.method == 'PUT'):
        user_object = User.objects.get(id=id)
        data = request.data
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        if new_password != confirm_password:            
            return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_PASSWORD}"}, status=400)
        # run 'passwd' command to change password
        rslt = reset_password_by_admin_in_system(new_password, user_object.username)
        # check if password change was successful
        if rslt:
            user_object.password = make_password(new_password)
            user_object.save()
            return JsonResponse({"msg": f"{CONSTANT_PASSWORD} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_PASSWORD}"}, status=400)


@swagger_auto_schema(
    method='put',
    operation_description="Change the user's password after verifying the current password and matching the new passwords.",
    request_body=Schema(
        type=TYPE_OBJECT,
        properties={
            'current_password': Schema(type=TYPE_STRING, description="The current password of the user",example="currentpassword"),
            'new_password': Schema(type=TYPE_STRING, description="The new password to set for the user",example="newpassword"),
            'confirm_password': Schema(type=TYPE_STRING, description="Confirmation of the new password",example="newpassword"),
        }
    ),
    responses={200: "Password updated successfully", 400: "Bad Request"},
)

@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change the password for the authenticated user.

    Args:
        request (HttpRequest): The HTTP request object containing the user request data.

    Returns:
        JsonResponse: A JSON response indicating success or failure of the password change.

    Behavior:
        - Accepts a PUT request to change the user's password.
        - Extracts `current_password`, `new_password`, and `confirm_password` from the request data.
        - Verifies if the new password matches the confirmation password and checks if the current password is correct.
        - If valid, attempts to reset the password by calling the `reset_password` function.
        - If the reset is successful, updates the user's password, marks the user as verified, and saves the changes.
        - Returns a success message if the password change was successful.
        - If any condition fails, returns an error message with a 400 status code.

    Notes:
        - `check_password(current_password, user.password)` checks if the current password is correct.
        - `reset_password(user.username, new_password)` attempts to reset the password using an external system.
        - `make_password(new_password)` securely hashes the new password before saving it.
    """
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
    method='get',
    operation_description="Retrieve a user's preferred profile language.",
    responses={200: 'Successfully retrieved the language', 400: 'Bad Request'}, 
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_profile_language(request, id):
    """
    Retrieves the language preference of a user's profile.

    This function:
    - Fetches the `Profile` associated with the given `User` ID.
    - Returns the user's selected language as a JSON response.

    Args:
        request (HttpRequest): The HTTP request (not used in processing).
        id (int): The unique identifier of the user whose language preference is being retrieved.

    Returns:
        JsonResponse: A JSON response containing the user's language setting.

    Exceptions:
        - `User.DoesNotExist`: Raised if no user with the given ID exists.
        - `Profile.DoesNotExist`: Raised if the user's profile is missing.
        - `Exception`: Catches other unexpected errors.

    HTTP Status Codes:
        - 200: Successfully retrieved the profile language.
        - 400: If the user or profile does not exist.

    Dependencies:
        - `User`: The model representing the user.
        - `Profile`: The model storing additional profile information.

    Example Response:
        - Success: {"language": "en"}
        - Failure: {"error": "User does not exist."}

    """
    profile = Profile.objects.get(user=User.objects.get(id=id))
    return JsonResponse({"language": profile.language})


@swagger_auto_schema(
    method='put',
    operation_description="Update a user's profile language preference and modify WAF rule descriptions accordingly.",
    request_body=Schema(
        type=TYPE_OBJECT,
        required=['language'],
        properties={
            'language': Schema(
                type=TYPE_STRING,
                enum=['en', 'fr'],
                description="Preferred language for the profile and WAF rule descriptions. Options: 'en' (English) or 'fr' (French)."
            )
        }
    ),
    responses={200: "Language updated successfully", 400: "Bad Request"},
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_language(request, id):
    """
    Updates a user's profile language and modifies WAF rule descriptions accordingly.

    This function:
    - Retrieves the user's profile.
    - Updates the profile's language setting.
    - Adjusts `RulesWaf` descriptions based on the selected language.
    - Saves the updated profile data.

    Args:
        request (HttpRequest): The HTTP request containing language update data.
        id (int): The unique identifier of the user whose profile language is being updated.

    Returns:
        JsonResponse:
            - On success: JSON response with a success message.
            - On failure: JSON response with an error message and HTTP status 400.

    Workflow:
        1. Retrieves the user's profile from the database.
        2. Serializes and validates the language update request.
        3. Updates the `description` field of `RulesWaf` objects where `created=False`:
            - If the selected language is English (`"en"`), descriptions are set to `description_english`.
            - Otherwise, descriptions are set to `description_french`.
        4. Saves the updated profile.
        5. Returns success or error responses.

    Exceptions:
        - `User.DoesNotExist`: Raised if the user ID does not exist.
        - `Profile.DoesNotExist`: Raised if the user profile is missing.
        - `Exception`: Catches other unexpected errors.

    HTTP Status Codes:
        - 200: Language successfully updated.
        - 400: Validation or processing error.

    Dependencies:
        - `User`: The model representing the user.
        - `Profile`: The model storing additional profile information.
        - `RulesWaf`: Model containing WAF rules with multilingual descriptions.
        - `ProfileSerializer`: Serializer for profile updates.

    Example Response:
        - Success: {"msg": "Language successfully updated."}
        - Failure: {"error": "Error message describing the failure."}
    """
    try:
        profile = Profile.objects.get(user=User.objects.get(id=id))
        data = request.data
        lang = data.get("language", "")
        if lang not in ["en", "fr"]:
            return JsonResponse({"error": f"{ERROR_MESSAGES_INVALID} {CONSTANT_DATA}"}, status=400)
        # Change language of rule waf description
        if lang == "en":
            for rule in RulesWaf.objects.filter(created=False):
                rule.description = rule.description_english
                rule.save()
        else:
            for rule in RulesWaf.objects.filter(created=False):
                rule.description = rule.description_french
                rule.save()
        profile.language = lang
        profile.save()
        return JsonResponse({"msg": f"{CONSTANT_LANGUAGE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
    except (User.DoesNotExist, Profile.DoesNotExist):
        return JsonResponse({"error": f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
