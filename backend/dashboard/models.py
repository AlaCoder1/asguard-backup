from django.db import models

# Create your models here.
class MonitoringData(models.Model):
    timestamp = models.IntegerField()
    cpu_percentage = models.FloatField()
    memory_percentage = models.FloatField()
    
    class Meta:
        db_table = 'monitoring_data'    
class Services(models.Model):
    service_name=models.CharField(max_length=200, null=True,unique=True)
    description=models.CharField(max_length=200, null=True,unique=True)
    status_enabled=models.BooleanField(default=False)
    status_started=models.BooleanField(default=False)
    status_install=models.BooleanField(default=False)
    class Meta:
        db_table = 'services '  