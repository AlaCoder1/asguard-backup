from rest_framework import serializers
from .models import *
from managementGroup.models import *

class UserSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ('username', 'uid')


class UserSerializerPost(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(many=True,queryset=Group.objects.all())
    class Meta:
        model = User
        fields =  ('username', 'password','uid', 'group')
