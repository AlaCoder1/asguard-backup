from rest_framework import serializers
from .models import *
from managementGroup.models import *
from django.contrib.auth import get_user_model



class UserSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ('username', 'uid')


class UserSerializerPost(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(many=True,queryset=Group.objects.all())
    # permission=serializers.PrimaryKeyRelatedField(many=True,queryset=Permission.objects.all())
    class Meta:
        model = User
        # fields =  ('username', 'password','fullname', 'email','role', 'uid', 'group','permission')
        fields =  ('username', 'password','fullname', 'email','role', 'uid', 'group')
        write_only_fields = ('password')
        
       
        
class UserSerializerPostWithoutGroupAndPermission(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ('username', 'password','fullname', 'email','role', 'uid')
        write_only_fields = ('password')
        
            
        
            
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields =  ('name','context',)
        
