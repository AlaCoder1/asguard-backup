from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.network.models import Interface
from backend.managementCertificates.models import Certificate


class Timezone(models.Model):
    name = models.CharField(max_length=800, null=True, unique=True, verbose_name=_("name"))

    class Meta:
        db_table = 'timezone'
        
class System(models.Model):
    hostname = models.CharField(max_length=200, null=True)
    domaine = models.CharField(max_length=200, null=True)
    time_zone =  models.ForeignKey(
        Timezone, on_delete=models.CASCADE, null=True)
    language = models.CharField(max_length=100, default='en', null=True, blank=True)
    
    class Meta:
        db_table = 'system'
        
class Network(models.Model):
    prever_ipv4_ipv6 = models.BooleanField(default=False, null=True)
    server_dns = models.JSONField(null=True)
    # server_dns =  models.CharField(max_length=800, null=True)
    # gateway =  models.CharField(max_length=800, null=True)
    allow_server_dns = models.BooleanField(default=False, null=True)
    exclude_interfaces = models.CharField(max_length=800, null=True)
    getway_failover = models.BooleanField(default=False, null=True)
    class Meta:
        db_table = 'network'
        
class ServerReseau(models.Model):
    circular_logs = models.BooleanField(default=False, null=True)
    size_log_files = models.CharField(max_length=800, null=True)
    log_firewall_default_blocks = models.CharField(max_length=800, null=True)
    exclude_interfaces = models.CharField(max_length=800, null=True)
    xxx = models.BooleanField(default=False, null=True)
    class Meta:
        db_table = 'server_reseau'
        
        

class Settings(models.Model):
    enable_ssh = models.BooleanField(default=True)
    root_login = models.BooleanField(default=True)
    auth_method = models.CharField(max_length=800, null=True)
    session_timeout = models.IntegerField(null=True)
    certificat = models.ForeignKey(
        Certificate, on_delete = models.CASCADE, null=True)
    tcp_port = models.IntegerField(null=False)
    login_message = models.BooleanField(default=True)
    password_length = models.IntegerField(default=16)
    
    class Meta:
        db_table="settings"
        
    
class SettingInterface(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    setting = models.ForeignKey(Settings, on_delete=models.CASCADE)
    interface_web = models.BooleanField(default=True)
    class Meta:
        db_table = 'setting_interface'    

    
    
        
