from rest_framework import serializers
from datetime import time
from .models import *

class ServerSatusSerialize(serializers.ModelSerializer):
    class Meta:
        model = ServerSatus
        fields = ('status')
        
class ProxyRulesSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(max_length=255)
    allow_by_auth = serializers.BooleanField()
    type = serializers.ChoiceField(choices=['ip', 'domain','subnet'])  
    value = serializers.IPAddressField(protocol='IPv4')  
    status = serializers.BooleanField()
    
    class Meta:
        model = ProxyRules
        fields = ('rule_name','type', 'value','status','allow_by_auth')
        
class ProxyRulesByTimeSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(max_length=255)
    allow_by_auth = serializers.BooleanField()
    type = serializers.ChoiceField(choices=['ip', 'domain','subnet']) 
    value = serializers.IPAddressField(protocol='IPv4')  
    status = serializers.BooleanField()
    time_from = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    time_to = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    days = serializers.CharField()

    class Meta:
        model = ProxyRules
        fields = ('rule_name','type', 'value','days','time_from','time_to','status','allow_by_auth')
        
    def validate_days(self, value):
        valid_days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}
        days_list = [day.strip() for day in value.split(',')]
        invalid_days = [day for day in days_list if day not in valid_days]
        if invalid_days:
            raise serializers.ValidationError(f"Invalid day(s): {', '.join(invalid_days)}")
        return value

    def validate(self, attrs):
        if attrs['time_from'] >= attrs['time_to']:
            raise serializers.ValidationError("`time_from` must be earlier than `time_to`.")
        return attrs
class CacheLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CacheLogs
        fields = "__all__"
class AccessLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLogs
        fields = "__all__"
class StoreLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreLogs
        fields = "__all__"
        

