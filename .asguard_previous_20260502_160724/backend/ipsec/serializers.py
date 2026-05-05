from rest_framework import serializers
from .models import ServerIPsec


class ServerIPsecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerIPsec
        fields = '__all__'