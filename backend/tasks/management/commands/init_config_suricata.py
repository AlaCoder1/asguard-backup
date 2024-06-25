from django.core.management.base import BaseCommand
from backend.ids_ips.models import *
from backend.network.models import *
from backend.ids_ips.serializers import *
from backend.ids_ips.function_BD import *
from backend.ids_ips.function_sys import *
from django.db import IntegrityError
import ruamel.yaml
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            yaml_class = ruamel.yaml.YAML()
            suricata_path="/etc/suricata/suricata.yaml"
            data=read_from_yaml(suricata_path,yaml_class)
            file = read_config(data)
            id_conf=None
            if file:
                home_net = file.get("HOME_NET")
                if not suricatafile.objects.filter(home_net=home_net).exists() and suricatafile.objects.all().count()==0:
                    # Créer une instance du modèle suricatafile
                    suricata_config = SuricataFileSerializer(data=file)
                    if suricata_config.is_valid():
                        suricata_conf=suricata_config.save()
                        id_conf=suricata_conf.id
                    
                    if id_conf is not None:
                        _,error=execute_cmd("python manage.py init_rules_suricata -id {}".format(id_conf))
                        if error=="":
                            _,error=execute_cmd("python manage.py init_alerts_suricata -id {}".format(id_conf))
                            return "Configuration sauvegardé avec succès!!"
                        else:
                            return error
                    else:
                        return "Erreur dans le sauvegarde de configuration!!"
                else:
                    return "suricata config déjà exist!"
        except IntegrityError as e:
            return "Error: " + str(e)    