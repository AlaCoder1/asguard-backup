from rest_framework import serializers
from .models import *
from backend.network.models import *

class InterfaceSerializer(serializers.ModelSerializer):
    class Meta:
            model = Interface
            fields = ['ifname', 'private_aux','bogon_aux','service_status','description',"name_interface"]

class InterfaceOpenVPNSerializer(serializers.ModelSerializer):
    class Meta:
            model = Interface
            fields = [ 'ifname', 'private_aux','bogon_aux','service_status','description', 'name_interface']
            

# #serializer for ip4 config   
class IP4ConfigSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = IP4Config
            fields = ['typeip4','typedhcp', 'ip_address','netmask','addrgw',
                      'reject','hostname','alias_add','alias_mask',
                      'timeout','retry','reboot','backoff','select_timeout','initial_interval',
                      'dhcp_client','domain_name','domain_server','lease_time','request','require',
                      'interface',
                      ]
# #serializer for ip6 config   
class IP6ConfigSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = IP6Config
            fields = ['typeip6','typedhcp6', 'ip_address6','netmask6',
                      'request_only','prefix_delegation_size','prefix_hint',
                      'ipv4_connectivity','vlan_priority','information_only',
                      'send_options','request_options','script',
                      'non_temporary','id_assoc','address','nlifetime','nvalid_time',
                      'prefix_delegation','id_assoc_pd','ipv6_prefix','plifetime','pvalid_time',
                      'authname','protocol','algorithm',
                      'rdm','keyname','royaume','keyid','secret','expire',
                      'interface',
                      ]

                      

            
#serializer for generic config        
class GenericConfigSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = GenericConfig
            fields = ['mtuv','addmac','mssv','speed_duplex','interface']
            

