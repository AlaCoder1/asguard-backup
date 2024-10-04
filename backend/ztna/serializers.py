from rest_framework import serializers
from backend.ztna.models import *

class EnrollementsSerializer(serializers.ModelSerializer):
    identitie_id = serializers.PrimaryKeyRelatedField(source='identitie', queryset=Identities.objects.all())
    class Meta:
        model = Enrollements
        fields = ['date','time','type','identitie_id']


class IdentitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Identities
        fields = "__all__"


class IdentitiesSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Identities
        fields = ['token', 'date_expiration','name','attribute_identitie','type','is_admin', 'hostname']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class InterceptConfigsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterceptConfigs
        fields = "__all__"


class HostConfigsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostConfigs
        fields = "__all__"


class ServicesSerializer(serializers.ModelSerializer):
    host_id = serializers.PrimaryKeyRelatedField(source='host', queryset=HostConfigs.objects.all())
    intercept_id = serializers.PrimaryKeyRelatedField(source='intercept', queryset=InterceptConfigs.objects.all())

    class Meta:
        model = Services
        fields = ['ref_service', 'name', 'attribute_service', 'description', 'encryption', 'intercept_id', 'host_id', 'date_creation']


class RelaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relays
        fields = ['ref_relay','name','attribute_relay','tunneler','traversal','online','verified','date_creation','description','token']


class RelaySerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Relays
        fields = ['online', 'verified']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class RelaysPolicySerializer(serializers.ModelSerializer):
    relay_id = serializers.PrimaryKeyRelatedField(source='relay', queryset=Relays.objects.all())
    identity_id = serializers.PrimaryKeyRelatedField(source='identity', queryset=Identities.objects.all())
    class Meta:
        model = RelaysPolicy
        fields = [
            'ref_relay_policy',
            'name',
            'semantique',
            'description',
            'relay_id',
            'identity_id',
            'identity_attribute',
            'relay_attribute',
            'date_creation'
        ]


class ServicesPolicySerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(source='service', queryset=Services.objects.all())
    identity_id = serializers.PrimaryKeyRelatedField(source='identity', queryset=Identities.objects.all())
    class Meta:
        model = ServicesPolicy
        fields = [
            'ref_service_policy',
            'name',
            'semantique',
            'description',
            'type',
            'service_id',
            'identity_id',
            'identity_attribute',
            'service_attribute',
            'date_creation'
        ]


class ServicesRelaysPolicySerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(source='service', queryset=Services.objects.all())
    relay_id = serializers.PrimaryKeyRelatedField(source='relay', queryset=Relays.objects.all())
    class Meta:
        model = ServicesRelaysPolicy
        fields = [
            'ref_service_relay_policy',
            'name',
            'semantique',
            'description',
            'service_id',
            'relay_id',
            'relay_attribute',
            'service_attribute',
            'date_creation'
        ]
