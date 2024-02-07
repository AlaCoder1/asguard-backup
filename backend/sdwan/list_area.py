import json
from django.core import serializers

from backend.sdwan.models import Area


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
