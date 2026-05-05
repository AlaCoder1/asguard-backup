from django.db import models
from backend.network.models import Interface
from django.utils.translation import gettext_lazy as _


class Vlan(models.Model):
    VLAN_PRIORITY_CHOICES = [
        ("Best Effort ( 0 , default )", "Best Effort ( 0 , default )"),
        ("Background ( 1, lowest)", "Background ( 1, lowest)"),
        ("Excellent Effort (2)", "Excellent Effort (2)"),
        ("Critical Applications (3)", "Critical Applications (3)"),
        ("Video (4)", "Video (4)"),
        ("Voice (5)", "Voice (5)"),
        ("Internetwork Control (6)", "Internetwork Control (6)"),
        ("Network Control (7)", "Network Control (7)"),
    ]
    parent_interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    vlan_tag = models.IntegerField(unique=True, verbose_name=_("tag"))
    vlan_priority=models.CharField(max_length=200, 
                                   choices=VLAN_PRIORITY_CHOICES, 
                                   null=True, 
                                   verbose_name=_("priority"))
    description=models.CharField(max_length=200, null=True, blank=True, verbose_name=_("description"))
    class Meta:
            db_table = 'vlan'
