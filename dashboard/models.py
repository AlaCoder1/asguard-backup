from django.db import models

# Create your models here.
class MonitoringData(models.Model):
    timestamp = models.IntegerField()
    cpu_percentage = models.FloatField()
    memory_percentage = models.FloatField()
    
    class Meta:
        db_table = 'monitoringdata'    
