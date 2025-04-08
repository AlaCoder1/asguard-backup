from django.db import models
 
from backend.gateway.models import Gateway
from backend.network.models import Interface
 
 
class Routing(models.Model):
    destination_address = models.CharField(max_length=200, default=None, null=True, blank=True)
    gateway = models.ForeignKey(Gateway, on_delete=models.PROTECT, default=None, null=True, blank=True)
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None, null=True, blank=True)
    description = models.CharField(max_length=1000, default=None, null=True, blank=True)
 
    class Meta:
        unique_together = ('destination_address', 'gateway')
        db_table = 'routing'
