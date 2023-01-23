from rest_framework import serializers
from .models import User

class UserSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ('username', 'uid')


class UserSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ('username', 'password')
