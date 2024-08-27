from collections import Counter
from django.core import serializers
from django.db.models import Count
import json

from backend.waf.models import AlertWaf, ApplicationRulesWaf, ApplicationWaf, ConfigWaf, RulesWaf
from backend.waf.utils import convert_waf_rule_database
from backend.waf.utils_alerts import synchronize_database_waf_alert


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
    synchronize_database_waf_alert()
    waf_alerts = AlertWaf.objects.order_by('-pk')[:1000]
    waf_alert_dict = serializers.serialize("json", waf_alerts)
    res = json.loads(waf_alert_dict)

    # Count occurence of each violation_id
    list_violation_id_str = ""
    for violation_id_str in AlertWaf.objects.values('violation_id'):
        list_violation_id_str += violation_id_str["violation_id"] + "\n"
    list_violation_id = list(list_violation_id_str.split("\n"))
    list_violation_id = list(filter(lambda a: a != "", list_violation_id))
    # Count the frequency of each violation ID
    counter = Counter(list_violation_id)
    # Convert the counter to a list of objects
    violation_counts = [{'violation': violation_id, 'count_of_record': count_of_record} for violation_id, count_of_record in counter.items()]
    
    # Count occurence of each country
    top_countries_counts = AlertWaf.objects.values('country').annotate(attacks=Count('country')).order_by("-attacks")
    
    # Create list of blocked requests
    blocked_requests = []
    for waf_alert in res:
        waf_alert.pop('model')
        waf_alert_id = waf_alert['pk']
        waf_alert.pop('pk')
        waf_alert['fields']['id'] = waf_alert_id
        violation_id = waf_alert['fields'].pop('violation_id')
        violation_file = waf_alert['fields'].pop('violation_file')
        message = waf_alert['fields'].pop('message')
        if message.find("Access from blocked countries") > -1:
            list_violation_id = list(violation_id.split('\n'))
            list_violation_file = list(violation_file.split('\n'))
            waf_alert['fields']['message'] = list(message.split('\n'))
            waf_alert['fields']['violation'] = []
            for index in range(len(list_violation_id)):
                waf_alert['fields']['violation'].append(f"{list_violation_id[index]} > {list_violation_file[index]}")
            blocked_requests.append(waf_alert['fields'])
        else:
            waf_alert['fields']['message'] = [message]
            waf_alert['fields']['violation'] = [f"{violation_id} > {violation_file}"]
            blocked_requests.append(waf_alert['fields'])
    
    # Return an object contains attacks, top_countries and blocked_requests
    alerts_dict = {"attacks": violation_counts,
                   "top_countries": [{"country": country["country"], "attacks": country["attacks"]} for country in top_countries_counts],
                   "blocked_requests": blocked_requests
                   }
    return alerts_dict
