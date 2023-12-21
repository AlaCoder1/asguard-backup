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
            cmd="sudo suricata-update"
            output,error=execute_cmd(cmd)
            if error.strip()=="":
                rules_DB = ids_ips_rule.objects.all()  # Récupérer toutes les alertes de la base de données
                rules_sys = get_suricata_default_rules()
                rules_add=[]
                rules_delete=[]
                rules_list=[]
                serializer = RuleIdsIpsSerializer(rules_DB, many=True)
                rules_list=serializer.data
                rules_list=[l['sid'] for l in rules_list]
                rules_sys_list=[l['sid'] for l in prepare_rule_attribut(rules_sys)]
                if len(list(set(rules_list)-set(rules_sys_list)))!=0:
                    rules_add = [log for log in rules_sys if log not in rules_list]
                    rules_delete = [log for log in rules_list if log not in rules_sys]   
                    if len(rules_add)!=0:
                        rules_add=prepare_rule_attribut(rules_add)
                        # Parcourir les logs récupérés et ajoutez-les à la base de données
                        for rule in rules_add:
                            print("data to add ==>",rule['sid'])
                            rule['suricatafile']=int(id)
                            if not ids_ips_rule.objects.filter(sid=rule['sid']).exists():
                                serializerAlert = RuleIdsIpsSerializer(data=rule)
                                if serializerAlert.is_valid():
                                    serializerAlert.save()
                                else:
                                    return str(serializerAlert.errors)
                            else:
                                pass
                    if len(rules_delete)!=0:
                        rules_delete=prepare_rule_attribut(rules_delete)
                        for l in rules_delete:
                            print("data to delete ==>",l['sid'])
                            if ids_ips_rule.objects.filter(sid=l['sid']).exists():
                                rule = ids_ips_rule.objects.get(sid=l['sid'])
                                rule.delete()
                            else:
                                return "Rule not found!"
                    return "Rules updated successfully!"
                else:
                    return "No data to add !!"
            else:
                return error
        except IntegrityError as e:
            return "Error: " + str(e)