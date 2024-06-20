from backend.subscription.models import Organization
from django.core.management.base import BaseCommand
from django.db import IntegrityError

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-o', '--organization', type=str, help='Define a organization name')
    def handle(self, *args, **kwargs):
        try:
            organization = kwargs['organization']
            if organization and not Organization.objects.filter(organization=organization).exists():
                organization = f'{organization}'
                organization=Organization.objects.create(organization=organization)
                return "organization added succesffuly"
            else:
                return "organization already exist"
        except IntegrityError as e:
            return "Error: " + str(e)