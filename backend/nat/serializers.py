from rest_framework import serializers

from backend.nat.models import DNat, SNat


class SNatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SNat
        fields = '__all__'


class DNatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DNat
        fields = '__all__'




