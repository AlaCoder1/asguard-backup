from django.core import serializers
import json

from backend.sdwan.models import SdwanRules
from backend.sdwan.utils_system import synchronize_routing_table


def get_list_all_sdwan_rule():
    """Getting all sdwan_rules from database"""

    synchronize_routing_table()
    list_sdwan_rule = []
    sdwan_rules = SdwanRules.objects.all()
    sdwan_rule_dict = serializers.serialize("json", sdwan_rules)
    res = json.loads(sdwan_rule_dict)
    for sdwan_rule in res:
        sdwan_rule.pop('model')
        sdwan_rule_id = sdwan_rule['pk']
        sdwan_rule.pop('pk')
        sdwan_rule['fields']['id'] = sdwan_rule_id
        sdwan_rule['fields']['area_name'] = SdwanRules.objects.get(id=sdwan_rule_id).area.name
        list_sdwan_rule.append(sdwan_rule['fields'])
    return list_sdwan_rule


def get_one_sdwan_rule():
    """Getting sdwan_rule by id from database"""
    sdwan_rule = SdwanRules.objects.filter(pk=id)
    sdwan_rule_dict = serializers.serialize("json", sdwan_rule)
    res = json.loads(sdwan_rule_dict)
    res[0].pop('model')
    sdwan_rule_id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = sdwan_rule_id
    return res[0]['fields']