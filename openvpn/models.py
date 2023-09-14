from django.db import models

from network.models import Interface

# Create your models here.

class ServerOpenvpn(models.Model):
    name = models.CharField(max_length=100, default=None, null=True, blank=True, unique=True)
    description = models.CharField(max_length=300, default=None, null=True, blank=True)
    proto = models.CharField(max_length=10, default="udp", null=True, blank=True)
    dev = models.CharField(max_length=10, default="tun", null=True, blank=True)
    interface = models.CharField(max_length=100, default=None, null=True, blank=True)
    port = models.CharField(max_length=10, default="1194", null=True, blank=True, unique=True)
    ca = models.CharField(max_length=300, default=None, null=True, blank=True)
    cert = models.CharField(max_length=300, default=None, null=True, blank=True)
    key = models.CharField(max_length=300, default=None, null=True, blank=True)
    secret = models.CharField(max_length=300, default=None, null=True, blank=True)
    dh = models.CharField(max_length=100, default=None, null=True, blank=True)
    cipher = models.CharField(max_length=100, default="AES-256-CBC", null=True, blank=True)
    auth = models.CharField(max_length=100, default="SHA256", null=True, blank=True)
    hardware_crypto = models.CharField(max_length=100, default="No Hardware Crypto", null=True, blank=True)
    gateway = models.BooleanField(default=True, blank=True, null=True)
    bridge_interface = models.CharField(max_length=100, default=None, null=True, blank=True)
    bridge_start_dhcp = models.CharField(max_length=100, default=None, null=True, blank=True)
    bridge_end_dhcp = models.CharField(max_length=100, default=None, null=True, blank=True)
    ipv4_local_network = models.CharField(max_length=300, default=None, null=True, blank=True)
    ipv4_remote_network = models.CharField(max_length=300, default=None, null=True, blank=True)
    compression = models.CharField(max_length=100, default=None, blank=True, null=True)
    type_of_service = models.BooleanField(default=False, null=True, blank=True)
    duplicate_connections = models.BooleanField(default=True, null=True, blank=True)
    ipv6 = models.BooleanField(default=False, null=True, blank=True)
    inter_clients = models.BooleanField(default=False, null=True, blank=True)
    dynamic_ip = models.BooleanField(default=False, null=True, blank=True)
    topology = models.BooleanField(default=True, null=True, blank=True)
    dns_default_domain = models.CharField(max_length=100, default=None, null=True, blank=True)
    dns_server1 = models.CharField(max_length=300, default=None, null=True, blank=True)
    dns_server2 = models.CharField(max_length=300, default=None, null=True, blank=True)
    force_dns_cache_update = models.BooleanField(default=False, null=True, blank=True)
    ntp_server1 = models.CharField(max_length=300, default=None, null=True, blank=True)
    ntp_server2 = models.CharField(max_length=300, default=None, null=True, blank=True)
    verb = models.CharField(max_length=100, default="3", null=True, blank=True)

    class Meta:
        db_table = 'ServerOpenvpn'


class ClientOpenvpn(models.Model):
    server_openvpn = models.ForeignKey(ServerOpenvpn, on_delete=models.CASCADE, default=None, null=True, blank=True)
    name = models.CharField(max_length=255, default=None, null=True, blank=True, unique=True)
    description = models.CharField(max_length=300, default=None, null=True, blank=True)
    proto = models.CharField(max_length=10, default=None, null=True, blank=True)
    dev = models.CharField(max_length=10, default=None, null=True, blank=True)
    interface = models.CharField(max_length=100, default=None, null=True, blank=True)
    resolv_retry = models.BooleanField(default=False, null=True, blank=True)
    port = models.CharField(max_length=10, default="1194", null=True, blank=True, unique=True)
    ca = models.CharField(max_length=300, default=None, null=True, blank=True)
    cert = models.CharField(max_length=300, default=None, null=True, blank=True)
    key = models.CharField(max_length=300, default=None, null=True, blank=True)
    secret = models.CharField(max_length=300, default=None, null=True, blank=True)
    cipher = models.CharField(max_length=100, default=None, null=True, blank=True)
    auth = models.CharField(max_length=100, default=None, null=True, blank=True)
    hardware_crypto = models.CharField(max_length=100, default="No Hardware Crypto", null=True, blank=True)
    ipv4_remote = models.CharField(max_length=100, default=None, null=True, blank=True)
    compression = models.CharField(max_length=100, default=None, null=True, blank=True)
    type_of_service = models.BooleanField(default=False, null=True, blank=True)
    ipv6 = models.BooleanField(default=False, null=True, blank=True)
    verb = models.CharField(max_length=100, default=None, null=True, blank=True)

    class Meta:
        db_table = 'ClientOpenvpn'
