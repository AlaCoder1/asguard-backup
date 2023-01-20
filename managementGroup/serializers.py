from rest_framework import serializers
from .models import *

class GroupSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields =  ('groupname', 'gid')
        
class GroupSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields =  ('groupname',)
