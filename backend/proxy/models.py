from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ServerSatus(models.Model):
    status_server = models.BooleanField(default=False)

    class Meta:
        db_table = 'squid_conf'
        
class ProxyRules(models.Model):
    rule_name = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length=20, null = False)
    value = models.CharField(max_length=200, null=True, unique=True)
    status = models.BooleanField(default=False)
    days = models.CharField(max_length=200, null=True)
    time_from = models.TimeField(null=True) 
    time_to = models.TimeField(null=True)
    allow_by_auth = models.BooleanField(default=False)
    squid_conf = models.ForeignKey(
        ServerSatus, on_delete=models.CASCADE, null=True,default = 1)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(ProxyRules, self).save(*args, **kwargs)
    class Meta:
        db_table = 'proxy_rules'


class ProxyUser(models.Model):
    username = models.CharField(max_length=200, null=True, unique=True, verbose_name=_("username"))
    email = models.CharField(max_length=200, null=True, unique=True)
    squid_conf = models.ForeignKey(
        ServerSatus, on_delete=models.CASCADE, null=True,default = 1)
    
    class Meta:
        db_table = 'proxy_user'  
        
        
class CacheLogs(models.Model):
    log=models.TextField()

    class Meta:
        db_table = 'cache_logs'    
class AccessLogs(models.Model):
    log=models.TextField()

    class Meta:
        db_table = 'access_logs'    
        
class StoreLogs(models.Model):
    log=models.TextField()

    class Meta:
        db_table = 'store_logs'    