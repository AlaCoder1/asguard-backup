import json
from django.core import serializers

from backend.ipsec.models import ServerIPsec


def get_all_server_ipsec():
    list_ipsec = []
    ipsec = ServerIPsec.objects.all()
    ipsecDict = serializers.serialize("json", ipsec)
    res = json.loads(ipsecDict)
    for i in range(len(res)):
        res[i].pop('model')
        id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id
        list_ipsec.append(res[i]['fields'])
    # return list_ipsec
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
    return res[0]['fields']