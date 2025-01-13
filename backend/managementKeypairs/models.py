from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class PrivateKey(models.Model):
    name = models.CharField(max_length=300, unique=True, default=None, blank=True, null=True, verbose_name=_("name"))
    encryption_algorithm = models.CharField(max_length=1000, default=None, blank=True, null=True)
    key_size = models.CharField(max_length=10, default=None, blank=True, null=True)

    class Meta:
        db_table = 'private_key'


class PublicKey(models.Model):
    private_key = models.ForeignKey(PrivateKey, on_delete=models.PROTECT, default=None, blank=True, null=True)
    name = models.CharField(max_length=300, unique=True, default=None, blank=True, null=True, verbose_name=_("name"))
    encryption_algorithm = models.CharField(max_length=1000, default=None, blank=True, null=True)
    key_size = models.CharField(max_length=10, default=None, blank=True, null=True)
    finger_print = models.CharField(max_length=1000, default=None, blank=True, null=True)

    class Meta:
        db_table = 'public_key'
