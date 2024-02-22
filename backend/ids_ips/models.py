from django.db import models
from backend.network.models import *

# Create your models here.

#SuricataConfig
class suricatafile(models.Model):
    # Champ pour stocker la valeur de 'home_net'(adresse IP)
    home_net = models.CharField(max_length=100,null=True,unique=True)
    # Champ booléen pour activer/désactiver la mode promiscuité (true ou false / true par défaut)
    promisc = models.BooleanField(default=True) 
    # Champ pour spécifier syslog enable oun non (yes ou no  / yes par défaut )
    syslog=models.CharField(max_length=100,null=True)
    # Champ pour spécifier event-log enable ou non (yes ou no / no par défaut)
    eve_log=models.CharField(max_length=100,null=True)
    #(["auto", "ac", "ac-bs", "ac-ks", "hs" ]/ auto par défaut)
    mpm_algo =models.CharField(max_length=100,null=True)
    #(["medium", "high", "low"] / medium par défaut)
    profile = models.CharField(max_length=100, null=True, default="medium")
    #(["none", "tap", "ips"] / none par défaut)
    # copy_mode = models.CharField(max_length=100, null=True, default="none")
    # Indique si suricata est enable (par défaut, True )
    status_enabled=models.BooleanField(default=False)
    # par exemple [1,2]
    interface_ids=models.CharField(max_length=100,null=True)
    
    class Meta:
        db_table = 'suricataconfig'  # Nom de la table dans la base de données

###config interface
class SuricataInterface(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    suricata = models.ForeignKey(suricatafile, on_delete=models.CASCADE)
    threads=models.CharField(max_length=100,blank=True,null=True)
    cluster_id=models.IntegerField(null=True,default=0,unique=True)
    cluster_type=models.CharField(max_length=100,blank=True)
    defrag=models.CharField(max_length=100,blank=True)
    use_mmap=models.CharField(max_length=100,blank=True)
    ring_size=models.IntegerField(null=True,default=0)
    copy_mode= models.CharField(max_length=100, null=True)
    copy_iface=models.IntegerField(null=True,default=0)
    class Meta:
        db_table = 'suricata_interface'    

#Rule
class ids_ips_rule(models.Model):
    # id = models.AutoField(primary_key=True)
    # Numéro SID de la règle, unique
    sid = models.IntegerField(null=True,unique=True)
    # Action de la règle (par exemple, "alert" ou "drop")
    action=models.CharField(max_length=200,null=True)
    # Protocole de la règle (par exemple, "TCP" ou "UDP")
    protocol=models.TextField(null=True,blank=True)
    # Adresse IP source
    source_ip=models.TextField(null=True,blank=True)
    # Direction de la règle (par exemple, "->" ou "<-")
    direction=models.TextField(null=True,blank=True)
    # Adresse IP de destination
    destination_ip=models.TextField(null=True,blank=True)
    # Message associé à la règle
    msg=models.TextField(null=True,blank=True)
    # Révision de la règle
    rev= models.IntegerField(null=True,blank=True)
    # La règle elle-même (peut être très longue)
    rule=models.TextField(max_length=100000, null=True,blank=True)
    # Indique si la règle est activée (par défaut, True signifie activée (sans (#)))
    activate_rule=models.BooleanField(default=True)  
    # Indique si la règle est activée (par défaut, True signifie activée (sans (#)))
    default_rule=models.BooleanField(default=True)  
    # Clé étrangère pour établir la relation many-to-one avec SuricataFile
    suricatafile = models.ForeignKey(
               suricatafile, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'ids_ips_rules' # Nom de la table dans la base de données

#Alert
class Alert(models.Model):
    # Horodatage de l'alerte
    timestamp=models.CharField(max_length=200, null=True)
     # Numéro SID de la règle, unique
    sid = models.IntegerField(null=True)
    # Priorité de l'alerte
    priority=models.IntegerField(null=True)
    # Protocole de l'alerte (par exemple, "TCP" ou "UDP")
    protocol=models.TextField(null=True)
    # Adresse source de l'alerte
    src_addr=models.TextField(null=True)
    # Port source de l'alerte
    src_port=models.IntegerField(null=True)
    # Adresse de destination de l'alerte
    dst_addr=models.TextField(null=True)
    # Port de destination de l'alerte
    dst_port=models.IntegerField(null=True)
     # Messgae de l'alerte
    message=models.TextField(null=True)
    #alerte in text
    alert=models.TextField(unique=True,null=True)
    # Clé étrangère pour établir la relation many-to-one avec SuricataFile
    suricatafile = models.ForeignKey(
               suricatafile, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'alerts'   # Nom de la table dans la base de données