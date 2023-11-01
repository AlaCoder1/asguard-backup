from rest_framework import serializers
from .models import *
from backend.managementGroup.models import *
from django.contrib.auth import get_user_model
from backend.subscription.models import *

class UserSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'uid')


class UserSerializerPost(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all())
    # permission=serializers.PrimaryKeyRelatedField(many=True,queryset=Permission.objects.all())
    organisation = serializers.PrimaryKeyRelatedField(queryset=organization.objects.all())
    class Meta:
        model = User
        # fields =  ('username', 'password','fullname', 'email','role', 'uid', 'group','permission')
        fields = ('username', 'password', 'fullname',
                  'email', 'role', 'uid','organisation', 'group','is_active')
        write_only_fields = ('password')


class UserSerializerPostWithoutGroupAndPermission(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'fullname', 'email', 'role', 'uid','organisation','is_active')
        write_only_fields = ('password')


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('name', 'context',)
