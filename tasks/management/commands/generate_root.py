from managementUsers.models import *
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
        parser.add_argument('-u', '--name', type=str, help='Define a username name')
        parser.add_argument('-p', '--pw', type=str, help='Define a username password')
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            name = kwargs['name']
            pw = kwargs['pw']
            if name and pw:
                username = f'{name}'
                password = f'{pw}'
            User.objects.create(username=username, password=make_password(password))
            return "root added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)