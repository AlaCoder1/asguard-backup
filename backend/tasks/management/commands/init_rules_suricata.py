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
            rules = get_suricata_default_rules()
            added_rule_ids = []  # Pour stocker les IDs des règles ajoutées avec succès
            # Recherche du fichier SuricataFile par ID
            try:
                suricatafile_obj = suricatafile.objects.get(pk=id)
            except suricatafile.DoesNotExist:
                return  "SuricataFile non trouvé"
            # Parcourez les règles récupérées et ajoutez-les à la base de données
            for rule in rules:
                rule = rule.strip()  # Supprimez les espaces inutiles
                if len(rule)!=0:
                    action=None
                    protocol=None
                    # Vérifiez si la règle n'est pas vide
                    if rule.startswith("#") is True:
                        active=False
                        action=rule.split(" ")[0].strip()+rule.split(" ")[1]
                        protocol=rule.split(" ")[2].strip()
                        
                    else:
                        active=True
                        action=rule.split(" ")[0].strip()
                        protocol=rule.split(" ")[1].strip()
                        print({"protocol":protocol})
                
            
                    sid=None
                    if rule.find("sid")!=-1:
                        rule_inter=rule[rule.find("sid:"):]
                        sid=int(rule_inter[rule_inter.find("sid:")+len("sid:"):rule_inter.find(";")])
                    src_ip=None
                    direction=None
                    dest_ip=None
                    if rule[1:].find("->")!=-1:
                        src_ip=rule[rule.find(protocol)+len(protocol):rule.find("->")].strip()
                        direction="->"
                        dest_ip=rule[rule.find("->")+len("->"):rule.find("(msg")].strip()
                    msg=None
                    if rule.find("msg:")!=-1:
                        msg=rule[rule.find('msg:"')+len('msg:"'): rule.find('";')].strip()
                    rev=None
                    if rule.find("rev:")!=-1:
                        rev=rule[rule.find("rev:")+len("rev:"): rule.find(";sid")].strip(";")
                        if rev.isdigit():
                            rev=int(rev)
                        else:
                            rev=None
                    action=action if action!="" else None    
                    protocol=protocol if protocol!="" else None  
                    src_ip=src_ip if src_ip!="" else None    
                    direction=direction if direction!="" else None  
                    dest_ip=dest_ip if dest_ip!="" else None    
                    msg=msg if msg!="" else None  
                    protocol=protocol if protocol!="" else None  
                    data = {
                        "sid":sid,
                        "action":action.strip("#"),
                        "protocol":protocol,
                        "source_ip":src_ip,
                        "direction":direction,
                        "destination_ip":dest_ip,
                        "msg":msg.strip('"'),
                        "rev":rev,
                        "rule": rule,
                        "suricatafile": suricatafile_obj.id,
                        "activate_rule":active,
                         "default_rule":True
                        }
                    if ids_ips_rule.objects.filter(sid=sid).exists():
                        pass
                    else:
                        InboundSerializer = RuleIdsIpsSerializer(data=data)
                        if InboundSerializer.is_valid():
                            InboundSerializer.save()
                            added_rule_ids.append(data)
                            print(data)# Ajoutez l'ID de la règle ajoutée à la liste
                        else:
                            # message = InboundSerializer.errors
                            pass
            return "Les règles par défaut ont été ajoutées."
        except IntegrityError as e:
            return "Error: " + str(e)