from rest_framework import serializers

from backend.waf.models import AlertWaf, ApplicationRulesWaf, ApplicationWaf, ConfigWaf, RulesWaf


class ConfigWafSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfigWaf
        fields = '__all__'


class RulesWafSerializer(serializers.ModelSerializer):

    class Meta:
        model = RulesWaf
        fields = '__all__'


class ApplicationRulesWafSerializer(serializers.ModelSerializer):
     
     class Meta:
          model = ApplicationRulesWaf
          fields = ['rule_waf', 'rule_policy', 'rule_log']


class ApplicationWafSerializer(serializers.ModelSerializer):
    rules = ApplicationRulesWafSerializer(many=True)

    class Meta:
        model = ApplicationWaf
        fields = ['name', 'application_type', 'application_protocol', 'certificate_name', 'application_value', 'application_port', 'description', 'country', 
                  'rule_geoip_id', 'rules']

    def create(self, validated_data:dict):
        rules_data = validated_data.pop('rules')
        application_waf = ApplicationWaf.objects.create(**validated_data)
        for rule_data in rules_data:
            rule_waf = rule_data.pop('rule_waf')
            ApplicationRulesWaf.objects.create(application_waf=application_waf, rule_waf=rule_waf, **rule_data)
        return application_waf
    
    def update(self, application_waf:ApplicationWaf, validated_data:dict):
        rules_data = validated_data.pop('rules')
        
        # Update the ApplicationWaf instance
        application_waf.name = validated_data.get('name', application_waf.name)
        application_waf.application_type = validated_data.get('application_type', application_waf.application_type)
        application_waf.application_protocol = validated_data.get('application_protocol', application_waf.application_protocol)
        application_waf.certificate_name = validated_data.get('certificate_name', None)
        application_waf.application_value = validated_data.get('application_value', application_waf.application_value)
        application_waf.application_port = validated_data.get('application_port', application_waf.application_port)
        application_waf.description = validated_data.get('description', application_waf.description)
        application_waf.country = validated_data.get('country', application_waf.country)
        application_waf.save()

        # Handle the rules
        for rule_data in rules_data:
            rule_waf = rule_data.pop('rule_waf')
            
            try:
                # If rule_id is provided, update the existing rule
                rule_instance = ApplicationRulesWaf.objects.get(rule_waf=rule_waf, application_waf=application_waf)
                rule_instance.rule_waf = rule_waf
                for attr, value in rule_data.items():
                    setattr(rule_instance, attr, value)
                rule_instance.save()
            except ApplicationRulesWaf.DoesNotExist:
                # If no rule_id is provided, create a new rule
                ApplicationRulesWaf.objects.create(application_waf=application_waf, rule_waf=rule_waf, **rule_data)

        return application_waf


class AlertWafSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertWaf
        fields = '__all__'
