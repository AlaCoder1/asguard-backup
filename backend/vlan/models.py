from django.db import models
from backend.network.models import Interface
from django.utils.translation import gettext_lazy as _
class Vlan(models.Model):
    parent_interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    vlan_tag = models.IntegerField(unique=True,verbose_name=_("tag"))
    vlan_priority=models.CharField(max_length=200, null=True,verbose_name=_("priority"))
    description=models.CharField(max_length=200, null=True,blank=True,verbose_name=_("description"))
    class Meta:
            db_table = 'vlan'
