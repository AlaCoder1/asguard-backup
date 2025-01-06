from django.db import models
from django.utils.translation import gettext_lazy as _


class ServerOpenvpn(models.Model):
    name = models.CharField(max_length=100, default=None, null=True, blank=True, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=300, default=None, null=True, blank=True)
    server_mode = models.CharField(max_length=100, default="remote_access", null=True, blank=True)
    proto = models.CharField(max_length=10, default="udp", null=True, blank=True)
    dev = models.CharField(max_length=10, default="tun", null=True, blank=True)
    interface = models.CharField(max_length=100, default=None, null=True, blank=True)
    port = models.CharField(max_length=10, default="1194", null=True, blank=True, unique=True)
    ca_name = models.CharField(max_length=300, default=None, null=True, blank=True)
    cert_name = models.CharField(max_length=300, default=None, null=True, blank=True)
    dh = models.CharField(max_length=100, default=None, null=True, blank=True)
    cipher = models.CharField(max_length=100, default="AES-256-CBC", null=True, blank=True)
    auth = models.CharField(max_length=100, default="SHA256", null=True, blank=True)
    gateway = models.BooleanField(default=True, blank=True, null=True)
    ipv4_tunnel_network = models.CharField(max_length=300, default=None, blank=True, null=True)
    bridge_interface = models.CharField(max_length=100, default=None, null=True, blank=True)
    bridge_start_dhcp = models.CharField(max_length=100, default=None, null=True, blank=True)
    bridge_end_dhcp = models.CharField(max_length=100, default=None, null=True, blank=True)
    ipv4_local_network = models.CharField(max_length=300, default=None, null=True, blank=True)
    ipv4_remote_network = models.CharField(max_length=300, default=None, null=True, blank=True)
    concurrent_connections = models.CharField(max_length=10, default=None, null=True, blank=True)
    compression = models.CharField(max_length=100, default=None, blank=True, null=True)
    type_of_service = models.BooleanField(default=False, null=True, blank=True)
    duplicate_connections = models.BooleanField(default=True, null=True, blank=True)
    ipv6 = models.BooleanField(default=False, null=True, blank=True)
    inter_clients = models.BooleanField(default=False, null=True, blank=True)
    dynamic_ip = models.BooleanField(default=False, null=True, blank=True)
    address_pool_start = models.CharField(max_length=100, default=None, null=True, blank=True)
    address_pool_end = models.CharField(max_length=100, default=None, null=True, blank=True)
    dns_default_domain_server = models.CharField(max_length=100, default=None, null=True, blank=True)
    dns_server1 = models.CharField(max_length=300, default=None, null=True, blank=True)
    dns_server2 = models.CharField(max_length=300, default=None, null=True, blank=True)
    force_dns_cache_update = models.BooleanField(default=False, null=True, blank=True)
    ntp_server1 = models.CharField(max_length=300, default=None, null=True, blank=True)
    ntp_server2 = models.CharField(max_length=300, default=None, null=True, blank=True)
    client_management_port = models.CharField(max_length=10, default=None, null=True, blank=True)
    client_management_password = models.CharField(max_length=100, default=None, null=True, blank=True)
    verb = models.CharField(max_length=100, default="3", null=True, blank=True)
    server_status = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        db_table = 'server_openvpn'


class ClientOpenvpn(models.Model):
    name = models.CharField(max_length=255, default=None, null=True, blank=True, unique=True, verbose_name=_("name"))
    description = models.CharField(max_length=300, default=None, null=True, blank=True)
    server_mode = models.CharField(max_length=100, default="peer-to-peer", null=True, blank=True)
    proto = models.CharField(max_length=10, default=None, null=True, blank=True)
    dev = models.CharField(max_length=10, default=None, null=True, blank=True)
    resolv_retry = models.BooleanField(default=False, null=True, blank=True)
    proxy_host = models.CharField(max_length=300, default=None, null=True, blank=True)
    proxy_port = models.CharField(max_length=300, default=None, null=True, blank=True)
    proxy_authentication_option = models.CharField(max_length=100, default=None, null=True, blank=True)
    proxy_auth_username = models.CharField(max_length=100, default=None, null=True, blank=True)
    proxy_auth_password = models.CharField(max_length=100, default=None, null=True, blank=True)
    port = models.CharField(max_length=10, default="1194", null=True, blank=True)
    username = models.CharField(max_length=100, default=None, null=True, blank=True)
    password = models.CharField(max_length=100, default=None, null=True, blank=True)
    renegotiate_time = models.CharField(max_length=100, default=None, null=True, blank=True)
    ca_name = models.CharField(max_length=300, default=None, null=True, blank=True)
    cert_name = models.CharField(max_length=300, default=None, null=True, blank=True)
    cipher = models.CharField(max_length=100, default=None, null=True, blank=True)
    auth = models.CharField(max_length=100, default=None, null=True, blank=True)
    ipv4_tunnel_network = models.CharField(max_length=300, default=None, blank=True, null=True)
    ipv4_remote_network = models.CharField(max_length=300, default=None, null=True, blank=True)
    limit_outgoing_bandwidth = models.CharField(max_length=100, default=None, null=True, blank=True)
    compression = models.CharField(max_length=100, default=None, null=True, blank=True)
    type_of_service = models.BooleanField(default=False, null=True, blank=True)
    ipv6 = models.BooleanField(default=False, null=True, blank=True)
    pull_routes = models.BooleanField(default=False, null=True, blank=True)
    add_remove_routes = models.BooleanField(default=False, null=True, blank=True)
    verb = models.CharField(max_length=100, default=None, null=True, blank=True)
    server_remote = models.CharField(max_length=1000, default=None, null=True, blank=True)

    class Meta:
        db_table = 'client_openvpn'

class OpenVpnLogs(models.Model):
    log=models.TextField()

    class Meta:
        db_table = 'openvpn_logs'    