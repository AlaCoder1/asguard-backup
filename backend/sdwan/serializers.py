from rest_framework import serializers

from .models import Area, SdwanRules


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = '__all__'
            
    
class SdwanRulesSerializer(serializers.ModelSerializer):
        
        area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())
    
        class Meta:
            model = SdwanRules
            fields = '__all__'
