from rest_framework import status
from django.contrib.auth import authenticate, login
from django.conf import settings
from backend.managementUsers.models import User,Profile
from email.mime.text import MIMEText
from datetime import datetime, timedelta 
from .serializers import *
from .models import VerificationCode
import smtplib
import random
import string

def normal_connect(request,data):
    user = authenticate(request, username=data['username'], password=data['password'])
    if (user is not None):
        userObject = User.objects.get(username=data['username'])
        userDict = userObject.__dict__
        CurrentUser = {"username":userDict['username'],"email":userDict['email'],"role":userDict['role']}
        settings.CurrentUserId = userDict['id']
        profile = Profile.objects.get(user=userObject.pk)
        if profile.is_enable_2FA is False:
            login(request, user)
            return 'Success Authentification',CurrentUser, status.HTTP_200_OK,False
        else:
            if send_verification_code(userDict['email'],userDict['username']):
                return "Verification code sent successfully",CurrentUser, status.HTTP_200_OK,True
    else:
        return 'Invalid credentiels',None,status.HTTP_401_UNAUTHORIZED,False
    
def exist_user_email(username):
    try:
        user_session = User.objects.get(email=username)
        return user_session
    except User.DoesNotExist:
        return False

def show_url(request):
    host = request.get_host()
    if host.startswith("127"):
        url="http://"+host
    else:
        url="https://"+host
    return url

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=8))

def send_email_to_user(email, code, username):
    subject = 'Welcome ' + username
    message = f'Welcome {username},\n\nplease verify your account:\n* EMAIL: {email}\n* Your verification code is: {code}\n\nBest regards'
    server = smtplib.SMTP(settings.EMAIL_HOST, 587)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = email
    server.sendmail(settings.EMAIL_HOST_USER, [email], msg.as_string())
    server.quit()

def send_verification_code(email,username):
    user = User.objects.get(email=email)
    verification_code = generate_verification_code()
    send_email_to_user(email, verification_code, username)
    expiration_time = datetime.now() + timedelta(minutes=30)
    VerificationCode.objects.update_or_create(user=user, defaults={'code': verification_code, 'expiration_time': expiration_time})
    return True