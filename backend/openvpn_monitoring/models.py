from django.db import models
from django.utils import timezone
# Create your models here.
class  VpnMonitoring(models.Model):
    address_server = models.CharField(max_length=200, null=True,unique=True)
    client_active= models.IntegerField(null=True,unique=False)
    capacity_server_in= models.IntegerField(null=True,unique=False)
    capacity_client_out =  models.IntegerField(null=True,unique=False)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    
    class Meta:
        db_table = 'vpnmonitoring'
    
class  VpnMonitoringClient(models.Model):
    username = models.CharField(max_length=200, null=True,unique=False)
    login_time= models.CharField(max_length=200, null=True,unique=False)
    address= models.CharField(max_length=200, null=True,unique=False)
    bytes_recv =   models.IntegerField(null=True,unique=False)
    bytes_sent =   models.IntegerField(null=True,unique=False)
    total_traffic= models.IntegerField(null=True,unique=False)
    location = models.CharField(max_length=200, null=True,unique=False)
    traffic_distr= models.FloatField(null=True,unique=False)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)

    vpnmonitor = models.ForeignKey(
            VpnMonitoring, on_delete=models.CASCADE)
    class Meta:
        db_table = 'vpnmonitoring_clients'