from django.db import models
from backend.network.models import Interface

class Vlan(models.Model):
    parent_interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    vlan_tag = models.IntegerField(unique=True)
    vlan_priority=models.CharField(max_length=200, null=True)
    description=models.CharField(max_length=200, null=True,blank=True)
    class Meta:
            db_table = 'vlan'
