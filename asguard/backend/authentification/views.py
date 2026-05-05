"""
This module provides authentication and subscription functionalities for an API using Django REST Framework.

It includes:
- Authentication via username/password with Active Directory or OpenLDAP verification.
- User login and logout.
- Two-factor authentication (2FA) using verification codes.
- Integration with Stripe for handling subscription payments.

Dependencies:
    - Django REST Framework (drf)
    - Django authentication modules
    - Stripe API
    - LDAP for directory authentication
    - DRF-YASG for API documentation

Constants:
    - `CONSTANT_USER_EMAIL`: Email constant for user authentication.
    - `CONSTANT_VERIFICATION_CODE`: Constant for verification code messages.
    - `SUCCESS_MESSAGES_*`: Various success messages.
    - `ERROR_MESSAGES_*`: Various error messages related to authentication and servers.

Functions:
    - `authentication(request)`: Handles user login with directory server authentication.
    - `logout_view(request)`: Logs out the current user session.
    - `create_checkout_session(request)`: Creates a Stripe checkout session for user subscriptions.
    - `verify_code(request, id)`: Verifies a user's 2FA code and logs them in if valid.

Models:
    - `User`: Represents application users.
    - `Profile`: Stores additional user information such as 2FA status.
    - `Roles`: Defines user roles and permissions.
    - `ADServer`: Represents directory servers for authentication.
    - `plan`: Represents subscription plans.

Example Usage:
    ```
    POST /api/authentication/
    {
        "username": "user@example.com",
        "password": "securepassword"
    }
    
    GET /api/logout/
    
    POST /api/create-checkout-session/
    {
        "features": ["Basic"],
        "status": "active",
        "price": 9.99
    }
    
    POST /api/verify-code/{id}/
    {
        "verification_code": "123456"
    }
    ```

"""

from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view,permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import login, logout
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import TYPE_ARRAY, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING, Schema
from datetime import datetime, timedelta

import json
import threading
import stripe
import ldap
from backend.backup.notifications import notify_user_login

from backend.authentification.function import get_plan_ids_by_descriptions, group_descriptions_by_plan

from .constant_variables import STRIPE_SECRET_KEY
from .function import exist_user_email, generate_verification_code, normal_connect, send_email_to_user, send_verification_code, show_url
from .models import VerificationCode
from backend.managementUsers.models import User, Profile, Roles
from backend.LdapServer.models import ADServer
from backend.subscription.models import plan
from django.views.decorators.http import require_http_methods

# Constants
CONSTANT_USER_EMAIL = _("Email")
CONSTANT_VERIFIFCATION_CODE = _("verification code")
# Success messages
SUCCESS_MESSAGES_LOGIN = _("Success Authentication")
SUCCESS_MESSAGES_LOGOUT = _("Success Logout")
SUCCESS_MESSAGES_SENT = _("is sent successfully")
SUCCESS_MESSAGES_RESENT = _("is re-sent successfully")
# Error messages
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_CREDENTIALS_SERVER_AD = _("Invalid credentials for directory server login")
ERROR_MESSAGES_INVALID_CREDENTIALS = _("Invalid credentials")
ERROR_MESSAGES_NO_SERVERS = _("No directory servers registered")
ERROR_MESSAGES_SERVER_UNREACHABLE = _("Directory server is unreachable")
ERROR_MESSAGES_USER_NOTASSIGNED = _("Email not assigned in Asguard. Contact your administrator")
ERROR_MESSAGES_EXPIRED = _("has expired")
 
 
@swagger_auto_schema(
    'POST', responses={200: 'Login successfully', 400: 'Bad Request'}, 
    security=[{"session_auth": []}],  # Specify the security requirement
    operation_summary="LOGIN API",
    operation_description="LOGIN API",
    request_body=Schema(
        type=TYPE_OBJECT, required=["username", "password"],
        properties={
            "username": Schema(type=TYPE_STRING, example="asguard"),
            "password": Schema(type=TYPE_STRING, example="asguard")
        }
                     ))
