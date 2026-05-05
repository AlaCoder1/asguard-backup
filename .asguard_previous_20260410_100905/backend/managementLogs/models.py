from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class LogsData(models.Model):
    date = models.CharField(max_length=200, blank=True, unique=False)
    process = models.CharField(max_length=200, blank=True, unique=False)
    message = models.CharField(max_length=200, blank=True, unique=False)
    class Meta:
        db_table = 'logs_data'    
        
class LogrotateData(models.Model):
    service=models.CharField(max_length=200, blank=True, unique=False)
    filename = models.CharField(max_length=200, blank=True, unique=True, verbose_name=_("file name"))
    original_path = models.CharField(max_length=200, blank=True, unique=False)
    backup_path = models.CharField(max_length=200, blank=True, unique=False)
    date=models.CharField(max_length=200, blank=True, unique=False)
    class Meta:
        db_table = 'logrotate_data'  
          
