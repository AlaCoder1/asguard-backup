from rest_framework import serializers
from  backend.ids_ips.models import *

#Rule
class RuleIdsIpsSerializer(serializers.ModelSerializer):
    suricatafile = serializers.PrimaryKeyRelatedField(queryset=suricatafile.objects.all())
    class Meta:
            model = ids_ips_rule
            fields = ['sid','action',
                      'protocol','source_ip','direction','destination_ip',
                      'msg','content','flowbit','rev',"rule",'suricatafile','activate_rule','default_rule'
                      ]

# class RuleSerializerForSwagger(serializers.Serializer):
#     id = serializers.IntegerField()
#     rule = RuleIdsIpsSerializer(exclude=['default_rule'])
class RuleSerializerForSwagger(serializers.ModelSerializer):
    class Meta:
        model = ids_ips_rule
        fields = ['id', 'sid', 'action', 'protocol', 'source_ip', 'direction', 'destination_ip',
                'msg', 'content', 'flowbit', 'rev', 'activate_rule',]
            
    id = serializers.IntegerField(required=False)
#Suricata Config
class SuricataFileSerializer(serializers.ModelSerializer):
    # interface = serializers.PrimaryKeyRelatedField(queryset=Interface.objects.all())
    class Meta:
            model = suricatafile
            fields = ['home_net','promisc','syslog','eve_log','mpm_algo','profile','copy_mode',
                      'interface_ids','status_enabled'
                     ]

#Alert       
class AlertSerializer(serializers.ModelSerializer):
    suricatafile = serializers.PrimaryKeyRelatedField(queryset=suricatafile.objects.all())
    class Meta:
            model = alert
            fields = ['timestamp','sid','priority',
                      'protocol','src_addr','src_port','dst_addr',
                      'dst_port','suricatafile','alert'
                      ]
