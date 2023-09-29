# serializers.py (inside your new app)

from rest_framework import serializers
from .models import MonitoringData

class MonitoringDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringData
        fields = '__all__'
