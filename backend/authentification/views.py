from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import login, logout
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from backend.authentification.constant_variables import STRIPE_SECRET_KEY
from backend.authentification.function import exist_user_email, generate_verification_code, normal_connect, send_email_to_user, send_verification_code, show_url
from backend.managementUsers.models import User,Profile
from backend.LdapServer.models import ADServer
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime, timedelta 
from .models import VerificationCode
import json
import stripe
import ldap


# Constants
CONSTANT_USER = _("User")
CONSTANT_VERIFIFCATION_CODE = _("verification code")
# Success messages
SUCCESS_MESSAGES_LOGIN = _("Success Authentication")
SUCCESS_MESSAGES_LOGOUT = _("Success Logout")
SUCCESS_MESSAGES_SENT = _("is sent successfully")
SUCCESS_MESSAGES_RESENT = _("is re-sent successfully")
# Error messages
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_INVALID_CREDENTIALS = _("Invalid credentials")
ERROR_MESSAGES_NO_SERVERS = _("No directory servers registered")
ERROR_MESSAGES_SERVER_UNREACHABLE = _("Directory server is unreachable")
ERROR_MESSAGES_EXPIRED = _("has expired")


@swagger_auto_schema('POST', responses={201: 'Created', 400: 'Bad Request'},
                     security=[{"session_auth": []}],  # Specify the security requirement
                     operation_summary="Summary of your API endpoint",
                     operation_description="Description of your API endpoint")
@api_view(['POST'])
@permission_classes([AllowAny])
def authentication(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        ad_servers = ADServer.objects.all()
        user_session = exist_user_email(username)
        if '@' in username:
            if not ad_servers.exists():
                return JsonResponse({'message': ERROR_MESSAGES_NO_SERVERS}, status=400)
            if not user_session:
                return JsonResponse({'message': f"{CONSTANT_USER} {ERROR_MESSAGES_INEXISTANT}"}, status=401)
            else:
                authentication_server = False
                if user_session.id_server_id:
                    server = ADServer.objects.get(id = user_session.id_server_id)
                    ldap_uri = f"{'ldaps' if server.ssl_tls_activation else 'ldap'}://{server.server_url}:{server.port}"
                    ldap_conn = ldap.initialize(ldap_uri)
                    if server.server_type=="ad":
                        try :  
                            ldap_conn.simple_bind_s(username, password) 
                            result = ldap_conn.search_s(server.search_base, ldap.SCOPE_SUBTREE, 
                                                        "(objectClass=user)", ['userPrincipalName'])
                            if result:
                                authentication_server=True
                        except ldap.INVALID_CREDENTIALS:
                            return JsonResponse({'message': ERROR_MESSAGES_INVALID_CREDENTIALS}, status=400)
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
                            return JsonResponse({'message': ERROR_MESSAGES_INVALID_CREDENTIALS}, status=400)   
                        except ldap.SERVER_DOWN:
                            return JsonResponse({'message': ERROR_MESSAGES_SERVER_UNREACHABLE}, status=400)   
            if authentication_server:
                user_object = User.objects.get(email=data['username'])
                user_dict = user_object.__dict__
                profile = Profile.objects.get(user=user_object.pk)
                if not profile.is_enable_2FA:
                    login(request, user_session)
                    current_user = {"id": user_dict['id'], "username": user_dict['username'], "email": user_dict['email'],
                                    "role": user_dict['role']}
                    settings.CurrentUserId = user_dict['id']
                    ldap_conn.unbind()
                    return JsonResponse({'message': SUCCESS_MESSAGES_LOGIN, 
                                         "currentUser": current_user}, 
                                         status=200)
                elif send_verification_code(user_dict['email'],user_dict['username']):
                    return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {SUCCESS_MESSAGES_SENT}", 
                                         "redirect":True})
            return JsonResponse({'message': ERROR_MESSAGES_INVALID_CREDENTIALS}, status=401)

        # Connection with username and password
        message, current_user, status =normal_connect(request,data)
        return JsonResponse({'message': message, "currentUser": current_user}, status=status)


@swagger_auto_schema('GET', responses={201: 'Created', 400: 'Bad Request'},
                     security=[{"session_auth": []}],  # Specify the security requirement
                     operation_summary="Summary of your API endpoint",
                     operation_description="Description of your API endpoint")
@api_view(['GET'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return JsonResponse({"msg": SUCCESS_MESSAGES_LOGOUT})


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def create_checkout_session(request):
    data = request.data
    subscription_id = data['subscription_id']
    status = data['status']
    price = data['price']
    card_type = 'card'
    stripe.api_key = STRIPE_SECRET_KEY
    try:
        url=show_url(request)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[card_type],  # Specify the payment method type (e.g., card)
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': int(price * 100),  # Convert price to cents
                        'product_data': {
                            'name': 'Asguard Subscription',
                            'images': ['https://www.numeryx.fr/sites/default/files/gallery/ASGUARD%20bannirere%20site.png'],
                            'description': 'Asguard Subscription',
                            'metadata': {
                                'subscription_id': subscription_id,
                                'status': status,
                            }
                        },
                    },
                    'quantity': 1,
                },
            ],
                metadata = {
                'subscription_id': subscription_id,
                'status': status,
            },
            mode='payment',
            success_url = f'{url}/success/?subscription_id={subscription_id}',
            cancel_url= f'{url}/asguard/subscription/'
        )
        return Response(checkout_session)
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def verify_code(request,id):
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
                    return JsonResponse({"message": SUCCESS_MESSAGES_LOGIN})
                return JsonResponse({"message": ERROR_MESSAGES_INVALID_CREDENTIALS})
            
            # Verification code expired
            verification_code.delete()
            return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {ERROR_MESSAGES_EXPIRED}"})
        except VerificationCode.DoesNotExist:
            return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {ERROR_MESSAGES_INEXISTANT}"})

@csrf_exempt
def resend_verification_code(request,id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        verification_code = generate_verification_code()
        send_email_to_user(user.email, verification_code, user.username)
        expiration_time = datetime.now() + timedelta(minutes=30)
        VerificationCode.objects.update_or_create(user=user, 
                                                  defaults={'code': verification_code, 'expiration_time': expiration_time})
        return JsonResponse({"message": f"{CONSTANT_VERIFIFCATION_CODE} {SUCCESS_MESSAGES_RESENT}"})
