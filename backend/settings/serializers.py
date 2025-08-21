from rest_framework import serializers

from backend.network.models import Interface
from backend.settings.models import Network, ServerReseau, SettingInterface, System, Timezone,Settings


class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields =  ('hostname', 'domaine','time_zone', 'language')
        
        
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
class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields =  "__all__"

class SettingsInterfaceSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
      
    class Meta:
            model = SettingInterface
            fields = '__all__'