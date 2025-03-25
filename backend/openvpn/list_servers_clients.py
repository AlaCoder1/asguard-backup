import json
from django.core import serializers
from backend.managementCertificates.models import Certificate
from backend.openvpn.constant_variables import PATH_CLIENT_STATIC, PATH_SERVER_STATIC

from backend.openvpn.models import ClientOpenvpn, ServerOpenvpn
from backend.openvpn.servers_status import synchronize_server_openvpn
from utils.commands_utils import read_file_from_system


def get_list_all_server_openvpn():
    """Getting all servers from database"""
    synchronize_server_openvpn()

    list_server = []
    server = ServerOpenvpn.objects.all()
    server_dict = serializers.serialize("json",server)
    res = json.loads(server_dict)
    for serv in res:
        serv.pop('model')
        serv_id = serv['pk']
        serv.pop('pk')
        serv['fields']['id'] = serv_id
        serv['fields']['client_management_password'] = ''
        try:
            certificate = Certificate.objects.get(name=serv['fields']['cert_name'])
            cert_status = certificate.activation
        except Certificate.DoesNotExist:
            cert_status = False
        serv['fields']['cert_status'] = cert_status
        # Add the TLS content of the server
        serv['fields']['tls_key'] = read_file_from_system(PATH_SERVER_STATIC.format(serv["fields"]["name"]))
        list_server.append(serv['fields'])
    return list_server


def get_one_server_openvpn(id):
    """Getting server by id from database"""
    server_openvpn = ServerOpenvpn.objects.filter(pk=id)
    server_openvpn_dict = serializers.serialize("json", server_openvpn)
    res = json.loads(server_openvpn_dict)
    res[0].pop('model')
    serv_id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = serv_id
    res[0]['fields']['client_management_password'] = ''
    certificate = Certificate.objects.get(name=res[0]['fields']['cert_name'])
    res[0]['fields']['cert_status'] = certificate.activation
    # Add the TLS content of the server
    res[0]['fields']['tls_key'] = read_file_from_system(PATH_SERVER_STATIC.format(res[0]["fields"]["name"]))
    return res[0]['fields']


def get_list_all_client_openvpn():
    """Getting all clients from database"""
    list_client = []
    client = ClientOpenvpn.objects.all()
    client_dict = serializers.serialize("json",client)
    res = json.loads(client_dict)
    for cli in res:
        cli.pop('model')
        client_id = cli['pk']
        cli.pop('pk')
        cli['fields']['id'] = client_id
        cli['fields']['proxy_auth_password'] = ''
        cli['fields']['password'] = ''
        try:
            certificate = Certificate.objects.get(name=cli['fields']['cert_name'])
            cert_status = certificate.activation
        except Certificate.DoesNotExist:
            cert_status = False
        cli['fields']['cert_status'] = cert_status
        cli['fields']['tls_key'] = read_file_from_system(PATH_CLIENT_STATIC.format(cli["fields"]["name"]))
        list_server_remote = list(cli['fields']['server_remote'].split(','))
        cli['fields']['server_remote'] = []
        for server in list_server_remote:
            cli['fields']['server_remote'].append({'host': server[:server.find(':')],
                                                   'port': server[server.find(':')+1:]})
        list_client.append(cli['fields'])
    return list_client


def get_one_client_openvpn(id):
    """Getting client by id from database"""
    client_openvpn = ClientOpenvpn.objects.filter(pk=id)
    client_openvpn = serializers.serialize("json", client_openvpn)
    res = json.loads(client_openvpn)
    res[0].pop('model')
    client_id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = client_id
    res[0]['fields']['proxy_auth_password'] = ''
    res[0]['fields']['password'] = ''
    certificate = Certificate.objects.get(name=res[0]['fields']['cert_name'])
    res[0]['fields']['cert_status'] = certificate.activation
    res[0]['fields']['tls_key'] = read_file_from_system(PATH_CLIENT_STATIC.format(res[0]["fields"]["name"]))
    list_server_remote = list(res[0]['fields']['server_remote'].split(','))
    res[0]['fields']['server_remote'] = []
    for server in list_server_remote:
        res[0]['fields']['server_remote'].append({'host': server[:server.find(':')],
                                                  'port': server[server.find(':')+1:]})
    return res[0]['fields']
