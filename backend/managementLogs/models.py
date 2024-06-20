from django.db import models


# Create your models here.
class LogsData(models.Model):
    date = models.CharField(max_length=200, blank=True,unique=False)
    process = models.CharField(max_length=200, blank=True,unique=False)
    message = models.CharField(max_length=200, blank=True,unique=False)
    class Meta:
        db_table = 'logs_data'    