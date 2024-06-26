from django.core import serializers
from django.db.models import Count
import json

from backend.waf.models import AlertWaf, ApplicationRulesWaf, ApplicationWaf, ConfigWaf, RulesWaf
from backend.waf.utils import convert_waf_rule_database
from backend.waf.utils_alerts import create_list_alerts, rotate_log_alerts_waf, synchronize_database_waf_alert


# Configuration WAF
def get_one_waf_config():
    """Getting routing by id from database"""
    routing = ConfigWaf.objects.all()
    routing_dict = serializers.serialize("json", routing)
    res = json.loads(routing_dict)
    routing_id = res[0]['pk']
    res[0]['fields']['id'] = routing_id
    return res[0]['fields']


# Rules WAF list
def get_list_all_waf_rule():
    """Getting all WAF Rules from database"""

    list_waf = []
    wafs = RulesWaf.objects.exclude(name__in=["REQUEST-900-EXCLUSION-RULES-BEFORE-CRS", 
                                              "RESPONSE-999-EXCLUSION-RULES-AFTER-CRS"])
    waf_dict = serializers.serialize("json", wafs)
    res = json.loads(waf_dict)
    for rule in res:
        rule_id = rule['pk']
        rule['fields']['id'] = rule_id
        rule['fields'].pop("rule_content")
        rule['fields'].pop("rule_status")
        if rule['fields']['created']:
            rule['fields'] = convert_waf_rule_database(rule['fields'])
        list_app = ApplicationRulesWaf.objects.filter(rule_waf_id=rule_id)
        rule['fields']['application'] = [{'id': app.application_waf.pk,
                                          'name': app.application_waf.name} for app in list_app if app.rule_policy]
        list_waf.append(rule['fields'])
    return list_waf


def get_one_waf_rule(id):
    """Getting waf by id from database"""
    waf = RulesWaf.objects.filter(pk=id)
    waf_dict = serializers.serialize("json", waf)
    res = json.loads(waf_dict)
    waf_id = res[0]['pk']
    res[0]['fields']['id'] = waf_id
    res[0]['fields'].pop("rule_content")
    res[0]['fields'].pop("rule_status")
    if res[0]['fields']['created']:
        res[0]['fields'] = convert_waf_rule_database(res[0]['fields'])
    return res[0]['fields']


# Application WAF list
def get_list_all_waf_application():
    """Getting all waf applications from database"""

    list_waf_application = []
    waf_applications = ApplicationWaf.objects.all()
    waf_application_dict = serializers.serialize("json", waf_applications)
    res = json.loads(waf_application_dict)
    for waf_application in res:
        waf_application.pop('model')
        waf_application_id = waf_application['pk']
        waf_application.pop('pk')
        waf_application['fields']['id'] = waf_application_id
        # Convert country saved in database on str format to a list
        if waf_application['fields']['country'] and waf_application['fields']['country'] != '':
            waf_application['fields']['country'] = list(waf_application['fields']['country'].split(","))
        else:
            waf_application['fields']['country'] = []
        waf_application_rules = ApplicationRulesWaf.objects.filter(application_waf_id=waf_application_id)
        waf_application['fields']['rules'] = [{"rule_waf": rule.rule_waf.pk,
                                               "rule_name": rule.rule_waf.name,
                                               "rule_policy": rule.rule_policy,
                                               "rule_log": rule.rule_log,} for rule in waf_application_rules]
        list_waf_application.append(waf_application['fields'])
    return list_waf_application


def get_one_waf_application(id):
    """Getting waf application by id from database"""
    waf_application = ApplicationWaf.objects.filter(pk=id)
    waf_application_dict = serializers.serialize("json", waf_application)
    res = json.loads(waf_application_dict)
    res[0].pop('model')
    waf_application_id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = waf_application_id
    # Convert country saved in database on str format to a list
    if res[0]['fields']['country']:
        res[0]['fields']['country'] = list(res[0]['fields']['country'].split(","))
    else:
        res[0]['fields']['country'] = []
    waf_application_rules = ApplicationRulesWaf.objects.filter(application_waf_id=waf_application_id)
    res[0]['fields']['rules'] = [{"rule_waf": rule.rule_waf.pk,
                                  "rule_name": rule.rule_waf.name,
                                  "rule_policy": rule.rule_policy,
                                  "rule_log": rule.rule_log,} for rule in waf_application_rules]
    return res[0]['fields']


# Alerts WAF list
def get_alerts():
    """Getting waf alerts from database"""
    log_waf_content = rotate_log_alerts_waf()
    list_alert_system = create_list_alerts(log_waf_content)
    synchronize_database_waf_alert(list_alert_system)
    waf_alerts = AlertWaf.objects.order_by('-pk')
    waf_alert_dict = serializers.serialize("json", waf_alerts)
    res = json.loads(waf_alert_dict)
    violation_counts = AlertWaf.objects.values('violation_id').annotate(count=Count('violation_id')).order_by("-count")
    top_countries_counts = AlertWaf.objects.values('country').annotate(attacks=Count('country')).order_by("-attacks")
    alerts_dict = {"attacks": [{"violation": attack["violation_id"], "count_of_record": attack["count"]} for attack in violation_counts],
                   "top_countries": [{"country": country["country"], "attacks": country["attacks"]} for country in top_countries_counts],
                   "blocked_requests": []
                   }
    for waf_alert in res:
        waf_alert.pop('model')
        waf_alert_id = waf_alert['pk']
        waf_alert.pop('pk')
        waf_alert['fields']['id'] = waf_alert_id
        waf_alert['fields']['violation'] = f"{waf_alert['fields']['violation_id']} > {waf_alert['fields']['violation_file']}"
        waf_alert['fields'].pop('violation_id')
        waf_alert['fields'].pop('violation_file')
        alerts_dict["blocked_requests"].append(waf_alert['fields'])
    return alerts_dict
