from rest_framework import serializers
from  rules.models import *

class RuleSerializer(serializers.ModelSerializer):
    interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = Rule
            fields = ['rule','Rule_description','rule_status','type_rule',
                      'policy','protocol','saddr','sport',
                      'daddr','dport','interface'
                      ]