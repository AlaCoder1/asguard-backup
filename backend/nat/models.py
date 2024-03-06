from django.db import models

from backend.network.models import Interface


class SNat(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None)
    tcp_ip = models.CharField(max_length=100, default=None, null=True, blank=True)
    protocol = models.CharField(max_length=100, default=None, null=True, blank=True)
    source_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    source_port = models.CharField(max_length=20, default=None, null=True, blank=True)
    destination_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    destination_port = models.CharField(max_length=20, default=None, null=True, blank=True)
    snat_type = models.CharField(max_length=10, default=None)
    translation_address_from = models.CharField(max_length=100, default=None, null=True, blank=True)
    translation_address_to = models.CharField(max_length=100, default=None, null=True, blank=True)
    translation_port = models.CharField(max_length=20, default=None, null=True, blank=True)
    description = models.CharField(max_length=1000, default=None, null=True, blank=True)
    rule_number = models.IntegerField(default=None, null=True)
    rule_status = models.BooleanField(default=True, null=True)

    class Meta:
        db_table = 'nat_snat'


class OneToOneNat(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None)
    source_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    translation_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    destination_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    description = models.CharField(max_length=1000, default=None, null=True, blank=True)
    rule_number = models.IntegerField(default=None, null=True)
    rule_status = models.BooleanField(default=True, null=True)

    class Meta:
        db_table = 'nat_one_to_one'


class DNat(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None)
    tcp_ip = models.CharField(max_length=100, default=None, null=True, blank=True)
    protocol = models.CharField(max_length=100, default=None, null=True, blank=True)
    source_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    source_port_from = models.CharField(max_length=20, default=None, null=True, blank=True)
    source_port_to = models.CharField(max_length=20, default=None, null=True, blank=True)
    external_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    internal_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    destination_port_from = models.CharField(max_length=20, default=None, null=True, blank=True)
    destination_port_to = models.CharField(max_length=20, default=None, null=True, blank=True)
    destination_port = models.CharField(max_length=20, default=None, null=True, blank=True)
    description = models.CharField(max_length=1000, default=None, null=True, blank=True)
    rule_number = models.IntegerField(default=None, null=True)
    rule_status = models.BooleanField(default=True, null=True)

    class Meta:
        db_table = 'nat_dnat'
