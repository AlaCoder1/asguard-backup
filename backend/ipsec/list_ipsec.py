import json
from django.core import serializers

from backend.ipsec.models import ServerIPsec
from utils.commands_utils import execute_command_without_arguments
from utils.errors_utils import CommandExecutionError


def get_status_ipsec():
    """Getting IPsec status from system"""
    try:
        execute_command_without_arguments(['sudo', 'ipsec', 'status'])
        return True
    except CommandExecutionError:
        return False


def get_list_all_server_ipsec():
    """Getting list of IPsec server from database"""
    list_ipsec = []
    ipsec = ServerIPsec.objects.all()
    ipsec_dict = serializers.serialize("json", ipsec)
    res = json.loads(ipsec_dict)
    for config in res:
        config.pop('model')
        id_ipsec = config['pk']
        config.pop('pk')
        config['fields']['id'] = id_ipsec
        config['fields']['hash_algorithm_ph1'] = list(config['fields']['hash_algorithm_ph1'].split(','))
        config['fields']['dh_key_group'] = list(config['fields']['dh_key_group'].split(','))
        if config['fields']['protocol'] == 'ESP':
            config['fields']['encryption_algorithm_ph2'] = list(config['fields']['encryption_algorithm_ph2'].split(','))
        config['fields']['hash_algorithm_ph2'] = list(config['fields']['hash_algorithm_ph2'].split(','))
        list_ipsec.append(config['fields'])
    return list_ipsec
    

def get_one_server_ipsec(id):
    """Getting server by id from database"""
    try:
        ServerIPsec.objects.get(pk=id)
    except ServerIPsec.DoesNotExist:
        return False
    server_ipsec = ServerIPsec.objects.filter(pk=id)
    server_ipsec_dict = serializers.serialize("json", server_ipsec)
    res = json.loads(server_ipsec_dict)
    res[0].pop('model')
    id_ipsec = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id_ipsec
    res[0]['fields']['hash_algorithm_ph1'] = list(res[0]['fields']['hash_algorithm_ph1'].split(','))
    res[0]['fields']['dh_key_group'] = list(res[0]['fields']['dh_key_group'].split(','))
    if res[0]['fields']['protocol'] == 'ESP':
        res[0]['fields']['encryption_algorithm_ph2'] = list(res[0]['fields']['encryption_algorithm_ph2'].split(','))
    res[0]['fields']['hash_algorithm_ph2'] = list(res[0]['fields']['hash_algorithm_ph2'].split(','))
    return res[0]['fields']
