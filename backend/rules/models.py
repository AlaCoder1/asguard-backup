from django.db import models
from backend.network.models import Interface
from django.utils.translation import gettext_lazy as _

###Model inbound rule
class Rule(models.Model):
    rule = models.CharField(max_length=10000, null=True, unique=False)
    rule_status = models.BooleanField(default=False)
    type_rule=models.CharField(max_length=200, null=True)
    policy=models.CharField(max_length=200, null=True)
    rule_description=models.CharField(max_length=200, null=True, unique=True, verbose_name=_("rule description"))
    protocol=models.CharField(max_length=200, null=True)
    saddr=models.CharField(max_length=200, null=True)
    sport= models.IntegerField(null=True)
    daddr=models.CharField(max_length=200, null=True)
    dport=models.IntegerField(null=True)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, null=True)
    class Meta:
        db_table = 'rule'
    def __str__(self):
        return self.rule
    
   
class FirewallLog(models.Model):
    log = models.CharField(max_length=10000, null=True, unique=True)
    timestamp=models.CharField(max_length=200, null=True, unique=False)
    rule=models.CharField(max_length=10000, null=True, unique=False)
    interfaces=models.CharField(max_length=200, null=True, unique=False)
    out_mac=models.CharField(max_length=200, null=True, unique=False)
    src_ip=models.CharField(max_length=200, null=True, unique=False)
    dst_ip=models.CharField(max_length=200, null=True, unique=False)
    len_trame=models.CharField(max_length=200, null=True, unique=False)
    TOS=models.CharField(max_length=200, null=True, unique=False)
    PREC=models.CharField(max_length=200, null=True, unique=False)
    TTL=models.CharField(max_length=200, null=True, unique=False)
    ID=models.CharField(max_length=200, null=True, unique=False)
    DF=models.CharField(max_length=200, null=True, unique=False)
    protocole=models.CharField(max_length=200, null=True, unique=False)
    src_port=models.CharField(max_length=200, null=True, unique=False)
    dst_port=models.CharField(max_length=200, null=True, unique=False)
    window_size=models.CharField(max_length=200, null=True, unique=False)
    RES=models.CharField(max_length=200, null=True, unique=False)
    ACK=models.CharField(max_length=200, null=True, unique=False)
    URGP=models.CharField(max_length=200, null=True, unique=False)

    class Meta:
        db_table = 'firewall_log'
   
    
