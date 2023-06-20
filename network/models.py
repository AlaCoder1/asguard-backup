from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from managementUsers.models import User
# Create your models here.
##model interface
class Interface(models.Model):
    ifname = models.CharField(max_length=200, null=True,unique=True)
    private_aux= models.BooleanField(default=False)
    bogon_aux = models.BooleanField(default=False)
    service_status=models.CharField(max_length=200, null=True,default=None)
    # Created and updated timestamps
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now,editable=False)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Interface, self).save(*args, **kwargs)

    class Meta:
        db_table = 'Interface'

    def __str__(self):
        return self.ifname
    
#model generic config
from django.conf import settings
class GenericConfig(models.Model):
    interface = models.ForeignKey(
            Interface, on_delete=models.CASCADE)
    mtuV = models.IntegerField(null=True)
    addmac=models.CharField(max_length=200, null=True)
    mssV=models.IntegerField(null=True)
    speed_duplex=models.CharField(max_length=200, null=True)
      # Created and updated timestamps
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now,editable=False)
    created_by = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
            self.created_by = settings.CurrentUserId
            self.updated_by = settings.CurrentUserId
        self.updated_at = timezone.now()
        super(GenericConfig, self).save(*args, **kwargs)
    class Meta:
        db_table = 'GenericConfig'


#model to configure ipv4
class IP4Config(models.Model):
     ##
    interface = models.ForeignKey(
            Interface, on_delete=models.CASCADE, null=True)

    typeIP4=models.CharField(max_length=200, null=True,default=None)
    typeDHCP=models.CharField(max_length=200, null=True,default=None)
    ##static
    ip_address=models.CharField(max_length=200, null=True,default=None)
    netmask=models.IntegerField(null=True,default=None)
    ##dhcp base 
    reject=models.CharField(max_length=200, null=True,default=None)
    hostname=models.CharField(max_length=200, null=True,default=None)
    alias_add=models.CharField(max_length=200, null=True,default=None)
    alias_mask=models.CharField(max_length=200, null=True,default=None)
    ##dhcp advanced
     #time protocol
    timeout=models.IntegerField(null=True,default=None)
    retry=models.IntegerField(null=True, default=None)
    reboot=models.IntegerField(null=True, default=None)
    backoff=models.IntegerField(null=True, default=None)
    select_timeout=models.IntegerField(null=True, default=None)
    initial_interval=models.IntegerField(null=True, default=None)
    #other
    dhcp_client=models.CharField(max_length=200,null=True,default=None)
    domaine_name=models.CharField(max_length=200,null=True,default=None)
    domain_server=models.CharField(max_length=200,null=True,default=None)
    lease_time=models.CharField(max_length=200, null=True,default=None)
    request=models.CharField(max_length=200, null=True,default=None)
    require=models.CharField(max_length=200,null=True,default=None)
      # Created and updated timestamps
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now,editable=False)
    created_by = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(IP4Config, self).save(*args, **kwargs)
    class Meta:
        db_table = 'IP4Config'
        


            

            


