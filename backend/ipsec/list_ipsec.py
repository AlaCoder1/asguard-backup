import json
from django.core import serializers

from backend.ipsec.models import ServerIPsec


def get_all_server_ipsec():
    list_ipsec = []
    ipsec = ServerIPsec.objects.all()
    ipsecDict = serializers.serialize("json", ipsec)
    res = json.loads(ipsecDict)
    for config in res:
        config.pop('model')
        id = config['pk']
        config.pop('pk')
        config['fields']['id'] = id
        config['fields']['hash_algorithm_ph1'] = list(config['fields']['hash_algorithm_ph1'].split(','))
        config['fields']['dh_key_group'] = list(config['fields']['dh_key_group'].split(','))
        if config['fields']['protocol'] == 'ESP':
            config['fields']['encryption_algorithm_ph2'] = list(config['fields']['encryption_algorithm_ph2'].split(','))
        config['fields']['hash_algorithm_ph2'] = list(config['fields']['hash_algorithm_ph2'].split(','))
        list_ipsec.append(config['fields'])
    return list_ipsec
    

def get_server_ipsec(id):
    """Getting server by id from database"""
    server_ipsec = ServerIPsec.objects.filter(pk=id)
    server_ipsecDict = serializers.serialize("json", server_ipsec)
    res = json.loads(server_ipsecDict)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    res[0]['fields']['hash_algorithm_ph1'] = list(res[0]['fields']['hash_algorithm_ph1'].split(','))
    res[0]['fields']['dh_key_group'] = list(res[0]['fields']['dh_key_group'].split(','))
    if res[0]['fields']['protocol'] == 'ESP':
        res[0]['fields']['encryption_algorithm_ph2'] = list(res[0]['fields']['encryption_algorithm_ph2'].split(','))
    res[0]['fields']['hash_algorithm_ph2'] = list(res[0]['fields']['hash_algorithm_ph2'].split(','))
    return res[0]['fields']
