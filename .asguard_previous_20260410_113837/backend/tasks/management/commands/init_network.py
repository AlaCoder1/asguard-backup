from backend.network.models import *
from django.core.management.base import BaseCommand
from django.db import IntegrityError



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            settings.CurrentUserId = 1
            interface=Interface.objects.get(id=1)
            IP4Config.objects.create(interface=interface,created_at=timezone.now,updated_at=timezone.now,created_by=1,updated_by=1)
            GenericConfig.objects.create(interface=interface,created_at=timezone.now,updated_at=timezone.now,created_by=1,updated_by=1)
            # GenericConfig.objects.create(interface=None,typeip4='None',typedhcp=None,ip_address=None,netmask=None,reject=None,hostname=None,alias_add=None,alias_mask=None,timeout=None,retry=None,reboot=None,backoff=None,select_timeout=None,dhcp_client=None,domaine_name=None,domain_server=None,lease_time=None,request=None,require=None,created_at=None,updated_at=None,created_by=None,updated_by=None)
            return "IP4Config and GenericConfig added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)