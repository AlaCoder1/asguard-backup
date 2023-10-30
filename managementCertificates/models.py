from django.db import models

# Create your models here.

class CertificateAuthority(models.Model):
    """Model of activated authority certificates"""
    name = models.CharField(max_length=300, unique=True, default=None, blank=True, null=True)
    certificate_path = models.CharField(max_length=1000, default=None, blank=True, null=True)
    valid_from = models.DateTimeField(default=None, blank=True, null=True)
    valid_until = models.DateTimeField(default=None, blank=True, null=True)
    key_type = models.CharField(max_length=100, default='RSA', blank=True, null=True)
    key_length = models.IntegerField(default=2048, blank=True, null=True)
    digest_algorithm = models.CharField(max_length=100, default='sha256', blank=True, null=True)
    lifetime = models.IntegerField(default=None, blank=True, null=True)
    country_code = models.CharField(max_length=100, default=None, blank=True, null=True)
    state = models.CharField(max_length=100, default=None, blank=True, null=True)
    city = models.CharField(max_length=100, default=None, blank=True, null=True)
    organization = models.CharField(max_length=100, default=None, blank=True, null=True)
    email = models.CharField(max_length=100, default=None, blank=True, null=True)
    common_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    serial = models.CharField(max_length=100, default=None, blank=True, null=True)

    class Meta:
        db_table = 'certificate_authority'


class Certificate(models.Model):
    """Model of activated certificates or keys"""
    certificate_authority = models.ForeignKey(CertificateAuthority, on_delete=models.PROTECT, default=None, blank=True, null=True)
    name = models.CharField(max_length=300, unique=True, default=None, blank=True, null=True)
    certificate_path = models.CharField(max_length=1000, default=None, blank=True, null=True)
    certificate_type = models.CharField(max_length=1000, default=None, blank=True, null=True)  # can be certificate or key or Diffie-Hellman
    activation = models.BooleanField(default=True)  # Activated or Revoked
    valid_from = models.DateTimeField(default=None, blank=True, null=True)
    valid_until = models.DateTimeField(default=None, blank=True, null=True)
    key_type = models.CharField(max_length=100, default='RSA', blank=True, null=True)
    key_length = models.IntegerField(default=2048, blank=True, null=True)
    digest_algorithm = models.CharField(max_length=100, default='sha256', blank=True, null=True)
    lifetime = models.IntegerField(default=None, blank=True, null=True)
    private_key_location = models.CharField(max_length=100, default="Save on this firewall", blank=True, null=True)
    country_code = models.CharField(max_length=100, default=None, blank=True, null=True)
    state = models.CharField(max_length=100, default=None, blank=True, null=True)
    city = models.CharField(max_length=100, default=None, blank=True, null=True)
    organization = models.CharField(max_length=100, default=None, blank=True, null=True)
    email = models.CharField(max_length=100, default=None, blank=True, null=True)
    common_name = models.CharField(max_length=100, default=None, blank=True, null=True, unique=True)
    serial = models.CharField(max_length=100, default=None, blank=True, null=True)

    class Meta:
        db_table = 'certificate'
