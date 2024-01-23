import json
from django.core import serializers

from backend.sdwan.models import Area, SdwanRules


def get_list_all_area():
    """Getting all areas from database"""

    list_area = []
    areas = Area.objects.all()
    area_dict = serializers.serialize("json", areas)
    res = json.loads(area_dict)
    for area in res:
        area.pop('model')
        area_id = area['pk']
        area.pop('pk')
        area['fields']['id'] = area_id
        area['fields']['members'] = list(area['fields']['members'].split(','))
        list_area.append(area['fields'])
    return list_area


def get_one_area(id):
    """Getting area by id from database"""
    area = Area.objects.filter(pk=id)
    area_dict = serializers.serialize("json", area)
    res = json.loads(area_dict)
    res[0].pop('model')
    area_id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = area_id
    res[0]['fields']['members'] = list(res[0]['fields']['members'].split(','))
    return res[0]['fields']


def get_list_all_sdwan_rule():
    """Getting all sdwan_rules from database"""

    list_sdwan_rule = []
    sdwan_rules = SdwanRules.objects.all()
    sdwan_rule_dict = serializers.serialize("json", sdwan_rules)
    res = json.loads(sdwan_rule_dict)
    for sdwan_rule in res:
        sdwan_rule.pop('model')
        sdwan_rule_id = sdwan_rule['pk']
        sdwan_rule.pop('pk')
        sdwan_rule['fields']['id'] = sdwan_rule_id
        sdwan_rule['fields']['members'] = list(sdwan_rule['fields']['members'].split(','))
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
    res[0]['fields']['members'] = list(res[0]['fields']['members'].split(','))
    return res[0]['fields']
