from backend.proxy.models import *
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        squid_conf_instance = ServerSatus()
        squid_conf_instance.status_server = False
        squid_conf_instance.save()
