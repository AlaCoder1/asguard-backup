from django.http import JsonResponse
import json
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .service_openvpn import *
from .models import *
from .serializers import *
from django.core import serializers
# Create your views here.
@api_view(['GET'])
@permission_classes([])
def getAllOpenvpns(request):
    list_openvpn = []
    if (request.method == 'GET'):
        openvpn = ServerOpenvpn.objects.all()
        openvpnDict = serializers.serialize("json",openvpn)
        res = json.loads(openvpnDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_openvpn.append(res[i]['fields'])
        return JsonResponse(list_openvpn, safe=False)
    

def find_word_in_line(line, word):
    index = line.find(word)
    if index != -1:
        rest_of_line = line[index + len(word):].strip()
        return rest_of_line
    return ''
def find_word_in_table(table, word):
    for row in table:
        if word in row:
            index = row.index(word)
            rest_of_line = row[index + len(word):]
            return rest_of_line
    return ''   

#function to update interface tables  
def update_openvpn_table(id,data,ServerOpenvpnSerializer):
    objectConfig=ServerOpenvpn.objects.get(id=id)
    # Set all attributes to None
    for field in objectConfig._meta.fields:
        if field.attname not in ["id"]: 
            setattr(objectConfig, field.attname, None)
    serializerServerOpenvpn= ServerOpenvpnSerializer(objectConfig,data=data)
    if serializerServerOpenvpn.is_valid():
            serializerServerOpenvpn.save()    
@api_view(['PUT'])
@permission_classes([AllowAny])
def updateOpenVPN(request,id):
    msg=''
    if (request.method == 'PUT'):
        # parse the incoming information
        data = JSONParser().parse(request)
        port = data.get('port', '')
        proto = data.get('proto', '')
        dev = data.get('dev', '')
        user = data.get('user', '')
        group = data.get('group', '')
        persist_key = data.get('persist_key', '')
        persist_tun = data.get('persist_tun', '')
        keepalive = data.get('keepalive', '')
        topology = data.get('topology', '')
        server = data.get('server', '')
        ifconfig_pool_persist = data.get('ifconfig_pool_persist', '')
        push_ipv4_option1 = data.get('push_ipv4_option1', '')
        push_ipv4_option2 = data.get('push_ipv4_option2', '')
        push_ipv4_option3 = data.get('push_ipv4_option3', '')
        server_ipv6 = data.get('port', '')
        tun_ipv6 = data.get('tun_ipv6', '')
        push_ipv6_option1 = data.get('push_ipv6_option1', '')
        push_ipv6_option2 = data.get('push_ipv6_option2', '')
        push_ipv6_option3 = data.get('push_ipv6_option3', '')
        dh = data.get('dh', '')
        ecdh_curve = data.get('ecdh_curve', '')
        tls_crypt = data.get('tls_crypt', '')
        crl_verify = data.get('crl_verify', '')
        ca = data.get('ca', '')
        cert = data.get('cert', '')
        key = data.get('key', '')
        auth = data.get('auth', '')
        cipher = data.get('cipher', '')
        ncp_ciphers = data.get('ncp_ciphers', '')
        tls_server = data.get('tls_server', '')
        tls_version_min = data.get('tls_version_min', '')
        tls_cipher = data.get('tls_cipher', '')
        client_config_dir = data.get('port', '')
        status = data.get('status', '')
        verb = data.get('verb', '')
        server_path = "/etc/openvpn/server.conf"
        new_server_conf = f"""
port {port}
proto {proto}
dev {dev}
user {user}
group {group}
persist-key {persist_key}
persist-tun {persist_tun}
keepalive {keepalive}
topology {topology}
server {server}
ifconfig_pool_persist {ifconfig_pool_persist}
push "{push_ipv4_option1}"
push "{push_ipv4_option2}"
push "{push_ipv4_option3}"
dh {dh}
ecdh-curve {ecdh_curve}
tls-crypt {tls_crypt}
crl-verify {crl_verify}
ca {ca}
cert {cert}
key {key}
auth {auth}
cipher {cipher}
ncp-ciphers {ncp_ciphers}
tls-server {tls_server}
tls-version-min {tls_version_min}
tls-cipher {tls_cipher}
client-config-dir {client_config_dir}
status {status}
verb {verb}"""
        # print(data)
        stdin, stdout, stderr = add_config_server(server_path, new_server_conf)
        if stderr.read().decode('utf-8') == "":
            # update_openvpn_table(id,data,ServerOpenvpnSerializer)
            obj = ServerOpenvpn.objects.get(id=id)
            serializer = ServerOpenvpnSerializer(obj, data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                msg="done"
            else:
                msg = serializer.errors
        else:
            msg=stderr.read().decode('utf-8')
        return JsonResponse({"msg":msg})