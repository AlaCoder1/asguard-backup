from rest_framework import serializers
from backend.double_mask.models import DoubleMask

class DoubleMaskSerializer(serializers.ModelSerializer):
    class Meta:
            model = DoubleMask
            fields = "__all__"
