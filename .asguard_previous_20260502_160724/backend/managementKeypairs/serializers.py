from rest_framework import serializers
from .models import PrivateKey, PublicKey

class PrivateKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateKey
        fields = '__all__'


class PublicKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicKey
        fields = '__all__'