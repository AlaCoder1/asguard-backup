from rest_framework import serializers
from .models import *


class ServerOpenvpnSerializer(serializers.ModelSerializer):
    class Meta:
            model = ServerOpenvpn
            fields = '__all__'


class ClientOpenvpnSerializer(serializers.ModelSerializer):
    class Meta:
            model = ClientOpenvpn
            fields = '__all__'