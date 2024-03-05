from django.core import serializers
import json

from backend.nat.models import DNat, OneToOneNat, SNat
from backend.nat.utils import save_rules_handle_after_reboot


# SNAT list
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
        snat['fields']['interface_name'] = SNat.objects.get(id=snat_id).interface.name_interface
        list_snat.append(snat['fields'])
    return list_snat


def get_one_snat(id):
    """Getting snat by id from database"""
    snat = SNat.objects.filter(pk=id)
    snat_dict = serializers.serialize("json", snat)
    res = json.loads(snat_dict)
    snat_id = res[0]['pk']
    res[0]['fields']['id'] = snat_id
    res[0]['fields']['interface_name'] = SNat.objects.get(id=snat_id).interface.name_interface
    return res[0]['fields']


# OneToOne Nat list
def get_list_all_one_to_one_nat():
    """Getting all one_to_one_nat from database"""

    list_one_to_one_nat = []
    one_to_one_nats = OneToOneNat.objects.all()
    one_to_one_nat_dict = serializers.serialize("json", one_to_one_nats)
    res = json.loads(one_to_one_nat_dict)
    for one_to_one_nat in res:
        one_to_one_nat_id = one_to_one_nat['pk']
        one_to_one_nat['fields']['id'] = one_to_one_nat_id
        one_to_one_nat['fields']['interface_name'] = OneToOneNat.objects.get(id=one_to_one_nat_id).interface.name_interface
        list_one_to_one_nat.append(one_to_one_nat['fields'])
    return list_one_to_one_nat


def get_one_one_to_one_nat(id):
    """Getting one_to_one_nat by id from database"""
    one_to_one_nat = OneToOneNat.objects.filter(pk=id)
    one_to_one_nat_dict = serializers.serialize("json", one_to_one_nat)
    res = json.loads(one_to_one_nat_dict)
    one_to_one_nat_id = res[0]['pk']
    res[0]['fields']['id'] = one_to_one_nat_id
    res[0]['fields']['interface_name'] = OneToOneNat.objects.get(id=one_to_one_nat_id).interface.name_interface
    return res[0]['fields']


# DNAT list
def get_list_all_dnat():
    """Getting all dnat from database"""

    list_dnat = []
    dnats = DNat.objects.all()
    dnat_dict = serializers.serialize("json", dnats)
    res = json.loads(dnat_dict)
    for dnat in res:
        dnat_id = dnat['pk']
        dnat['fields']['id'] = dnat_id
        dnat['fields']['interface_name'] = DNat.objects.get(id=dnat_id).interface.name_interface
        list_dnat.append(dnat['fields'])
    return list_dnat


def get_one_dnat(id):
    """Getting dnat by id from database"""
    dnat = DNat.objects.filter(pk=id)
    dnat_dict = serializers.serialize("json", dnat)
    res = json.loads(dnat_dict)
    dnat_id = res[0]['pk']
    res[0]['fields']['id'] = dnat_id
    res[0]['fields']['interface_name'] = DNat.objects.get(id=dnat_id).interface.name_interface
    return res[0]['fields']
