from django.db import models
from backend.network.models import Interface

class Vxlan(models.Model):
    parent_interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    vxlan_interface_name = models.CharField(max_length=200,unique=True,null=False)
    vxlan_id = models.IntegerField(unique=True,null=False)
    vxlan_source_address=models.CharField(max_length=200, null=True,blank=True)
    vxlan_destination_address=models.CharField(max_length=200, null=False)
    vxlan_destination_port=models.CharField(max_length=200, null=False)
    vxlan_connection_uuid=models.CharField(max_length=200, null=False,unique=True)
    
    class Meta:
            db_table = 'vxlan'
