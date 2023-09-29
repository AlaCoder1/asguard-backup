from django.db import models

# Create your models here.
class Dashboard(models.Model):
    timestamp = models.IntegerField()
    cpu_percentage = models.FloatField()
    memory_percentage = models.FloatField()
  