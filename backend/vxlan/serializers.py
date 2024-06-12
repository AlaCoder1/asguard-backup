from rest_framework import serializers
from backend.network.models import Interface
from backend.vxlan.models import Vxlan

class VxlanSerializer(serializers.ModelSerializer):
    parent_interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = Vxlan
            fields = ['parent_interface','vxlan_interface_name','vxlan_id',
                      'vxlan_source_address','vxlan_destination_address','vxlan_destination_port',
                      'vxlan_connection_uuid'
                      ]