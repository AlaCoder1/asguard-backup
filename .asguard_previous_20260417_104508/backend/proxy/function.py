from email.mime.text import MIMEText
import random
import re
import smtplib
import string
import subprocess
from django.conf import settings
import psycopg2
import secrets
def send_email_to_user(email, password, username):
    subject = 'Welcome ' + username
    message = f'Welcome {username},\n\nThis is your account:\n* EMAIL: {email}\n* PASSWORD: {password}\n\nBest regards'
    server = smtplib.SMTP(settings.EMAIL_HOST, 587)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = email
    server.sendmail(settings.EMAIL_HOST_USER, [email], msg.as_string())

    server.quit()
    
    
def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def extract_names_from_file(file_path):
    names = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if lines:
            for line in lines:
                # Using regular expression to extract the text before the colon (username)
                match = re.match(r'^([^:]+):', line)
                if match:
                    names.append(match.group(1).strip())
            return names
        else:
            return False
        
def change_pwd_squid(username_squid,password_squid):
    squid_conf_path = '/etc/squid/squid_passwd'
    try:
        subprocess.run(['htpasswd', '-b', squid_conf_path, username_squid, password_squid], check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False
    
