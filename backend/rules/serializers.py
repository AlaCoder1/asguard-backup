from rest_framework import serializers
from  backend.rules.models import *

class RuleSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = Rule
            fields = ['rule','rule_description','rule_status','type_rule',
                      'policy','protocol','saddr','sport',
                      'daddr','dport','interface'
                      ]