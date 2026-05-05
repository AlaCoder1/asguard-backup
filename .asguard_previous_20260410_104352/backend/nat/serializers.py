from rest_framework import serializers

from backend.nat.models import DNat, OneToOneNat, SNat


class SNatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SNat
        fields = '__all__'


class OneToOneNatSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneToOneNat
        fields = '__all__'


class DNatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DNat
        fields = '__all__'




