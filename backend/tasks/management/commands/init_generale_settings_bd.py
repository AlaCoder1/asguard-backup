import re
from django.core.management.base import BaseCommand
from backend.settings.models import System, Timezone, Network
from backend.settings.function import get_time_zone,get_hostname,get_dns_servers
from django.db import IntegrityError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        timezone = get_time_zone()
        def extract_timezone(full_timezone):
            match = re.match(r'^([^\s]+)', full_timezone)
            if match:
                return match.group(1)
            else:
                return None
        time_zone = Timezone.objects.get(name = extract_timezone(timezone))
        hostname = get_hostname()
        
        list_dns_servers = get_dns_servers()
        print({"list_dns_servers":list_dns_servers})
        list_servers = []
        server_dns = {}
        for i in list_dns_servers:
            server_dns['gateway'] = {}
            server_dns['dns_server'] = i
            print({"server_dns":server_dns})
            list_servers.append(server_dns)
            server_dns = {}
        print({"list_servers":list_servers})

        try:
            System.objects.create(hostname=hostname,domaine='localdomain',time_zone =time_zone)
            Network.objects.create(prever_ipv4_ipv6=None,server_dns=list_servers,allow_server_dns = None,exclude_interfaces = None,getway_failover = None)
            return "generale settings added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)
        
    