@api_view(['POST'])
@require_http_methods(['POST'])
@permission_classes([AllowAny])
def authentication(request):
    """
    Handles user authentication via Active Directory (AD) or OpenLDAP.

    This function verifies user credentials either through an LDAP-based authentication 
    process (for users with an email address) or a standard username/password authentication.

    Args:
        request (HttpRequest): The HTTP request containing authentication data.

    Returns:
        JsonResponse: A JSON response indicating authentication success or failure.
            - 200: Successful authentication (with or without 2FA).
            - 400: Bad request (e.g., missing AD servers, user not assigned to a server).
            - 401: Unauthorized (e.g., invalid credentials, non-existent user).
    
    Authentication Flow:
        1. If the request method is not POST, the function does nothing.
        2. Extracts `username` and `password` from the request data.
        3. Checks if `username` contains '@' (indicating an email-based login via AD/OpenLDAP).
           - If no AD servers are configured, returns an error.
           - If the user does not exist in the session, returns an error.
           - If assigned to an AD server, attempts LDAP authentication:
             - AD: Uses `simple_bind_s` with `userPrincipalName`.
             - OpenLDAP: Uses `simple_bind_s` with the user's DN.
        4. On successful authentication, retrieves user details and role information.
        5. If 2FA is enabled, sends a verification code and requires user validation.
        6. Otherwise, logs the user in and returns a success response.

    Dependencies:
        - `ADServer`: Model containing LDAP server configurations.
        - `Profile`: Model storing user profile details (e.g., 2FA settings).
        - `Roles`: Model defining user roles and permissions.
        - `ldap`: Python LDAP library for directory authentication.
        - `send_verification_code`: Function for sending 2FA verification codes.
    """
    if (request.method == "POST"):
        data = request.data
        username = data['username']
        password = data['password']
        ad_servers = ADServer.objects.all()
        user_session = exist_user_email(username)
        if '@' in username:
            if not ad_servers.exists():
                return JsonResponse({'message': ERROR_MESSAGES_NO_SERVERS}, status=400)
            if not user_session:
                return JsonResponse({'message': f"{CONSTANT_USER_EMAIL} {ERROR_MESSAGES_INEXISTANT}"}, status=401)
            else:
                authentication_server = False
                if user_session.id_server_id:
                    server = ADServer.objects.get(id = user_session.id_server_id)
                    ldap_uri = f"{'ldaps' if server.ssl_tls_activation else 'ldap'}://{server.server_url}:{server.port}"
                    ldap_conn = ldap.initialize(ldap_uri)
                    ldap_conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 5)
                    if server.server_type=="ad":
                        try :  
                            ldap_conn.simple_bind_s(username, password)
                            result = ldap_conn.search_s(server.search_base, ldap.SCOPE_SUBTREE,
                                                        "(objectClass=user)", ['userPrincipalName'])
                            if result:
                                authentication_server=True
                        except ldap.INVALID_CREDENTIALS:
                            return JsonResponse({'message': ERROR_MESSAGES_INVALID_CREDENTIALS_SERVER_AD}, status=400)
                        except ldap.SERVER_DOWN:
                            return JsonResponse({'message': ERROR_MESSAGES_SERVER_UNREACHABLE}, status=400)    
                    else: # server_type is openldap
                        try :
                            dn_user = user_session.dn_user
                            ldap_conn.simple_bind_s(dn_user,password)
                            authenticated_dn = ldap_conn.whoami_s()
                            if authenticated_dn:
                                authentication_server=True
                        except ldap.INVALID_CREDENTIALS:
                            return JsonResponse({'message': ERROR_MESSAGES_INVALID_CREDENTIALS_SERVER_AD}, status=400)  
                        except ldap.SERVER_DOWN:
                            return JsonResponse({'message': ERROR_MESSAGES_SERVER_UNREACHABLE}, status=400)  
                       
                else:
                    return JsonResponse({'message': ERROR_MESSAGES_USER_NOTASSIGNED}, status=400)    
               
            if authentication_server:
                user_object = User.objects.get(email=data['username'])
                user_dict = user_object.__dict__
                profile = Profile.objects.get(user=user_object.pk)
                profile_dict = profile.__dict__
                role = Roles.objects.get(id=user_dict['role_id'])
                current_user = {
                    "id": user_dict['id'],
                    "username": user_dict['username'],
                    "email": user_dict['email'],
                    "is_enable_2FA": profile_dict['is_enable_2FA'],
                    # "role": user_dict['role'],
                    "role": role.name,
                    "list_fonctionalities":role.fonctionalities
                      }
                if not profile.is_enable_2FA:
                    login(request, user_session)
                   
                    settings.CurrentUserId = user_dict['id']
                    ldap_conn.unbind()
                    return JsonResponse({'message': SUCCESS_MESSAGES_LOGIN,
                                         "currentUser": current_user},
                                         status=200)
                else:
                    if send_verification_code(user_dict['email'],user_dict['username']):
 
                        return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {SUCCESS_MESSAGES_SENT}",
                                         "currentUser": current_user,"redirect":True},status=200)
                    return JsonResponse({"message": "incorrect code , please try again",
                                         "currentUser": current_user,"redirect":True}, status=401)
               
            return JsonResponse({'message': ERROR_MESSAGES_INVALID_CREDENTIALS}, status=401)
 
        # Connection with username and password
        message, current_user, status = normal_connect(request, data)
        _ip = request.META.get("REMOTE_ADDR", "")
        if status == 200:
            threading.Thread(target=notify_user_login, args=(username, _ip, True, "login"), daemon=True).start()
        else:
            threading.Thread(target=notify_user_login, args=(username, _ip, False, "failed"), daemon=True).start()
        return JsonResponse({'message': message, "currentUser": current_user}, status=status)
 
 
