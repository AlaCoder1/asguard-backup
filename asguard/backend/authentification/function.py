from itertools import groupby
from operator import itemgetter
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from backend.managementUsers.models import User, Profile,Roles
from email.message import EmailMessage
from datetime import datetime, timedelta

from backend.subscription.models import plansFeatures 
from .models import VerificationCode
import smtplib
import random
import string
import qrcode
import os

import secrets
# Constants
CONSTANT_VERIFIFCATION_CODE = _("verification code")
# Success messages
SUCCESS_MESSAGES_LOGIN = _("Success Authentication")
SUCCESS_MESSAGES_SENT = _("is sent successfully")
# Error messages
ERROR_MESSAGES_INVALID_CREDENTIALS = _("Invalid credentials")


def normal_connect(request,data):
    user = authenticate(request, username=data['username'], password=data['password'])
    if user:
        user_object = User.objects.get(username=data['username'])
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
        settings.CurrentUserId = user_dict['id']
        
        if profile.is_enable_2FA is False:
            login(request, user)
            return SUCCESS_MESSAGES_LOGIN, current_user, status.HTTP_200_OK
        else:
            if send_verification_code(user_dict['email'], user_dict['username']):
                return f"{CONSTANT_VERIFIFCATION_CODE} {SUCCESS_MESSAGES_SENT}", current_user, status.HTTP_200_OK
            else:
                print('code incorrect')
                return f"incorrect code , please try again", current_user, status.HTTP_401_UNAUTHORIZED
    else:
        return ERROR_MESSAGES_INVALID_CREDENTIALS, None, status.HTTP_401_UNAUTHORIZED
    
def exist_user_email(username):
    try:
        user_session = User.objects.get(email=username)
        return user_session
    except User.DoesNotExist:
        return False

def show_url(request):
    host = request.get_host()
    # if host.startswith("127"):
    #     url="https://"+host
    # else:
    url="https://"+host
    return url

def generate_verification_code():
    return ''.join(secrets.choice(string.digits) for _ in range(6))

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


def group_descriptions_by_plan():
    queryset = plansFeatures.objects.values('plan_id', 'description')
    # Sort by plan_id to make groupby work
    sorted_queryset = sorted(queryset, key=itemgetter('plan_id'))

    # Group by plan_id and then format as required
    grouped_descriptions = []
    for plan_id, group in groupby(sorted_queryset, key=itemgetter('plan_id')):
        list_descriptions = [item['description'] for item in group]
        grouped_descriptions.append({
            "plan_id": plan_id,
            "descriptions": list_descriptions
        })

    return grouped_descriptions


def get_plan_ids_by_descriptions(list_descriptions, grouped_data):
    """
    Function to get plan_ids that match the given list of descriptions.

    Parameters:
    list_descriptions (list): The descriptions to match.
    grouped_data (list): The grouped data returned from the previous query.

    Returns:
    list: A list of plan_ids that contain all the given descriptions.
    """
    # Filter plan_ids where all descriptions match
    for group in grouped_data:
        if group['descriptions'] == list_descriptions:
            return group['plan_id']

    return None
