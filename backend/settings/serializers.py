from rest_framework import serializers
from .models import *

class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields =  ('hostname', 'domaine','time_zone')
        
        
class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        # fields =  ('prever_ipv4_ipv6', 'server_DNS','allow_server_DNS', 'exclude_interfaces','getway_failover')
        fields =  ('prever_ipv4_ipv6', 'server_dns','gateway')
        
        
class ServerReseauSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerReseau
        fields =  ('circular_logs', 'size_log_files','log_firewall_default_blocks', 'exclude_interfaces','xxx')
        

class TimezoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timezone
        fields =  ('name', )
        