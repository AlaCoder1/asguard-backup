from rest_framework import serializers

from backend.gateway.models import Gateway, GatewayInterface
from backend.network.models import Interface


class GatewaySerializer(serializers.ModelSerializer):
    # interfaces = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=Interface.objects.all())
    class Meta:
            model = Gateway
            fields = ['gwname','gwaddress','staticgw','description', 'default_aux','far_aux',
                      'multiwan_aux','ipv4_gw'
                      ]


class GatewayInterfaceSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
      
    class Meta:
            model = GatewayInterface
            fields = '__all__'
