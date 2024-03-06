from rest_framework import serializers
from backend.network.models import Interface
from backend.server_dhcp4.models import ServerDhcp4

class DHCP4ServerSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = ServerDhcp4
            fields = ['enable_dhcpv4','subnet_addr','subnet_mask','available_range',
                      'range_from','range_to','dns_server','gateway','domain_name'
                      'interface',
                      ]