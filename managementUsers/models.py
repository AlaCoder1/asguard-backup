from django.db import models
from managementGroup.models import *
# Create your models here.


class Permission(models.Model):
    name=models.CharField(max_length=200,null=True)
    context=models.CharField(max_length=200,null=True)
    class Meta:
        db_table = 'permission'
    def __str__(self):
        return self.name
    
    
class User(models.Model):
    username = models.CharField(max_length=200, null=True,unique=True)
    password = models.CharField(max_length=800, null=True)
    fullname = models.CharField(max_length=800, null=True)
    email = models.CharField(max_length=800, null=True)
    role = models.CharField(max_length=800, null=True)
    uid = models.IntegerField(null=True,unique=True)
    group = models.ManyToManyField(Group)
    permission=models.ManyToManyField(Permission)
    
    class Meta:
        db_table = 'User'
        
    # def __str__(self):
    #     return self.username
