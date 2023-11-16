import json
from django.core import serializers
from backend.managementCertificates.models import Certificate

from backend.openvpn.models import ClientOpenvpn, ServerOpenvpn


def get_all_server_openvpn():
    """Getting all servers from database"""
    list_server = []
    server = ServerOpenvpn.objects.all()
    serverDict = serializers.serialize("json",server)
    res = json.loads(serverDict)
    for serv in res:
        certificate = Certificate.objects.get(name=serv['fields']['cert_name'])
        serv.pop('model')
        id = serv['pk']
        serv.pop('pk')
        serv['fields']['id'] = id
        serv['fields']['cert_status'] = certificate.activation
        list_server.append(serv['fields'])
    return list_server
    

def get_server_openvpn(id):
    """Getting server by id from database"""
    server_openvpn = ServerOpenvpn.objects.filter(pk=id)
    server_openvpnDict = serializers.serialize("json", server_openvpn)
    res = json.loads(server_openvpnDict)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    certificate = Certificate.objects.get(name=res[0]['fields']['cert_name'])
    res[0]['fields']['cert_status'] = certificate.activation
    return res[0]['fields']


def get_all_client_openvpn():
    """Getting all clients from database"""
    list_client = []
    client = ClientOpenvpn.objects.all()
    clientDict = serializers.serialize("json",client)
    res = json.loads(clientDict)
    for cli in res:
        cli.pop('model')
        id = cli['pk']
        cli.pop('pk')
        cli['fields']['id'] = id
        list_client.append(cli['fields'])
    return list_client


def get_client_openvpn(id):
    """Getting client by id from database"""
    client_openvpn = ClientOpenvpn.objects.filter(pk=id)
    client_openvpn = serializers.serialize("json", client_openvpn)
    res = json.loads(client_openvpn)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    certificate = Certificate.objects.get(name=res[0]['fields']['cert_name'])
    res[0]['fields']['cert_status'] = certificate.activation
    return res[0]['fields']
