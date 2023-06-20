from rest_framework import serializers
from .models import *
from network.models import *

class InterfaceSerializer(serializers.ModelSerializer):
    class Meta:
            model = Interface
            fields = ['ifname', 'private_aux','bogon_aux','service_status']
            

# #serializer for ip4 config   
class IP4ConfigSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = IP4Config
            fields = ['typeIP4','typeDHCP', 'ip_address','netmask',
                      'reject','hostname','alias_add','alias_mask',
                      'timeout','retry','reboot','backoff','select_timeout','initial_interval',
                      'dhcp_client','domaine_name','domain_server','lease_time','request','require',
                      'interface',
                      ]

            
#serializer for generic config        
class GenericConfigSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = GenericConfig
            fields = ['mtuV','addmac','mssV','speed_duplex','interface']
            

