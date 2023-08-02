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
# #serializer for ip6 config   
class IP6ConfigSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = IP6Config
            fields = ['typeIP6','typeDHCP6', 'ip6_address','netmask6',
                      'Request_only','Prefix_delegation','prefix_hint',
                      'IPv4_connectivity','VLAN_priority','information_only',
                      'send_options','request_options','script',
                      'non_temporary','id_assoc','address','Nlifetime','Nvalid_time',
                      'prefix_delegation','id_assoc_pd','IPv6_Prefix','Plifetime','Pvalid_time',
                      'authname','protocol','algorithm',
                      'rdm','keyname','royaume','keyid','secret','expire',
                      'interface',
                      ]
                      

            
#serializer for generic config        
class GenericConfigSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = GenericConfig
            fields = ['mtuV','addmac','mssV','speed_duplex','interface']
            

