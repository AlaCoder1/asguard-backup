from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from backend.authentification.constant_variables import STRIPE_CANCEL_URL, STRIPE_SECRET_KEY, STRIPE_SUCCESS_URL
from .serializers import *
import json
from django.http import JsonResponse
from backend.managementUsers.models import User
from drf_yasg.utils import swagger_auto_schema
import stripe
from backend.LdapServer.models import ADServer
import ldap
from email.mime.text import MIMEText
import smtplib
import random
import string
import time
# Create your views here.

def normal_connect(request,data):
    serializer = ObtainTokenSerializer(data=data)
    if (serializer.is_valid()):
        user = authenticate(request, username=data['username'], password=data['password'])
        if (user is not None):
            login(request, user)
            userObject = User.objects.get(username=data['username'])
            userDict = userObject.__dict__
            CurrentUser = {"username":userDict['username'],"email":userDict['email'],"role":userDict['role']}
            settings.CurrentUserId = userDict['id']
            return 'Success Authentification',CurrentUser, status.HTTP_200_OK
        else:
            return 'Invalid credentiels',None,status.HTTP_401_UNAUTHORIZED
    else:
        return 'Invalid username or password',None,status.HTTP_401_UNAUTHORIZED
    
def exist_user_email(username):
    try:
        user_session = User.objects.get(email=username)
        return user_session
    except User.DoesNotExist:
        return False
    
@swagger_auto_schema(
    method='POST',
    request_body=ObtainTokenSerializer,
    responses={201: 'Created', 400: 'Bad Request'},
    security=[{"session_auth": []}],  # Specify the security requirement
    operation_summary="Summary of your API endpoint",
    operation_description="Description of your API endpoint",
)
     
@api_view(['POST'])
@permission_classes([AllowAny])
def authentification(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        ad_servers = ADServer.objects.all()
        user_session = exist_user_email(username)
        if '@' in username:
            if not ad_servers.exists():
                return JsonResponse({'message': "No Directory servers registered in the database."}, status=400)
            if user_session == False:
                return JsonResponse({'message': 'User Not Registred in Asguard'}, status=401)
            else:
                print({"user_session.id_server_id":user_session.id_server_id})
                if user_session.id_server_id is None:
                    authentication_server=False
                else:
                    server = ADServer.objects.get(id = user_session.id_server_id)
                    ldap_uri = f"{'ldaps' if server.ssl_tls_activation else 'ldap'}://{server.server_url}:{server.port}"
                    ldap_conn = ldap.initialize(ldap_uri)
                    if server.server_type=="ad":
                        try :  
                            ldap_conn.simple_bind_s(username, password) 
                            result = ldap_conn.search_s(server.search_base, ldap.SCOPE_SUBTREE, "(objectClass=user)", ['userPrincipalName'])
                            if result:
                                authentication_server=True
                        except ldap.INVALID_CREDENTIALS as e:
                            authentication_server=False
                            return JsonResponse({'message': 'Invalid credentials'},status=500)   
                            
                        except ldap.SERVER_DOWN:
                            authentication_server=False
                            return JsonResponse({'message': 'directory server is unreachable'},status=500)    
                            
                    elif server.server_type=="openldap":   
                        try : 
                            dn_user = user_session.dn_user
                            ldap_conn.simple_bind_s(dn_user,password)
                            authenticated_dn = ldap_conn.whoami_s()
                            if authenticated_dn:
                                authentication_server=True
                        except ldap.INVALID_CREDENTIALS as e:
                            authentication_server=False
                            return JsonResponse({'message': ' Invalid credentials'},status=500)   
                            
                        except ldap.SERVER_DOWN:
                            authentication_server=False
                            return JsonResponse({'message': 'directory server is unreachable'},status=500)   
            if authentication_server:
                login(request, user_session)
                userObject = User.objects.get(email=data['username'])
                userDict = userObject.__dict__
                CurrentUser = {"username":userDict['username'],"email":userDict['email'],"role":userDict['role']}
                settings.CurrentUserId = userDict['id']
                ldap_conn.unbind()
                return JsonResponse({'message': 'Success Authentification ',"currentUser":CurrentUser},status=200)
            else:
                return JsonResponse({'message':'Verify your Credentiels'}, status=401)
                    
        else:
            message,CurrentUser,status =normal_connect(request,data)
            return JsonResponse({'message': message,"currentUser":CurrentUser}, status=status)

@swagger_auto_schema(
    method='GET',
    responses={201: 'Created', 400: 'Bad Request'},
    security=[{"session_auth": []}],  # Specify the security requirement
    operation_summary="Summary of your API endpoint",
    operation_description="Description of your API endpoint",
)
@api_view(['GET'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return JsonResponse({"msg": 'User Logged out successfully'})

def show_url(request):
    host = request.get_host()
    if host.startswith("127"):
        url="http://"+host
    else:
        url="https://"+host
    print('url',url)
    return url

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def create_checkout_session(request):
    if request.method == 'POST':
        data = request.data
        subscription_id = data['subscription_id']
        status = data['status']
        price = data['price']
        # card_type = data['card_type']  # Assuming card_type is provided in the request data
        card_type = 'card'
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            url=show_url(request)
            print({"url":url})
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
            print({
                'checkout_session': checkout_session.metadata.subscription_id
            })
            return Response(checkout_session)
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request'})


from django.views.decorators.csrf import csrf_exempt
from .models import VerificationCode
###### data in settings.py and .env
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'mh.benelghali@numeryx.fr'  
EMAIL_HOST_PASSWORD = 'Ess4live+++'

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=8))

def send_email_to_user(email, code, username):
    subject = 'Welcome ' + username
    message = f'Welcome {username},\n\nThis is your account:\n* EMAIL: {email}\n* Your verification code is: {code}\n\nBest regards'
    server = smtplib.SMTP(EMAIL_HOST, 587)
    server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = email
    server.sendmail(EMAIL_HOST_USER, [email], msg.as_string())
    server.quit()

from datetime import datetime, timedelta   
@csrf_exempt
def send_verification_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data['email']
        username = data['username']
        
        user = User.objects.get(email=email)
        verification_code = generate_verification_code()

        send_email_to_user(email, verification_code, username)
        expiration_time = datetime.now() + timedelta(minutes=2)
        VerificationCode.objects.update_or_create(user=user, defaults={'code': verification_code, 'expiration_time': expiration_time})

        return JsonResponse({"message": "Verification code sent successfully"})

from django.utils import timezone
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
                    return JsonResponse({"message": "Verification successful"})
                else:
                    return JsonResponse({"message": "Invalid verification code"})
            else:
                verification_code.delete()
                return JsonResponse({"message": "Verification code expired. Please request a new one."})
        except VerificationCode.DoesNotExist:
            return JsonResponse({"message": "No verification code found for this email"})

@csrf_exempt
def resend_verification_code(request,id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        
        email = user.email
        username = user.username

        verification_code = generate_verification_code()
        send_email_to_user(email, verification_code, username)

        expiration_time = datetime.now() + timedelta(minutes=2)
        VerificationCode.objects.update_or_create(user=user, defaults={'code': verification_code, 'expiration_time': expiration_time})

        return JsonResponse({"message": "Verification code resent successfully"})
