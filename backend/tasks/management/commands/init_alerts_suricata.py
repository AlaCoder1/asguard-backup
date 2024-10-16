from django.core.management.base import BaseCommand

from django.db import IntegrityError

from backend.ids_ips.function_sys import add_alert_suricata, delete_alert_suricata, prepare_alert_attribut, read_suricata_log
from backend.ids_ips.models import Alert, suricatafile
from backend.ids_ips.serializers import AlertSerializer
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-id', '--id', type=str, help='Defineid suricata file')
    def handle(self, *args, **kwargs):
         # Your code to add data to the database here
        try:
            id=kwargs['id']
            logs = read_suricata_log()
            if logs is not None:
                alert_list=[l['alert'] for l in AlertSerializer( Alert.objects.all(), many=True).data]
                logs_add = [log for log in logs if log not in alert_list]
                logs_add=prepare_alert_attribut(logs_add)
                logs_delete = [log for log in alert_list if log not in logs]   
                if len(logs_add)!=0:
                    aux_add=add_alert_suricata(logs_add,id)
                    if aux_add is not True:
                        return aux_add
                if len(logs_delete)!=0:
                    aux_del=delete_alert_suricata(logs_delete)
                    if aux_del is False:
                        return "Alert not Found!!"
                return "All alerts updated successfully!!"
            else:
                return "Error in reading file log!!"
        except IntegrityError as e:
            return "Error: " + str(e)