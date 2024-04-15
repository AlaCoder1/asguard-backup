from rest_framework import serializers
from .models import ADServer

class ADServerSerializer(serializers.ModelSerializer):
    server_type = serializers.ChoiceField(choices=ADServer.SERVER_TYPES)

    class Meta:
        model = ADServer
        fields = '__all__'


