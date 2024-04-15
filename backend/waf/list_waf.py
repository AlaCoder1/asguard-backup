from django.core import serializers
import json

from backend.waf.models import ConfigWaf


def get_one_waf_config():
    """Getting routing by id from database"""
    routing = ConfigWaf.objects.all()
    routing_dict = serializers.serialize("json", routing)
    res = json.loads(routing_dict)
    routing_id = res[0]['pk']
    res[0]['fields']['id'] = routing_id
    return res[0]['fields']
