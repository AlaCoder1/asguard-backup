from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.network.models import Interface


class SNat(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None, null=True)
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
    postrouting_position = models.IntegerField(default=None, null=True, unique=True) # Rule in system in chain postrouting
    db_position = models.IntegerField(default=None, null=True, unique=True) # Rule in database in snat table
    rule_number = models.IntegerField(default=None, null=True)
    rule_status = models.BooleanField(default=True, null=True)
    rule_content = models.CharField(max_length=1000, default=None, null=True, blank=True, unique=True, verbose_name=_("Content"))

    class Meta:
        db_table = 'nat_snat'


class OneToOneNat(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None, null=True)
    source_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    translation_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    destination_address = models.CharField(max_length=100, default=None, null=True, blank=True)
    description = models.CharField(max_length=1000, default=None, null=True, blank=True)
    postrouting_position = models.IntegerField(default=None, null=True, unique=True) # Rule in system in chain postrouting
    db_position = models.IntegerField(default=None, null=True, unique=True) # Rule in database in One To One Nat table
    rule_number = models.IntegerField(default=None, null=True)
    rule_status = models.BooleanField(default=True, null=True)
    rule_content = models.CharField(max_length=1000, default=None, null=True, blank=True, unique=True, verbose_name=_("Content"))

    class Meta:
        db_table = 'nat_one_to_one'


class DNat(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.PROTECT, default=None, null=True)
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
    prerouting_position = models.IntegerField(default=None, null=True, unique=True) # Rule in system in chain prerouting
    db_position = models.IntegerField(default=None, null=True, unique=True) # Rule in database in dNat table
    rule_number = models.IntegerField(default=None, null=True)
    rule_status = models.BooleanField(default=True, null=True)
    rule_content = models.CharField(max_length=1000, default=None, null=True, blank=True, unique=True, verbose_name=_("Content"))

    class Meta:
        db_table = 'nat_dnat'
