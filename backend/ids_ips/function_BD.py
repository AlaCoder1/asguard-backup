from backend.network.models import *
from.models import *

# Fonction pour obtenir les adresses IP en fonction des interfaces
def get_ip_addresses(interface_ids):
    list_ipAddress = []
    try:
        # Récupérez les adresses IP de la base de données pour les interfaces spécifiées
        ip_configs = IP4Config.objects.filter(interface_id__in=interface_ids).values('ip_address', 'netmask')
    except IP4Config.DoesNotExist:
        return 'Interfaces non trouvées'  # Gestion de l'exception si les interfaces ne sont pas trouvées
    for config  in ip_configs:
        ip_address = config['ip_address']
        prefix_length = config['netmask']
        if prefix_length == 16:
            list_ipAddress.append(ip_address.split('.')[0] + "." + ip_address.split('.')[1] + ".0.0/16")
        elif prefix_length == 24:
            list_ipAddress.append(ip_address.split('.')[0] + "." + ip_address.split('.')[1] + "." + ip_address.split('.')[2] + ".0/24")
        elif prefix_length == 8:
            list_ipAddress.append(ip_address.split('.')[0] + ".0.0.0/8")
    print({"list_ipAddress": list_ipAddress})
    return list_ipAddress



# Fonction pour obtenir le champ HOME_NET à partir de la base de données
def get_home_net_de_la_base_de_donnees(id):
    try:
        # Récupérez l'instance Suricata à partir de la base de données en fonction de l'ID
        suricata_instance = suricatafile.objects.get(id=id)
        return suricata_instance.home_net, suricata_instance.interface_ids
    except suricatafile.DoesNotExist:
        return None  # Gestion de l'exception si l'instance Suricata n'est pas trouvée