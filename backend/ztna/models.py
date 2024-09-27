from django.db import models
from datetime import datetime

# Create your models here.

class Identities(models.Model):
    ref_identitie = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    attribute_identitie = models.CharField(max_length=500, null=True, blank=True)
    type = models.CharField(max_length=200)
    description = models.CharField(max_length=800,null=True)
    is_admin = models.BooleanField(default=False)
    date_creation = models.DateTimeField()
    date_expiration = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=1000, unique=True, null=True, blank=True)
    class Meta:
        db_table = 'identities'
    def __str__(self):
        return self.ref_identitie
    
class Enrollements(models.Model):
    date = models.DateField()
    time = models.TimeField()
    type = models.CharField(max_length=100)
    identitie = models.ForeignKey(Identities, on_delete=models.CASCADE)
    class Meta:
        db_table = 'enrollements'

class InterceptConfigs(models.Model):
    ref_intercept=models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    protocol = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    low = models.IntegerField()
    high = models.IntegerField()
    date_creation = models.DateTimeField()
    description = models.CharField(max_length=800,null=True)
    class Meta:
        db_table = 'interceptconfigs'
    def __str__(self):
        return self.ref_intercept
    
class HostConfigs(models.Model):
    ref_host=models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    protocol = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    port = models.IntegerField()
    date_creation = models.DateTimeField()
    description = models.CharField(max_length=800,null=True)
    class Meta:
        db_table = 'hostconfigs'
    def __str__(self):
        return self.ref_host
    
class Services(models.Model):
    ref_service = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    attribute_service = models.CharField(max_length=500, null=True, blank=True)
    description = models.CharField(max_length=800,null=True)
    encryption = models.BooleanField(default=False)
    intercept = models.ForeignKey(InterceptConfigs, on_delete=models.CASCADE)
    host = models.ForeignKey(HostConfigs, on_delete=models.CASCADE)
    date_creation = models.DateTimeField()
    class Meta:
        db_table = 'servicesztna'

class Relays(models.Model):
    ref_relay=models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    attribute_relay = models.CharField(max_length=500, null=True, blank=True)
    tunneler = models.BooleanField(default=False)
    traversal = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    date_creation = models.DateTimeField()
    description = models.CharField(max_length=800,null=True)
    class Meta:
        db_table = 'relays'
    def __str__(self):
        return self.ref_relay
    
class RelaysPolicy(models.Model):
    ref_relay_policy = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    semantique = models.CharField(max_length=10, blank=False)
    description = models.CharField(max_length=800,null=True)
    relay = models.ForeignKey(Relays, on_delete=models.CASCADE)
    identity = models.ForeignKey(Identities, on_delete=models.CASCADE)
    identity_attribute=models.CharField(max_length=500, null=True, blank=True)
    relay_attribute=models.CharField(max_length=500, null=True, blank=True)

    date_creation = models.DateTimeField()
    class Meta:
        db_table = 'relaypolicy'

class ServicesPolicy(models.Model):
    ref_service_policy = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    semantique = models.CharField(max_length=10, blank=False)
    type = models.CharField(max_length=10, blank=False)
    description = models.CharField(max_length=800,null=True)
    service_attribute = models.CharField(max_length=10, blank=False)
    identity_attribute = models.CharField(max_length=10, blank=False)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    identity = models.ForeignKey(Identities, on_delete=models.CASCADE)
    date_creation = models.DateTimeField()
    class Meta:
        db_table = 'servicepolicies'

class ServicesRelaysPolicy(models.Model):
    ref_service_relay_policy = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=500, unique=True)
    semantique = models.CharField(max_length=10, blank=False)
    description = models.CharField(max_length=800,null=True)
    service_attribute = models.CharField(max_length=10, blank=False)
    relay_attribute = models.CharField(max_length=10, blank=False)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    relay = models.ForeignKey(Relays, on_delete=models.CASCADE)
    date_creation = models.DateTimeField()
    class Meta:
        db_table = 'servicerelaypolicies'