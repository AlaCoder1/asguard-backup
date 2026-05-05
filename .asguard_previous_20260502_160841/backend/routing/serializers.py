from rest_framework import serializers

from backend.gateway.models import Gateway
from backend.routing.models import Routing


class RoutingSerializer(serializers.ModelSerializer):

    gateway = serializers.PrimaryKeyRelatedField(queryset=Gateway.objects.all())

    class Meta:
        model = Routing
        fields = '__all__'
