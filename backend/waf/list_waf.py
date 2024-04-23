from django.core import serializers
import json

from backend.waf.models import ConfigWaf, RulesWaf


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
def get_list_all_waf():
    """Getting all WAF Rules from database"""

    list_waf = []
    wafs = RulesWaf.objects.exclude(name__in=["REQUEST-900-EXCLUSION-RULES-BEFORE-CRS", 
                                              "RESPONSE-999-EXCLUSION-RULES-AFTER-CRS"])
    waf_dict = serializers.serialize("json", wafs)
    res = json.loads(waf_dict)
    for waf in res:
        waf_id = waf['pk']
        waf['fields']['id'] = waf_id
        list_waf.append(waf['fields'])
    return list_waf


def get_one_waf(id):
    """Getting waf by id from database"""
    waf = RulesWaf.objects.filter(pk=id)
    waf_dict = serializers.serialize("json", waf)
    res = json.loads(waf_dict)
    waf_id = res[0]['pk']
    res[0]['fields']['id'] = waf_id
    return res[0]['fields']
