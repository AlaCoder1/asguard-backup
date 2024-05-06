from rest_framework import status
from django.contrib.auth import authenticate, login
from django.conf import settings
from backend.managementUsers.models import User,Profile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.mime.image import MIMEImage
from datetime import datetime, timedelta 
from .serializers import *
from .models import VerificationCode
import smtplib
import random
import string
# import qrcode
import time
import os

def normal_connect(request,data):
    user = authenticate(request, username=data['username'], password=data['password'])
    if (user is not None):
        userObject = User.objects.get(username=data['username'])
        userDict = userObject.__dict__
        CurrentUser = {"id": userDict["id"], "username":userDict['username'], "email":userDict['email'], "role":userDict['role']}
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
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image
    img_path = "qr_code.png"
    img.save(img_path)


    html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QR Code Email</title>
            <style>
                /* Add your CSS styles here */
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #333;
                }}
                p {{
                    color: #666;
                }}
                .qr-code {{
                    margin-top: 20px;
                    text-align: center;
                }}
                .qr-code img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>QR Code Verification</h1>
                <p>Welcome {username},</p>
                <p>
                <div class="qr-code">Please verify your account by scan the QR code attached:
                    <img src="cid:qr_code">
                </div>
                <p>Thank you!</p>
            </div>
        </body>
        </html>
        """


    subject = 'Welcome ' + username
    msg = EmailMessage()
    msg.set_content(html_content, subtype='html')
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = email


    # Load the image
    with open(img_path, 'rb') as img_file:
        img_data = img_file.read()
        msg.add_alternative(html_content, subtype='html')
        msg.get_payload()[0].add_related(img_data, 'image', 'png', cid='qr_code')
    
    server = smtplib.SMTP(settings.EMAIL_HOST, 587)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    # msg.attach(MIMEText(html_content, 'plain'))


    server.sendmail(settings.EMAIL_HOST_USER, [email], msg.as_string())
    server.quit()

    # time.sleep(60)
    os.remove(img_path)

def send_verification_code(email,username):
    user = User.objects.get(email=email)
    verification_code = generate_verification_code()
    send_email_to_user(email, verification_code, username)
    expiration_time = datetime.now() + timedelta(minutes=30)
    VerificationCode.objects.update_or_create(user=user, defaults={'code': verification_code, 'expiration_time': expiration_time})
    return True