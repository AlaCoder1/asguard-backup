from django.contrib.auth import get_user_model
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
from django.core import serializers
# Create your views here.


# User = get_user_model()

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
        if '@' in username:
            if not ad_servers.exists():
                msg = "No Active Directory servers registered in the database."
                return JsonResponse({'msg': msg}, status=400)
            # Perform LDAP authentication
            for ad_server in ad_servers:
                ldap_uri = f"{'ldaps' if ad_server.ssl_tls_activation else 'ldap'}://{ad_server.server_url}:{ad_server.port}"
                ldap_conn = ldap.initialize(ldap_uri)
                try:
                    ldap_conn.simple_bind_s(username, password)
                    result = ldap_conn.search_s(ad_server.search_base, ldap.SCOPE_SUBTREE, "(objectClass=user)", ['userPrincipalName'])
                    if result:
                        user_session=User.objects.get(email=username)
                        if (user_session is not None):
                            login(request, user_session)
                            CurrentUser = {"username": user_session.username, "email": user_session.email, "role": user_session.role}
                            settings.CurrentUserId = user_session.id
                            ldap_conn.unbind()
                            return JsonResponse({'msg': 'Success Authentification', 'currentUser': CurrentUser},status=status.HTTP_200_OK)
                        else:
                            return JsonResponse({'msg': 'User not Registred in Asguard'}, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                            return JsonResponse({'msg': 'User not Registred in AD Server'}, status=status.HTTP_401_UNAUTHORIZED)
                except ldap.LDAPError as e:
                    msg = f"Error connecting to Active Directory Verify your Credentiels {ad_server.server_name}"
                    return JsonResponse({'msg': msg}, status=400)
        else:
            serializer = ObtainTokenSerializer(data=data)
            if (serializer.is_valid()):
                user = authenticate(request, username=username, password=password)
                if (user is not None):
                    login(request, user)
                    userObject = User.objects.get(username=username)
                    userDict = userObject.__dict__
                    CurrentUser = {"username":userDict['username'],"email":userDict['email'],"role":userDict['role']}
                    settings.CurrentUserId = userDict['id']
                    return JsonResponse({'message': ' Success Authentification',"currentUser":CurrentUser}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'message': 'Invalid credentiels'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return JsonResponse({'message': 'Invalid username or password'},status=status.HTTP_401_UNAUTHORIZED)


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
        print('********************',price)
       

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
