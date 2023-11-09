from django.db import models

# Create your models here.

class PrivateKey(models.Model):
    name = models.CharField(max_length=300, unique=True, default=None, blank=True, null=True)
    private_key_path = models.CharField(max_length=1000, default=None, blank=True, null=True)
    encryption_algorithm = models.CharField(max_length=1000, default=None, blank=True, null=True)
    key_size = models.CharField(max_length=10, default=None, blank=True, null=True)
    finger_print = models.CharField(max_length=1000, default=None, blank=True, null=True)


class PublicKey(models.Model):
    private_key = models.ForeignKey(PrivateKey, on_delete=models.PROTECT, default=True, blank=True, null=True)
    name = models.CharField(max_length=300, unique=True, default=None, blank=True, null=True)
    public_key_path = models.CharField(max_length=1000, default=None, blank=True, null=True)
    encryption_algorithm = models.CharField(max_length=1000, default=None, blank=True, null=True)
    key_size = models.CharField(max_length=10, default=None, blank=True, null=True)
    finger_print = models.CharField(max_length=1000, default=None, blank=True, null=True)
