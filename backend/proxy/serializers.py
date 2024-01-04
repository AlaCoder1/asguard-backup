from rest_framework import serializers
from .models import *

class ServerSatusSerialize(serializers.ModelSerializer):
    class Meta:
        model = ServerSatus
        fields = ('status')
        
class ProxyRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyRules
        fields = ('rule_name','type', 'value','status','allow_by_auth')
        
class ProxyRulesByTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyRules
        fields = ('rule_name','type', 'value','days','time_from','time_to','status','allow_by_auth')
        
class ProxyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyUser
        fields = ('username')