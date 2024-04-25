from rest_framework import serializers

from backend.waf.models import ConfigWaf, RulesWaf


class ConfigWafSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfigWaf
        fields = '__all__'


class RulesWafSerializer(serializers.ModelSerializer):

    class Meta:
        model = RulesWaf
        fields = '__all__'
