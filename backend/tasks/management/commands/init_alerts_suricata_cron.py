from django.core.management.base import BaseCommand
from backend.ids_ips.models import *
from backend.network.serializers import *
from backend.network.models import *
from backend.settings.serializers import *
from backend.authentification.views import *
from backend.ids_ips.serializers import *
from backend.ids_ips.function_BD import *
from backend.ids_ips.function_sys import *
from django.db import IntegrityError
from django.core import serializers
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            suricataObject = suricatafile.objects.all() 
            suricataDict = serializers.serialize("json", suricataObject)
            res = json.loads(suricataDict)
            id = res[0]['pk']
            logs = read_suricata_log()
            alerts = Alert.objects.all()  # Récupérer toutes les alertes de la base de données
            logs_add=[]
            logs_delete=[]
            alert_list=[]
            serializer = AlertSerializer(alerts, many=True)
            alert_list=serializer.data
            alert_list=[l['alert'] for l in alert_list]
            logs_add = [log for log in logs if log not in alert_list]
            logs_add=prepare_alert_attribut(logs_add)
            logs_delete = [log for log in alert_list if log not in logs]   
            if len(logs_add)!=0:
                # Parcourir les logs récupérés et ajoutez-les à la base de données
                for log in logs_add:
                    print("data to add ==>",log['alert'])
                    suricatafile_obj = suricatafile.objects.get(pk=id)  
                    log['suricatafile']=int(suricatafile_obj.id)
                    if not Alert.objects.filter(alert=log['alert']).exists():
                        serializerAlert = AlertSerializer(data=log)
                        if serializerAlert.is_valid():
                            serializerAlert.save()
                        else:
                            return str(serializerAlert.errors)
                    else:
                        pass
            if len(logs_delete)!=0:
                for l in logs_delete:
                    print("data to delete ==>",l)
                    if Alert.objects.filter(alert=l).exists():
                        alert = Alert.objects.get(alert=l)
                        alert.delete()
                    else:
                        return "Alert not found!!"
            return "All alerts updated successfully!!"
            
        except IntegrityError as e:
            return "Error: " + str(e)