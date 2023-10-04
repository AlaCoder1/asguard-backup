from django.db import models

# Create your models here.


class Type(models.Model):
    type_name = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'Type'


class Server(models.Model):
    name_server = models.CharField(max_length=200, null=True)
    hostname = models.CharField(max_length=800, null=True)
    transport = models.CharField(max_length=800, null=True)
    protocol_version = models.CharField(max_length=800, null=True)
    scope = models.CharField(max_length=800, null=True)
    domaine_name = models.CharField(max_length=200, null=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Server'
