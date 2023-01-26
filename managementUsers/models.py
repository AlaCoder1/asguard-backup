from django.db import models
from managementGroup.models import *
# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=800, null=True)
    uid = models.IntegerField(null=True)
    group = models.ManyToManyField(Group)
    # fullName = models.CharField(max_length=200, null=True)
    # email = models.CharField(max_length=200, null=True)
    
    class Meta:
        db_table = 'User'
        
    def __str__(self):
        return self.username
    
    
# class Group(models.Model):
#     namegroup = models.CharField(max_length=200, null=True)
#     class Meta:
#         db_table = 'Group'
#     def __str__(self):
#         return self.namegroup
