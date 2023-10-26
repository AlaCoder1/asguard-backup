from django.db import models

# Create your models here.

class IPsecServer(models.Model):
    conn_name = models.CharField(max_length=100, unique=True)
    authby = models.CharField(max_length=100)
    left = models.CharField(max_length=100)
    leftid = models.CharField(max_length=100)
    leftsubnet = models.CharField(max_length=100)
    right = models.CharField(max_length=100)
    rightsubnet = models.CharField(max_length=100)
    ike = models.CharField(max_length=100)
    esp = models.CharField(max_length=100)
    keyexchange = models.CharField(max_length=100)
    keyingtries = models.CharField(max_length=100)
    ikelifetime = models.CharField(max_length=100)
    lifetime = models.CharField(max_length=100)
    dpddelay = models.CharField(max_length=100)
    dpdaction = models.CharField(max_length=100)
    dpdaction = models.CharField(max_length=100)
    auto = models.CharField(max_length=100)


class IPsecSecrets(models.Model):
    server_ipsec = models.ForeignKey(IPsecServer, on_delete=models.CASCADE)
    peer_address = models.CharField(max_length=100)
    local_address = models.CharField(max_length=100)
    authentication_method = models.CharField(max_length=100)
    shared_secret = models.CharField(max_length=100)
