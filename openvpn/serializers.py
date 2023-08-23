from rest_framework import serializers
from .models import *

class ServerOpenvpnSerializer(serializers.ModelSerializer):
    class Meta:
            model = ServerOpenvpn
            fields = ('server_name', 'description', 'port', 'proto', 'dev', 'topology', 'compression', 'dh','cipher','verb','interface')
            # fields = '__all__'


class ClientOpenvpnSerializer(serializers.ModelSerializer):
    class Meta:
            model = ClientOpenvpn
            fields = ('server_openvpn', 'client_name', 'port', 'proto', 'dev', 'auth', 'cipher','verb')
            # fields = '__all__'
