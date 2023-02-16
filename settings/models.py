from django.db import models

# Create your models here.
class System(models.Model):
    hostname = models.CharField(max_length=200, null=True)
    domaine = models.CharField(max_length=200, null=True)
    Time_zone = models.DateTimeField( null=True)
    
    class Meta:
        db_table = 'System'
        
class Network(models.Model):
    prever_IPV4_IPV6 = models.BooleanField(default=False, null=True)
    server_DNS = models.JSONField(null=True)
    allow_server_DNS = models.BooleanField(default=False, null=True)
    exclude_interfaces = models.CharField(max_length=800, null=True)
    getway_failover = models.BooleanField(default=False, null=True)
    class Meta:
        db_table = 'Network'
        
class ServerReseau(models.Model):
    circular_logs = models.BooleanField(default=False, null=True)
    size_log_files = models.CharField(max_length=800,null=True)
    log_firewall_default_blocks = models.CharField(max_length=800, null=True)
    exclude_interfaces = models.CharField(max_length=800, null=True)
    xxx = models.BooleanField(default=False, null=True)
    class Meta:
        db_table = 'ServerReseau'
        