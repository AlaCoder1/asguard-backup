from rest_framework import serializers
from .models import *

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields =  ('groupname', 'gid','created_by_system')
        
