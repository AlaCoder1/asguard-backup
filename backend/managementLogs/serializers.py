# serializers.py (inside your new app)

from rest_framework import serializers

from backend.managementLogs.models import LogsData

class LogsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogsData
        fields = '__all__'
        
