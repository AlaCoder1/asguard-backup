from rest_framework import serializers
from .models import *

class ProxyRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyRules
        fields = ('rule_name','type', 'value','status','allow_by_auth')
        
class ProxyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyUser
        fields = ('username')