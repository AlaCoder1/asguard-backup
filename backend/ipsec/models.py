from django.db import models

# Create your models here.

class ServerIPsec(models.Model):

    #######################################
    ############### Phase 1 ###############
    #######################################

    # General Information
    conn_name = models.CharField(max_length=100, unique=True)
    connection_method = models.CharField(max_length=100, default='default', blank=True, null=True)
    key_exchange_version = models.CharField(max_length=100, default='ike', blank=True, null=True)
    internet_protocol = models.CharField(max_length=100, default='IPv4', blank=True, null=True)
    interface = models.CharField(max_length=100, default=None, null=True, blank=True)
    remote_gateway = models.CharField(max_length=100, default=None, null=True, blank=True)
    dynamic_gateway = models.BooleanField(default=False, null=True, blank=True)
    description_ph1 = models.CharField(max_length=300, default=None, null=True, blank=True)

    # Proposal (Authentication)
    authentication_method = models.CharField(max_length=100, default='Mutual PSK', blank=True, null=True)
    negotiation_mode = models.CharField(max_length=100, default=None, blank=True, null=True)
    pre_shared_key = models.CharField(max_length=100, default=None, blank=True, null=True)
    cert = models.CharField(max_length=300, default=None, null=True, blank=True)
    remote_distingushed_name = models.CharField(max_length=1000, default=None, blank=True, null=True)
    local_key_pair = models.CharField(max_length=100, default=None, blank=True, null=True)
    peer_key_pair = models.CharField(max_length=100, default=None, blank=True, null=True)

    # Proposal (Algorithms)
    encryption_algorithm_ph1 = models.CharField(max_length=100, default='128', blank=True, null=True)
    hash_algorithm_ph1 = models.CharField(max_length=100, default=None, blank=True, null=True)
    dh_key_group = models.CharField(max_length=100, default=None, blank=True, null=True)
    lifetime_ph1 = models.CharField(max_length=100, default=None, blank=True, null=True)

    # Advanced Options
    policy = models.BooleanField(default=True, blank=True, null=True)
    rekey = models.BooleanField(default=False, blank=True, null=True)
    reauth = models.BooleanField(default=False, blank=True, null=True)
    nat_traversal = models.CharField(max_length=100, default=None, blank=True, null=True)
    mobike = models.BooleanField(default=False, blank=True, null=True)
    deed_peer_detection = models.BooleanField(default=False, blank=True, null=True)
    deed_peer_delay = models.CharField(max_length=100, default=None, blank=True, null=True)
    deed_peer_timeout = models.CharField(max_length=100, default=None, blank=True, null=True)
    deed_peer_action = models.CharField(max_length=100, default=None, blank=True, null=True)
    inactivity_timeout = models.CharField(max_length=100, default=None, blank=True, null=True)
    margin_time = models.CharField(max_length=100, default=None, blank=True, null=True)
    rekey_fuzz = models.CharField(max_length=100, default=None, blank=True, null=True)

    #######################################
    ############### Phase 2 ###############
    #######################################

    # General Information
    mode = models.CharField(max_length=100, default='Tunnel IPv4', blank=True, null=True)
    description_ph2 = models.CharField(max_length=300, default=None, null=True, blank=True)

    # Tunnel Network
    local_address = models.CharField(max_length=100, default=None, blank=True, null=True)
    remote_address = models.CharField(max_length=300, default=None, null=True, blank=True)

    # Local Network
    type_local_network = models.CharField(max_length=100, default=None, blank=True, null=True)
    address_local_network = models.CharField(max_length=300, default=None, null=True, blank=True)

    # Remote Network
    type_remote_network = models.CharField(max_length=100, default=None, blank=True, null=True)
    address_remote_network = models.CharField(max_length=300, default=None, null=True, blank=True)

    # Proposal (Algorithms)
    protocol = models.CharField(max_length=100, default=None, blank=True, null=True)
    encryption_algorithm_ph2 = models.CharField(max_length=100, default=None, blank=True, null=True)
    hash_algorithm_ph2 = models.CharField(max_length=100, default=None, blank=True, null=True)
    pfs_key_group = models.CharField(max_length=100, default=None, blank=True, null=True)
    lifetime_ph2 = models.CharField(max_length=100, default=None, blank=True, null=True)

    # Advanced Options
    auto_ping_host = models.CharField(max_length=300, default=None, null=True, blank=True)
    manual_spd_entries = models.CharField(max_length=300, default=None, null=True, blank=True)

    class Meta:
        db_table = 'server_ipsec'