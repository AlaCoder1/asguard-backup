from backend.managementUsers.models import *
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

# class Command(BaseCommand):
#     def handle(self, *args, **kwargs):
#         # Your code to add data to the database here
#         try:
#             User.objects.create(username='root', password=make_password("root"))
#             return "root added succesffuly"
#         except IntegrityError as e:
#             return "Error: " + str(e)
        
## create user with arguments
class Command(BaseCommand):
    
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-u', '--name', type=str, help='Define a user name')
        parser.add_argument('-p', '--pw', type=str, help='Define a user password')
        parser.add_argument('-r', '--role', type=str, help='Define a user role')
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            name = kwargs['name']
            pw = kwargs['pw']
            role = kwargs['role']
            if name and pw and role:
                username = f'{name}'
                password = kwargs.get('pw') 
                role = f'{role}'
            role_db = Roles.objects.get(name=role)
            user=User.objects.create(username=username, password=make_password(password), role = role_db)
            Profile.objects.create(user=user)
            return "user added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)