@swagger_auto_schema('GET', responses={200: 'Logout successfully', 400: 'Bad Request'},
                     security=[{"session_auth": []}],  # Specify the security requirement
                     operation_summary="Summary of your API endpoint",
                     operation_description="Description of your API endpoint")
@api_view(['GET'])  
@require_http_methods(['GET'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    Logs out the currently authenticated user.

    This function invalidates the user's session and logs them out. 
    It can be accessed by any user, regardless of authentication status.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response confirming logout with a success message.
    
    HTTP Status:
        - 200: Logout successful.

    Decorators:
        - `@require_http_methods(['GET'])`: Restricts the view to handle only GET requests.
        - `@permission_classes([AllowAny])`: Allows access to all users, authenticated or not.

    Dependencies:
        - `logout`: Django's built-in logout function to clear user sessions.
        - `SUCCESS_MESSAGES_LOGOUT`: A predefined constant message for successful logout.
    """
    username = request.user.username if request.user.is_authenticated else "unknown"
    _ip = request.META.get("REMOTE_ADDR", "")
    logout(request)
    threading.Thread(target=notify_user_login, args=(username, _ip, True, "logout"), daemon=True).start()
    return JsonResponse({"msg": SUCCESS_MESSAGES_LOGOUT})
 
# @swagger_auto_schema(
#     'POST', 

#     responses={200: 'subscrpition successfully', 400: 'Bad Request'}, 
#     security=[{"session_auth": []}],  # Specify the security requirement
#     operation_summary="subscrpition API",
#     operation_description="Create a Stripe checkout session for subscription plans.",
#     request_body=Schema(
#         type=TYPE_OBJECT, required=['features', 'status', 'price'],
#         properties={
#             "features": Schema(type=TYPE_ARRAY,items=Schema(type=TYPE_STRING), example=["squid","ZTNA"]),
#             "status": Schema(type=TYPE_STRING, example="True"),
#             "price": Schema(type=TYPE_INTEGER, example=1199)
#         }
#     )
#  )
# @api_view(['POST'])
# @authentication_classes([SessionAuthentication])
# def create_checkout_session(request):
#     """
#     Creates a Stripe checkout session for processing subscription payments.

#     This function initializes a payment session based on the selected subscription 
#     plan and price provided in the request data. It integrates with Stripe to 
#     generate a checkout URL.

#     Args:
#         request (HttpRequest): The HTTP request containing subscription details.

#     Returns:
#         Response: A Stripe checkout session URL on success.
#         JsonResponse: An error message if the session creation fails.

#     Workflow:
#         1. Extracts `features`, `status`, and `price` from request data.
#         2. Determines the subscription plan based on selected features:
#             - "Basic" → Retrieves `Basic` plan from the database.
#             - "Full" → Retrieves `Full` plan from the database.
#             - Otherwise, matches features to a plan using `group_descriptions_by_plan()`.
#         3. Sets Stripe API key and prepares checkout session parameters.
#         4. Creates a Stripe checkout session with:
#             - Payment method (`card`).
#             - Subscription details (plan, price, and metadata).
#             - Success and cancellation URLs.
#         5. Returns the checkout session response.

#     HTTP Status:
#         - 200: Checkout session successfully created.
#         - 400: Error in processing the request.

#     Dependencies:
#         - `stripe`: Stripe API for payment processing.
#         - `plan`: Model storing subscription plans.
#         - `group_descriptions_by_plan()`: Groups plan descriptions for selection.
#         - `get_plan_ids_by_descriptions()`: Matches selected features to a plan.
#         - `show_url(request)`: Retrieves the base URL for success/cancel redirection.

#     Raises:
#         - Exception: Catches any errors during session creation and returns an error response.
#     """
#     data = request.data
#     list_features = data['features']
#     if "Basic"in list_features:
#         subscription_plan = plan.objects.get(slug="Basic")
#         plan_id = subscription_plan.pk
#     elif "Full" in list_features:
#         subscription_plan = plan.objects.get(slug="Full")
#         plan_id = subscription_plan.pk
#     else:
#         grouped_data = group_descriptions_by_plan()
#         plan_id = get_plan_ids_by_descriptions(list_features, grouped_data)
 
#     status = data['status']
#     price = data['price']
#     card_type = 'card'
#     stripe.api_key = STRIPE_SECRET_KEY
#     try:
#         url=show_url(request)
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=[card_type],  # Specify the payment method type (e.g., card)
#             line_items=[
#                 {
#                     'price_data': {
#                         'currency': 'eur',
#                         'unit_amount': int(price * 100),  # Convert price to cents
#                         'product_data': {
#                             'name': 'Asguard Subscription',
#                             'images': ['https://www.numeryx.fr/wp-content/themes/numeryx/assets/images/bg-Asguard.jpg'],
#                             'description': 'Asguard Subscription',
#                             'metadata': {
#                                 'subscription_id': plan_id,
#                                 'status': status,
#                             }
#                         },
#                     },
#                     'quantity': 1,
#                 },
#             ],
#                 metadata = {
#                 'subscription_id': plan_id,
#                 'status': status,
#             },
#             mode='payment',
#             success_url = f'{url}/success/?subscription_id={plan_id}',
#             cancel_url= f'{url}/asguard/subscription/'
#         )
 
#         return Response(checkout_session)
#     except Exception as e:
#         return JsonResponse({'error': str(e)})

 
# @csrf_exempt
@require_http_methods(["POST"])
def verify_code(request,id):
    """
    Verifies a user's authentication code and logs them in if valid.

    This function checks whether the provided verification code matches the one 
    stored for the user. If the code is valid and not expired, the user is logged in.

    Args:
        request (HttpRequest): The HTTP request containing the verification code.
        id (int): The ID of the user attempting verification.

    Returns:
        JsonResponse: 
            - 200: If login is successful or if the code has expired.
            - 400: If the code is invalid or does not exist.

    Workflow:
        1. Extracts the verification code from the request body.
        2. Retrieves the user and their stored verification code.
        3. Checks if the code is still valid:
            - If valid, logs in the user and deletes the verification code.
            - If expired, deletes the code and returns an expiration message.
            - If invalid, returns an error response.
        4. Handles cases where no verification code exists.

    HTTP Status:
        - 200: Login successful or verification code expired.
        - 400: Invalid verification code or no code found.

    Dependencies:
        - `User`: Django's user model.
        - `VerificationCode`: Model storing temporary authentication codes.
        - `timezone.now()`: Checks if the code is still valid.
        - `login()`: Logs in the user upon successful verification.

    Raises:
        - `VerificationCode.DoesNotExist`: If no verification code is found for the user.
    """
    if request.method == 'POST':
        user = User.objects.get(id=id)
        data = json.loads(request.body)
        user_input = data['verification_code']
        try:
            verification_code = VerificationCode.objects.get(user=user.pk)
            if timezone.now() <= verification_code.expiration_time:
                if user_input == verification_code.code:
                    verification_code.delete()
                    login(request, user)
                    return JsonResponse({"message": SUCCESS_MESSAGES_LOGIN}, status=200)
                return JsonResponse({"message": ERROR_MESSAGES_INVALID_CREDENTIALS}, status=400)
           
            # Verification code expired
            verification_code.delete()
            return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {ERROR_MESSAGES_EXPIRED}"}, status=200)
        except VerificationCode.DoesNotExist:
            return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


# @csrf_exempt
@require_http_methods(["POST"])
def resend_verification_code(request,id):
    """
    Resends a new verification code to the user's email.

    This function generates a new verification code, sends it to the user's 
    registered email, and updates the expiration time in the database.

    Args:
        request (HttpRequest): The HTTP request triggering the resend action.
        id (int): The ID of the user requesting a new verification code.

    Returns:
        JsonResponse: 
            - 200: If the verification code is successfully generated and sent.

    Workflow:
        1. Retrieves the user by ID.
        2. Generates a new verification code using `generate_verification_code()`.
        3. Sends the new code via email using `send_email_to_user()`.
        4. Updates or creates a `VerificationCode` entry for the user, setting:
            - The new code.
            - A new expiration time (30 minutes from the current time).
        5. Returns a success message.

    HTTP Status:
        - 200: Verification code successfully resent.

    Dependencies:
        - `User`: Django's user model.
        - `generate_verification_code()`: Function that generates a new verification code.
        - `send_email_to_user()`: Function to send the verification code via email.
        - `VerificationCode`: Model storing authentication codes.
        - `datetime.now() + timedelta(minutes=30)`: Sets the code expiration time.

    Raises:
        - `User.DoesNotExist`: If no user is found with the given ID.
    """
    if request.method == 'POST':
        user = User.objects.get(id=id)
        verification_code = generate_verification_code()
        send_email_to_user(user.email, verification_code, user.username)
        expiration_time = datetime.now() + timedelta(minutes=30)
        VerificationCode.objects.update_or_create(user=user,
                                                  defaults={'code': verification_code, 'expiration_time': expiration_time})
        return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {SUCCESS_MESSAGES_RESENT}"})
