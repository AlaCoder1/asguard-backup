from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=200, unique=True)
    members = models.CharField(max_length=1000, default=None, blank=True)

    class Meta:
        db_table = 'area'


class SdwanRules(models.Model):
    name = models.CharField(max_length=200, unique=True)
    source_address = models.CharField(max_length=250, default=None, blank=True, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, default=None)
    algorythme_type = models.CharField(max_length=100, default=None, blank=True)
    destination_address = models.CharField(max_length=200, default=None, blank=True, null=True)
    health_check = models.FloatField(default=5)
    health_check_target = models.CharField(max_length=200, default=None, blank=True)
    primary_interface = models.CharField(max_length=200, default=None, blank=True, null=True)
    table_id = models.IntegerField(default=1, unique=True)
    rule_status = models.BooleanField(default=False)

    class Meta:
        db_table = 'sdwan_rules'
