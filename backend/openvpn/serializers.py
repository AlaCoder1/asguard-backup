from rest_framework import serializers
from .models import OpenVpnLogs, ServerOpenvpn, ClientOpenvpn


class ServerOpenvpnSerializer(serializers.ModelSerializer):
    class Meta:
            model = ServerOpenvpn
            fields = '__all__'
    
    def validate_name(self, value):
        # Check if an openvpn server with the same first 11 letters exists
        existing_servers = ServerOpenvpn.objects.filter(name__startswith=value[:11])
        
        if self.instance:
            # If updating an existing instance, exclude it from the check
            existing_servers = existing_servers.exclude(pk=self.instance.pk)

        if existing_servers.exists():
            raise serializers.ValidationError("Another server with the same first 11 letters already exists.")
        
        return value


class ClientOpenvpnSerializer(serializers.ModelSerializer):
    class Meta:
            model = ClientOpenvpn
            fields = '__all__'
            
class LogsVpnDataSerializer(serializers.ModelSerializer):
     class Meta:
            model = OpenVpnLogs
            fields = '__all__'