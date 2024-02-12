from rest_framework import serializers
from backend.network.models import Interface

from backend.network.serializers import InterfaceSerializer

from .models import Area, AreaInterface, SdwanRules


class AreaInterfaceSerializer(serializers.ModelSerializer):
     
     class Meta:
          model = AreaInterface
          fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=Interface.objects.all())

    class Meta:
        model = Area
        fields = '__all__'
            
    
class SdwanRulesSerializer(serializers.ModelSerializer):
        
        area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())
    
        class Meta:
            model = SdwanRules
            fields = '__all__'
