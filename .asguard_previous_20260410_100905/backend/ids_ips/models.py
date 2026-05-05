from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.network.models import Interface


#SuricataConfig
class suricatafile(models.Model):
    home_net = models.CharField(max_length=100, null=True, unique=True, verbose_name=_("service name"))
    promisc = models.BooleanField(default=True) 
    syslog=models.CharField(max_length=100, null=True)
    eve_log=models.CharField(max_length=100, null=True)
    mpm_algo =models.CharField(max_length=100, null=True)
    profile = models.CharField(max_length=100, null=True, default="medium")
    mode_inline = models.CharField(max_length=100, null=True)
    status_enabled=models.BooleanField(default=False)
    
    class Meta:
        db_table = 'suricataconfig'  

###config interface
class SuricataInterface(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    suricata = models.ForeignKey(suricatafile, on_delete=models.CASCADE)
    threads=models.CharField(max_length=100, blank=True, null=True)
    cluster_id=models.IntegerField(null=True, default=0, unique=True)
    cluster_type=models.CharField(max_length=100, blank=True)
    defrag=models.CharField(max_length=100, blank=True)
    use_mmap=models.CharField(max_length=100, blank=True)
    ring_size=models.IntegerField(null=True, default=0)
    copy_mode= models.CharField(max_length=100, null=True)
    copy_iface=models.IntegerField(null=True, default=0)
    class Meta:
        db_table = 'suricata_interface'    

#Rule
class ids_ips_rule(models.Model):
    sid = models.IntegerField(null=True, unique=True)
    action=models.CharField(max_length=200, null=True)
    protocol=models.TextField(null=True, blank=True)
    source_ip=models.TextField(null=True, blank=True)
    direction=models.TextField(null=True, blank=True)
    destination_ip=models.TextField(null=True, blank=True)
    msg=models.TextField(null=True, blank=True)
    rev= models.IntegerField(null=True, blank=True)
    rule=models.TextField(max_length=100000, null=True, blank=True)
    activate_rule=models.BooleanField(default=True)  
    default_rule=models.BooleanField(default=True)  
    suricatafile = models.ForeignKey(
               suricatafile, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'ids_ips_rules' 
#Alert
class Alert(models.Model):
    timestamp=models.CharField(max_length=200, null=True)
    sid = models.IntegerField(null=True)
    priority=models.IntegerField(null=True)
    protocol=models.TextField(null=True)
    src_addr=models.TextField(null=True)
    src_port=models.IntegerField(null=True)
    dst_addr=models.TextField(null=True)
    dst_port=models.IntegerField(null=True)
    message=models.TextField(null=True)
    alert=models.TextField(unique=True, null=True)
    suricatafile = models.ForeignKey(
               suricatafile, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'alerts'   
        
    

class SuricataLogs(models.Model):
    log=models.TextField()

    class Meta:
        db_table = 'suricata_logs'    
class StatsLogs(models.Model):
    log=models.TextField()

    class Meta:
        db_table = 'stats_logs'    