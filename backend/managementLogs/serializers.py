# serializers.py (inside your new app)

from rest_framework import serializers

from backend.managementLogs.models import LogrotateData, LogsData

class LogsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogsData
        fields = '__all__'
        

class LogrotateDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogrotateData
        fields = '__all__'