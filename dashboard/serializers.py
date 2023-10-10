# serializers.py (inside your new app)

from rest_framework import serializers
from .models import MonitoringData, Services

class MonitoringDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringData
        fields = '__all__'
        
class ServiceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'
