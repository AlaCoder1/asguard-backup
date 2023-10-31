from rest_framework import serializers
from .models import IPsecServer, IPsecSecrets


class IPsecServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPsecServer
        fields = '__all__'