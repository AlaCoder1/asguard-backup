import json
import subprocess
from backend.dashboard.functions import add_sevice_DB, run_command, update_sevice_DB
from backend.dashboard.models import Services
from backend.network.models import *
from django.core.management.base import BaseCommand
from django.db import IntegrityError
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            list_info_services=[]
            list_service=[
            'sshd','suricata','squid',"ipsec"
            ]
            for s in list_service:
                output,_=run_command("sudo systemctl list-unit-files --type service | awk '{print $1}'")
                list_all_services=output.splitlines()
                status_install=False
                status_started=False
                status_enabled=False
                if s+'.service' in list_all_services:
                    status_install=True
                    if s!="ipsec":
                        aux_enabled,error=run_command("sudo systemctl is-enabled {}".format(s))
                        if aux_enabled.strip()=="enabled":
                            status_enabled=True
                        aux_started,error=run_command("sudo systemctl is-active  {}".format(s))
                        if aux_started.strip()=="active":
                            status_started=True
                    else:
                        aux_started,error=run_command("sudo ipsec status")
                        if aux_started.strip()!="":
                            status_started=True        
                service={
                    "service_name":s,
                    "description":"Service {}".format(s),
                    "status_enabled":status_enabled,
                    "status_started":status_started,
                    "status_install":status_install
                }
                list_info_services.append(json.dumps(service))
                if Services.objects.filter(service_name=s).exists():
                    aux_update=update_sevice_DB(s,service)
                    if aux_update is  not True:
                        return aux_update
                else:
                    aux_add=add_sevice_DB(service)
                    if aux_add is not True:
                        return aux_add
               
            return "All Services added in database Successfully!" 
                                
                            
                
        except IntegrityError as e:
            return "Error: " + str(e)
