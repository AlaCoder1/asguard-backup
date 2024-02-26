from django.db import models

class ADServer(models.Model):
    server_name = models.CharField(max_length=255)
    server_url = models.CharField(max_length=255)
    port = models.IntegerField(default=389)
    search_base = models.CharField(max_length=255)
    bind_user_dn = models.CharField(max_length=255)
    bind_user_password = models.CharField(max_length=255)
    ssl_tls_activation = models.BooleanField(default=False)
