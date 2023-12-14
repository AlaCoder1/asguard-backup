from rest_framework import serializers
from .models import ClamAV,FreshclamDatabase


class ClamavSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClamAV
        fields = '__all__'


class FreshclamDatabaseSerializer(serializers.ModelSerializer):
    clamav = serializers.PrimaryKeyRelatedField(queryset=ClamAV.objects.all())
    
    class Meta:
        model = FreshclamDatabase
        fields = '__all__'
