from django.core import serializers
import json

from backend.nat.models import SNat
from backend.nat.utils import save_rules_handle_after_reboot


def get_list_all_snat():
    """Getting all snat from database"""
    save_rules_handle_after_reboot()

    list_snat = []
    snats = SNat.objects.all()
    snat_dict = serializers.serialize("json", snats)
    res = json.loads(snat_dict)
    for snat in res:
        snat_id = snat['pk']
        snat['fields']['id'] = snat_id
        list_snat.append(snat['fields'])
    return list_snat


def get_one_snat():
    """Getting snat by id from database"""
    snat = SNat.objects.filter(pk=id)
    snat_dict = serializers.serialize("json", snat)
    res = json.loads(snat_dict)
    snat_id = res[0]['pk']
    res[0]['fields']['id'] = snat_id
    return res[0]['fields']
