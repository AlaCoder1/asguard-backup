from backend.ids_ips.serializers import SuricataInterfaceSerializer
from backend.network.models import *
from.models import *
from django.db.models import Q
# Fonction pour obtenir les adresses IP en fonction des interfaces
def get_ip_addresses(interface_ids):
    list_ipaddress = []
    try:
        # Récupérez les adresses IP de la base de données pour les interfaces spécifiées
        ip_configs = IP4Config.objects.filter(interface_id__in=interface_ids).values('ip_address', 'netmask')
    except IP4Config.DoesNotExist:
        return 'Interfaces non trouvées'  # Gestion de l'exception si les interfaces ne sont pas trouvées
    for config  in ip_configs:
        ip_address = config['ip_address']
        prefix_length = config['netmask']
        if prefix_length == 16:
            list_ipaddress.append(ip_address.split('.')[0] + "." + ip_address.split('.')[1] + ".0.0/16")
        elif prefix_length == 24:
            list_ipaddress.append(ip_address.split('.')[0] + "." + ip_address.split('.')[1] + "." + ip_address.split('.')[2] + ".0/24")
        elif prefix_length == 8:
            list_ipaddress.append(ip_address.split('.')[0] + ".0.0.0/8")
    return list_ipaddress



# Fonction pour obtenir le champ HOME_NET à partir de la base de données
def get_home_net_de_la_base_de_donnees(id):
    try:
        # Récupérez l'instance Suricata à partir de la base de données en fonction de l'ID
        suricata_instance = suricatafile.objects.get(id=id)
        return suricata_instance.home_net, suricata_instance.interface_ids
    except suricatafile.DoesNotExist:
        return None  # Gestion de l'exception si l'instance Suricata n'est pas trouvée
    
def delete_suricata_interface(list_id_db,list_id_in):
    """function to delete suricata interfaces"""
    for id in list_id_db:
        if id not in list_id_in:
            interfaces=SuricataInterface.objects.get(interface_id=id)
            interfaces.delete()
            
def save_suricata_interface(id_suricata,list_config_input):
    """function to save informations in suricata Interface"""
    list_id_db=list(SuricataInterface.objects.values_list('interface', flat=True))
    list_id_in=[]
    for config_input in list_config_input:
        id_interface=config_input['id']
        data_updated=config_input
        data_updated["copy_iface"]=config_input["copy_iface"]['id'] if config_input["copy_iface"] is not None else None
        data_updated['interface']=id_interface
        data_updated['suricata']=id_suricata
        list_id_in.append(config_input['id'])
        if SuricataInterface.objects.filter(Q(interface_id=id_interface)&Q(suricata_id=id_suricata)).exists():
            suricata_interface_instance=SuricataInterface.objects.get(Q(interface_id=id_interface)&Q(suricata_id=id_suricata))
            suricata_interface_serializer=SuricataInterfaceSerializer(suricata_interface_instance,data=data_updated)
        else:
            suricata_interface_serializer=SuricataInterfaceSerializer(data=data_updated)
        if suricata_interface_serializer.is_valid():
            suricata_interface_serializer.save()
        else:
            return suricata_interface_serializer.errors
    delete_suricata_interface(list_id_db,list_id_in)
    return True