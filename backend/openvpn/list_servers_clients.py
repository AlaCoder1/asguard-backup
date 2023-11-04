import json
from django.core import serializers

from backend.openvpn.models import ClientOpenvpn, ServerOpenvpn


def get_all_server_openvpn():
    """Getting all servers from database"""
    list_openvpn = []
    openvpn = ServerOpenvpn.objects.all()
    openvpnDict = serializers.serialize("json",openvpn)
    res = json.loads(openvpnDict)
    for i in range(0, len(res)):
        res[i].pop('model')
        id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id
        list_openvpn.append(res[i]['fields'])
    return list_openvpn
    

def get_server_openvpn(id):
    """Getting server by id from database"""
    server_openvpn = ServerOpenvpn.objects.filter(pk=id)
    server_openvpnDict = serializers.serialize("json", server_openvpn)
    res = json.loads(server_openvpnDict)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    return res[0]['fields']


def get_all_client_openvpn():
    """Getting all clients from database"""
    list_openvpn = []
    openvpn = ClientOpenvpn.objects.all()
    openvpnDict = serializers.serialize("json",openvpn)
    res = json.loads(openvpnDict)
    for i in range(0, len(res)):
        res[i].pop('model')
        id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id
        list_openvpn.append(res[i]['fields'])
    return list_openvpn


def get_client_openvpn(id):
    """Getting client by id from database"""
    client_openvpn = ClientOpenvpn.objects.filter(pk=id)
    client_openvpn = serializers.serialize("json", client_openvpn)
    res = json.loads(client_openvpn)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    return res[0]['fields']
