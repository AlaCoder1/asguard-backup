from rest_framework import serializers

from backend.nat.models import SNat


class SNatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SNat
        fields = '__all__'




