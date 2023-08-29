from gateway.models import *
from rest_framework import serializers
from network.models import *
# #serializer for ip4 config   
class GatewaySerializer(serializers.ModelSerializer):
    # interfaces = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=Interface.objects.all())
    class Meta:
            model = Gateway
            fields = ['gwname','gwaddress','staticgw','description', 'default_aux','far_aux',
                      'multiwan_aux'
                      ]
