from rest_framework import serializers
from .models import *


class ServerSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('username', 'uid')


class ServerSerializerPost(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all())

    class Meta:
        model = Server
        fields = ('name_server', 'hostname', 'transport',
                  'protocol_version', 'scope', 'domaine_name', 'type')
