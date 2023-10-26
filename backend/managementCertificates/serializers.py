from rest_framework import serializers
from .models import *

class CertificateAuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateAuthority
        # fields = ('name', 'certificate_path', 'valid_from', 'valid_until')
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        # fields = ('certificate_authority', 'name', 'certificate_path', 'certificate_type', 'activation')
        fields = '__all__'
