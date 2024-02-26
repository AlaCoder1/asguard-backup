from rest_framework import serializers
from .models import ADServer

class ADServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ADServer
        fields = '__all__'


