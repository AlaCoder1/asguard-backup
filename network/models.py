from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from managementUsers.models import User

# Create your models here.
##model interface
class Interface(models.Model):
    # gateway = models.ForeignKey(
            # Gateway, on_delete=models.CASCADE,null=True)
    ifname = models.CharField(max_length=200, null=True,unique=True)
    private_aux= models.BooleanField(default=False)
    bogon_aux = models.BooleanField(default=False)
    service_status=models.CharField(max_length=200, null=True,default=None)
    name_interface=models.CharField(max_length=200, null=True,default=None)
    description=models.CharField(max_length=200, null=True,default=None)
    # Created and updated timestamps
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now,editable=False)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Interface, self).save(*args, **kwargs)

    class Meta:
        db_table = 'interface'
    description=models.CharField(max_length=200, null=True,default=None)


    
#model generic config
from django.conf import settings
class GenericConfig(models.Model):
    interface = models.ForeignKey(
            Interface, on_delete=models.CASCADE)
    mtuv = models.IntegerField(null=True)
    addmac=models.CharField(max_length=200, null=True)
    mssv=models.IntegerField(null=True)
    speed_duplex=models.CharField(max_length=200, null=True)
      # Created and updated timestamps
    created_at = models.DateTimeField(default=timezone.now, editable=False,null=True)
    updated_at = models.DateTimeField(default=timezone.now,editable=False,null=True)
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
        db_table = 'genericConfig'


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
    addrgw=models.CharField(max_length=200, null=True,default=None)
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
            self.created_by = settings.CurrentUserId
            self.updated_by = settings.CurrentUserId
        self.updated_at = timezone.now()
        super(IP4Config, self).save(*args, **kwargs)
    class Meta:
        db_table = 'IP4Config'
        

#model to configure ipv6
class IP6Config(models.Model):

    interface = models.ForeignKey(
            Interface, on_delete=models.CASCADE, null=True)

    typeIP6=models.CharField(max_length=200, null=True,default=None)
    typeDHCP6=models.CharField(max_length=200, null=True,default=None)
    ##static
    ip6_address=models.CharField(max_length=200, null=True,default=None)
    netmask6=models.IntegerField(null=True,default=None)
    ##dhcp base 
    Request_only= models.BooleanField(default=False)
    Prefix_delegation=models.IntegerField(null=True,default=None)
    prefix_hint= models.BooleanField(default=False)
    IPv4_connectivity= models.BooleanField(default=False)
    VLAN_priority=models.CharField(max_length=200, null=True,default=None)
    ##dhcp advanced
     #interface status
    information_only=models.BooleanField(default=False)
    send_options=models.CharField(max_length=200, null=True,default=None)
    request_options=models.CharField(max_length=200, null=True,default=None)
    script=models.CharField(max_length=200, null=True,default=None)
    non_temporary=models.BooleanField(default=False)
    ####if non_temporary is true
    id_assoc=models.CharField(max_length=200, null=True,default=None)
    address=models.CharField(max_length=200, null=True,default=None)
    Nlifetime=models.CharField(max_length=200, null=True,default=None)
    Nvalid_time=models.CharField(max_length=200, null=True,default=None)
    ####
    
    prefix_delegation=models.CharField(max_length=200, null=True,default=None)
    ####if prefix_delegation is true
    id_assoc_pd=models.CharField(max_length=200, null=True,default=None)
    IPv6_Prefix=models.CharField(max_length=200, null=True,default=None)
    Plifetime=models.CharField(max_length=200, null=True,default=None)
    Pvalid_time=models.CharField(max_length=200, null=True,default=None)
    #####
    
    #authentification
    authname=models.CharField(max_length=200,null=True,default=None)
    protocol=models.CharField(max_length=200,null=True,default=None)
    algorithm=models.CharField(max_length=200, null=True,default=None)
    rdm=models.CharField(max_length=200, null=True,default=None)
    #key info
    keyname=models.CharField(max_length=200,null=True,default=None)
    royaume=models.CharField(max_length=200,null=True,default=None)
    keyid=models.CharField(max_length=200,null=True,default=None)
    secret=models.CharField(max_length=200, null=True,default=None)
    expire=models.CharField(max_length=200, null=True,default=None)
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
        super(IP6Config, self).save(*args, **kwargs)
    class Meta:
        db_table = 'IP6Config'




class tempsExucution(models.Model):
    type=models.CharField(max_length=200, null=True)
    cmd=models.TextField(max_length=10000, null=True)
    temps=models.FloatField(null=True)

    class Meta:
        db_table = 'tempsExucution'