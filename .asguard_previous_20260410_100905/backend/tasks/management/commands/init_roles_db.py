from backend.managementUsers.models import Roles
from django.core.management.base import BaseCommand
from django.db import IntegrityError



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            Roles.objects.create(name='admin',fonctionalities=['all'])
            Roles.objects.create(name='default',fonctionalities=None)
            Roles.objects.create(name='viewer',fonctionalities=None)
            return "Roles added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)