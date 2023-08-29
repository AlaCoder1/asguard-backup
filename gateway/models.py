
from django.db import models
from django.utils import timezone
from network.models import Interface
# Create your models here.
###model Gateway
class Gateway(models.Model):
    # interfaces = models.ManyToManyField(Interface, related_name='Interfaces', through='GatewayInterface')
    gwname=models.CharField(max_length=200, null=True,unique=True)
    gwaddress=models.CharField(max_length=200, null=True,unique=True)
    staticgw=models.BooleanField(default=False)
    description=models.CharField(max_length=200, null=True)
    default_aux= models.BooleanField(default=True)
    far_aux= models.BooleanField(default=False)
    multiwan_aux= models.BooleanField(default=False)
    # Created and updated timestamps
    created_at = models.DateTimeField(default=timezone.now, editable=False,null=True)
    updated_at = models.DateTimeField(default=timezone.now,editable=False,null=True)

    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Gateway, self).save(*args, **kwargs)

    class Meta:
        db_table = 'Gateway'    
        
class GatewayInterface(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    gateway = models.ForeignKey(Gateway, on_delete=models.CASCADE)
    metric=models.IntegerField(null=True,default=0)
    class Meta:
        db_table = 'GatewayInterface'    