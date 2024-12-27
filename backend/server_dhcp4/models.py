from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.network.models import Interface

# Create your models here.
class ServerDhcp4(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    enable_dhcpv4 = models.BooleanField(default=False)
    subnet_addr = models.CharField(max_length=200, null=True, unique=True, verbose_name=_("subnet address"))
    subnet_mask = models.CharField(max_length=200, null=True)
    available_range=models.CharField(max_length=200, null=True, unique=True, verbose_name=_("available range"))
    range_from=models.CharField(max_length=200, null=True, unique=True, verbose_name=_("range from"))
    range_to=models.CharField(max_length=200, null=True, unique=True, verbose_name=_("range to"))
    dns_server=models.CharField(max_length=200, null=True)
    gateway=models.CharField(max_length=200, null=True)
    domain_name=models.CharField(max_length=200, null=True)
    class Meta:
            db_table = 'server_dhcp4'
