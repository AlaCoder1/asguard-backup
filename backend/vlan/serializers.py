from rest_framework import serializers
from backend.network.models import Interface
from backend.vlan.models import Vlan

class VlanSerializer(serializers.ModelSerializer):
    parent_interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = Vlan
            fields = ['vlan_tag','vlan_priority','description',
                      'parent_interface',
                      ]