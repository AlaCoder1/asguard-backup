from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ids_ips.function_sys import  read_from_yaml, save_in_yaml, update_config
import ruamel.yaml


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            status_enabled=False
            global_path="/var/log/suricata/"
            yaml_class = ruamel.yaml.YAML()
            suricata_path="/etc/suricata/suricata.yaml"
            data=read_from_yaml(suricata_path,yaml_class)
            data['outputs'][1]["eve-log"]['filename']=global_path+data['outputs'][1]["eve-log"]['filename']
            data['outputs'][7]['stats']['filename']=global_path+data['outputs'][7]['stats']['filename']
            data['outputs'][0]['fast']['filename']=global_path+data['outputs'][0]['fast']['filename']
            data['outputs'][0]['fast']['filetype']='regular'
            data['vars']['address-groups']['HOME_NET']="[10.0.0.0/8]"
            save_in_yaml(suricata_path,data,yaml_class) 
            aux_update_system=update_config(status_enabled)
            if aux_update_system is True:
                return "Config saved successfully"
            else:
                return aux_update_system
        except IntegrityError as e:
            return "Error: " + str(e)    