from django.db import models
from backend.network.models import Interface
from django.utils.translation import gettext_lazy as _


class Vxlan(models.Model):
    parent_interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    vxlan_interface_name = models.CharField(max_length=200, unique=True, null=False, verbose_name=_("interface Name"))
    vxlan_id = models.IntegerField(unique=True, null=False,verbose_name=_("vxlan id"))
    vxlan_source_address=models.CharField(max_length=200, null=True, blank=True, verbose_name=_("source address"))
    vxlan_destination_address=models.CharField(max_length=200, null=False, verbose_name=_("destination address"))
    vxlan_destination_port=models.CharField(max_length=200, null=False, verbose_name=_("port"))
    vxlan_connection_uuid=models.CharField(max_length=200, null=False, unique=True, verbose_name=_("connection name"))
    
    class Meta:
            db_table = 'vxlan'
