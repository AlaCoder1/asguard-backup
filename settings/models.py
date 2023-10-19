from django.db import models

# Create your models here.
class System(models.Model):
    hostname = models.CharField(max_length=200, null=True)
    domaine = models.CharField(max_length=200, null=True)
    time_zone = models.DateTimeField( null=True)
    
    class Meta:
        db_table = 'System'
        
class Network(models.Model):
    prever_ipv4_ipv6 = models.BooleanField(default=False, null=True)
    # server_DNS = models.JSONField(null=True)
    server_dns =  models.CharField(max_length=800, null=True)
    gateway =  models.CharField(max_length=800, null=True)
    allow_server_dns = models.BooleanField(default=False, null=True)
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
        db_table = 'server_reseau'
        
        
class Timezone(models.Model):
    name = models.CharField(max_length=800, null=True,unique=True)

    class Meta:
        db_table = 'Timezone'
        
# class GateWayInterface(models.Model):
#     gateway = models.CharField(max_length=800, null=True)
#     interface = models.CharField(max_length=800, null=True)

#     class Meta:
#         db_table = 'gateway_Interface'
