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
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-id', '--id', type=str, help='Defineid suricata file')
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            id=kwargs['id']
            logs = read_suricata_log()
            if logs:
                added_logs = []  # Pour stocker les logs ajoutés avec succès en base de données
                # Parcourir les logs récupérés et ajoutez-les à la base de données
                for log in logs:
                    suricatafile_obj = suricatafile.objects.get(pk=id)  
                    log['suricatafile']=int(suricatafile_obj.id)
                    if not Alert.objects.filter(alert=log['alert']).exists():
                        serializerAlert = AlertSerializer(data=log)
                        if serializerAlert.is_valid():
                            serializerAlert.save()
                            added_logs.append(serializerAlert.data)
                        else:
                            return str(serializerAlert.errors)
                    else:
                        pass
                return "Les alerts ont été ajoutées avec succès."
            else:
                return "Aucun log n'a été trouvé pour ajouter."
        except IntegrityError as e:
            return "Error: " + str(e)