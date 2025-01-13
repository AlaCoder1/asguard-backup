from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.network.models import Interface


class Area(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name=_("name"))
    members = models.ManyToManyField(Interface, through="AreaInterface")


    class Meta:
        db_table = 'area'


class SdwanRules(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name=_("name"))
    source_address = models.CharField(max_length=250, default=None, blank=True, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, default=None)
    algorythme_type = models.CharField(max_length=100, default=None, blank=True)
    destination_address = models.CharField(max_length=200, default=None, blank=True, null=True)
    health_check = models.FloatField(default=5)
    health_check_target = models.CharField(max_length=200, default=None, blank=True)
    primary_interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None, blank=True, null=True)
    table_id = models.IntegerField(default=1, unique=True)
    rule_status = models.BooleanField(default=False)

    class Meta:
        db_table = 'sdwan_rules'


class AreaInterface(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)

    class Meta:
        db_table = 'area_interface'
