from rest_framework import serializers

from backend.waf.models import ConfigWaf


class ConfigWafSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfigWaf
        fields = '__all__'
