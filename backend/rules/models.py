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
   
    
