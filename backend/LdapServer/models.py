from django.db import models

class ADServer(models.Model):
    SERVER_TYPES = [
        ('openldap', 'OpenLDAP Server'),
        ('ad', 'Active Directory Server'),
    ]
    server_name = models.CharField(max_length=255, blank=False, null=False,unique=True)
    server_url = models.CharField(max_length=255, blank=False, null=False)
    port = models.IntegerField(default=389, blank=False, null=False)
    search_base = models.CharField(max_length=255, blank=False, null=False)
    bind_user_dn = models.CharField(max_length=255, blank=False, null=False)
    bind_user_password = models.CharField(max_length=255,blank=False, null=False)
    ssl_tls_activation = models.BooleanField(default=False, blank=False, null=False)
    server_type = models.CharField(max_length=10, choices=SERVER_TYPES, default='openldap')

    class Meta:
        db_table = 'ad_server'
            