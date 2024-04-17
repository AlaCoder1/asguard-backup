from django.db import models

# Create your models here.
class  VpnMonitoring(models.Model):
    address_server = models.CharField(max_length=200, null=True,unique=True)
    client_active= models.IntegerField(null=True,unique=True)
    capacity_server_in= models.IntegerField(null=True,unique=True)
    capacity_client_out =  models.IntegerField(null=True,unique=True)
    
    class Meta:
        db_table = 'vpnmonitoring'
    
class  VpnMonitoringClient(models.Model):
    username = models.CharField(max_length=200, null=True,unique=True)
    login_time= models.CharField(max_length=200, null=True,unique=True)
    address= models.CharField(max_length=200, null=True,unique=True)
    bytes_recv =   models.IntegerField(null=True,unique=True)
    bytes_sent =   models.IntegerField(null=True,unique=True)
    total_traffic= models.IntegerField(null=True,unique=True)
    location = models.CharField(max_length=200, null=True,unique=True)
    traffic_distr= models.IntegerField(null=True,unique=True)
    vpnmonitor = models.ForeignKey(
            VpnMonitoring, on_delete=models.CASCADE)
    class Meta:
        db_table = 'vpnmonitoring_clients'