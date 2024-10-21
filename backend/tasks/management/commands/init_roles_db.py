from backend.managementUsers.models import Roles
from django.core.management.base import BaseCommand
from django.db import IntegrityError



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        list_fonctionalities = [
            "Firewall",
            "ZTNA"
        ]
        try:
            Roles.objects.create(name='admin',fonctionalities='all')
            Roles.objects.create(name='default',fonctionalities=list_fonctionalities)
            Roles.objects.create(name='viewer',fonctionalities='all')
            return "Roles added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)