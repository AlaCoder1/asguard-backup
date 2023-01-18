from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=800, null=True)
    uid = models.IntegerField()
    # fullName = models.CharField(max_length=200, null=True)
    # email = models.CharField(max_length=200, null=True)
    

    def __str__(self):
        return self.titre
    
    
class Group(models.Model):
    namegroup = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return self.namegroup