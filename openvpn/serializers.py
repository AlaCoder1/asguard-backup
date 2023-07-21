from rest_framework import serializers
from .models import *

class ServerOpenvpnSerializer(serializers.ModelSerializer):
    class Meta:
            model = ServerOpenvpn
            # fields = ('port','proto','dev','user','group','persist_key','persist_tun','keepalive','topology','server','ifconfig_pool_persist','push_ipv4_option1','push_ipv4_option2','push_ipv4_option3','server_ipv6','tun_ipv6','push_ipv6_option1','push_ipv6_option2','push_ipv6_option3','dh','ecdh_curve','tls_crypt','crl_verify','ca','cert','key','auth','cipher','ncp_ciphers','tls_server','tls_version_min','tls_cipher','client_config_dir','status','verb',)
            fields = '__all__'