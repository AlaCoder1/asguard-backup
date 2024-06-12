from django.db import models

from backend.ipsec.models import ServerIPsec

# Create your models here.
class IpsecMonitoring(models.Model):
    establishetd_date=models.CharField(max_length=200,blank=True,unique=False)
    active_sessions=models.IntegerField(null=True,unique=False)
    availability= models.IntegerField(null=True,unique=False)
    bytes_in= models.IntegerField(null=True,unique=False)
    bytes_out= models.IntegerField(null=True,unique=False)
    total_bytes=models.IntegerField(null=True,unique=False)
    availability_bytes= models.IntegerField(null=True,unique=False)
    packet_loss= models.IntegerField(null=True,unique=False)
    timestamp=models.IntegerField(null=True,unique=False)
    time_added=models.FloatField(null=True,unique=False)
    tunnel = models.ForeignKey(
            ServerIPsec, on_delete=models.CASCADE)
 
    class Meta:
        db_table = 'ipsecmonitoring'
        
           