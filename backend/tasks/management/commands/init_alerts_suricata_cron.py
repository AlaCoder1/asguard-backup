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
        
            id=kwargs['id']
            logs = read_suricata_log()
            alerts = Alert.objects.all()  # Récupérer toutes les alertes de la base de données
            alert_list=[]
            if alerts:
                serializer = AlertSerializer(alerts, many=True)
                alert_list=serializer.data
                alert_list=[l['alert'] for l in alert_list]
            logs_all=[l['alert'] for l in logs]    
            difference=list(set(logs_all)-set(alert_list))
            # print(difference)
            max_size=10000
            if len(difference)!=0:
                added_logs = []  # Pour stocker les logs ajoutés avec succès en base de données
                # Parcourir les logs récupérés et ajoutez-les à la base de données
                for log in difference:
                    suricatafile_obj = suricatafile.objects.get(pk=id)  
                    if not Alert.objects.filter(alert=log).exists():
                        attributes = log.split()
                        if len(attributes)!=0:
                            timestamp = attributes[0] + ' ' + attributes[1].replace("[**]", "",2)
                            priority=attributes[-5][:1]
                            protocol = attributes[-4][1:-1]
                            src_addr=attributes[-3].split(":")[0]
                            src_port=attributes[-3].split(":")[1]
                            dst_addr=attributes[-1].split(":")[0]
                            dst_port=attributes[-1].split(":")[1]
                            sid=attributes[2].split(":")[1]
                            # Afficher les attributs
                            data={"timestamp": timestamp,
                                "sid":sid,
                                "priority": int(priority),
                                "protocol": protocol,
                                "src_addr": src_addr,
                                "src_port": int(src_port),
                                "dst_addr": dst_addr,
                                "dst_port": int(dst_port),
                                "alert":log.strip(),}    
                            data['suricatafile']=int(suricatafile_obj.id)
                            print({"log to add":log})
                            serializerAlert = AlertSerializer(data=data)
                            if serializerAlert.is_valid():
                                serializerAlert.save()
                                added_logs.append(serializerAlert.data)
                            else:
                                return str(serializerAlert.errors)
                    else:
                        pass
            nb_lines=len(logs)
            if nb_lines>max_size:
                nb_iter=nb_lines//max_size
                print({"nblines initiales":nb_lines})
                print(nb_iter)
                if len(logs)%max_size!=0:
                    nb_line_delete=nb_iter*max_size
                list_logs = [l['alert'] for l in logs[:nb_line_delete]]
                date_systeme = datetime.now().date()
                print("logs to delete==>",nb_line_delete)
                print("logs reste",nb_lines-nb_line_delete)
                
                for l in list_logs:
                    commandes=[
                "mkdir -p /var/log/suricata/backup_logs",
                '[ -e "/var/log/suricata/backup_logs/{}" ] || touch "/var/log/suricata/backup_logs/logs_{}"'.format(date_systeme,date_systeme),
    # 'sudo grep -qF "{} {}" /var/log/suricata/backup_logs/logs_{} || sudo bash -c \'cat <<EOF >> /var/log/suricata/backup_logs/logs_{}  {}\\nEOF\''.format(date_systeme, l, date_systeme, date_systeme, l)

             """sudo cat <<EOF >> /var/log/suricata/backup_logs/logs_{}
{}
EOF""".format(date_systeme, l)
                ]   
                    print("this alert ================>",l)
                    for cmd in commandes:
                        output, error = execute_cmd(cmd)
                        if error!="":
                            return error
                    
                    # cmd="sed -i '/{}/' /var/log/suricata/fastcopi.log".format(l)
                    cmd = "sed -i '#{}/#' /var/log/suricata/fastcopie.log ".format(l)
                    output, error = execute_cmd(cmd)
                    if error=="":
                        if Alert.objects.filter(alert=l).exists():
                            alert = Alert.objects.get(alert=l)
                            alert.delete()
                            print("this alert deleted from system/database==>",l)
                        else:
                            return "Alert not found!!===>"+l
                    else :
                        return "hellooooo===>"+error+cmd
                return "All alerts saved in backup successfully!!"
            else:
                return "Pas de backup nombre de lignes est limités"
        
        