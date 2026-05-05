from backend.managementGroup.models import *
from django.core.management.base import BaseCommand
from django.db import IntegrityError



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            Group.objects.create(groupname='wheel',gid=998)
            return "wheel added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)