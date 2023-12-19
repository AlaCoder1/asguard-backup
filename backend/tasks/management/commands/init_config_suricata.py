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
    def handle(self, *args, **kwargs):
        try:
            file = read_config()
            if file:
                home_net = file.get("HOME_NET")
                promisc = file.get("promisc")
                if promisc is not None:
                    promisc = promisc.lower() == "true"
                else:
                    promisc = False
                syslog= file.get("syslog-enabled")
                eve_log= file.get("eve-log-enabled")
                mpm_algo = file.get("mpm-algo")
                profile = file.get("profile")
                copy_mode = file.get("copy-mode")
                status_command = "systemctl is-enabled suricata.service"
                output, error = execute_cmd(status_command)
                if output == 'enabled':
                    status_enabled = True
                else:
                    status_enabled = False
                if not suricatafile.objects.filter(home_net=home_net).exists() and suricatafile.objects.all().count()==0:
                    # Créer une instance du modèle suricatafile
                    suricata_config = suricatafile(home_net=home_net, promisc=promisc, eve_log=eve_log, syslog=syslog, mpm_algo=mpm_algo, profile=profile,copy_mode=copy_mode,status_enabled=status_enabled)
                    suricata_config.save()
                    id_conf=suricata_config.id
                    if id_conf is not None:
                        output,error=execute_cmd("python manage.py init_rules_suricata -id {}".format(id_conf))
                        if error=="":
                            output,error=execute_cmd("python manage.py init_alerts_suricata -id {}".format(id_conf))
                            return "Configuration sauvegardé avec succès!!"
                        else:
                            return error
                    else:
                        return "Erreur dans le sauvegarde de configuration!!"
                else:
                    return "suricata config déjà exist!"
        except IntegrityError as e:
            return "Error: " + str(e)    