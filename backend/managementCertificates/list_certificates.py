import json
import os

from backend.managementCertificates.constant_variables import PATH_CA_KEY, PATH_CLIENT_CERT_KEY, PATH_SERVER_CERT_KEY
from backend.managementCertificates.models import Certificate, CertificateAuthority

from django.core import serializers


def get_list_all_cert_auth():
    """Getting all Certificates Authority from database"""
    list_ca = []
    ca = CertificateAuthority.objects.all()
    ca_dict = serializers.serialize("json",ca)
    res = json.loads(ca_dict)
    for i in range(len(res)):
        list_certs_auth_by_ca = len(Certificate.objects.filter(certificate_authority=ca[i].pk))
        list_revoke_ca = Certificate.objects.filter(certificate_authority=ca[i].pk, activation=False)
        list_revokation = []
        for revoke in list_revoke_ca:
            list_revokation.append({"id": revoke.id,
                                    "name": revoke.name,
                                    "reason": revoke.reason_revocation})
        res[i]['fields']['is_private_key'] = True
        if not os.path.exists(PATH_CA_KEY.format(ca[i].name)):
            res[i]['fields']['is_private_key'] = False
        res[i].pop('model')
        id_ca = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id_ca
        res[i]['fields']['certificates'] = list_certs_auth_by_ca
        res[i]['fields']['list_revokation'] = list_revokation
        # Send a boolean variable to test the existance of private key
        res[i]['fields']['is_private_key'] = True
        if not os.path.exists(PATH_CA_KEY.format(ca[i].name)):
            res[i]['fields']['is_private_key'] = False
        list_ca.append(res[i]['fields'])
    return list_ca


def get_one_cert_auth(id):
    """Getting a Certificates Authority by id from database"""
    try:
        CertificateAuthority.objects.get(pk=id)
    except CertificateAuthority.DoesNotExist:
        return False
    ca = CertificateAuthority.objects.filter(pk=id)
    ca_dict = serializers.serialize("json", ca)
    res = json.loads(ca_dict)
    list_certs_auth_by_ca = len(Certificate.objects.filter(certificate_authority=ca[0].pk))
    list_revoke_ca = Certificate.objects.filter(certificate_authority=ca[0].pk, activation=False)
    list_revokation = []
    for revoke in list_revoke_ca:
        list_revokation.append({"id": revoke.id,
                                "name": revoke.name,
                                "reason": revoke.reason_revocation})
    res[0]['fields']['is_private_key'] = True
    if not os.path.exists(PATH_CA_KEY.format(ca[0].name)):
        res[0]['fields']['is_private_key'] = False
    res[0].pop('model')
    id_ca = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id_ca
    res[0]['fields']['certificates'] = list_certs_auth_by_ca
    res[0]['fields']['list_revokation'] = list_revokation
    # Send a boolean variable to test the existance of private key
    res[0]['fields']['is_private_key'] = True
    if not os.path.exists(PATH_CA_KEY.format(ca[0].name)):
        res[0]['fields']['is_private_key'] = False
    return res[0]['fields']


def get_list_all_certificates():
    """Getting all Certificates from database"""
    list_cert = []
    cert = Certificate.objects.all()
    cert_dict = serializers.serialize("json",cert)
    res = json.loads(cert_dict)
    for i in range(len(res)):
        res[i].pop('model')
        id_cert = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id_cert
        # Send a boolean variable to test the existance of private key
        res[i]['fields']['is_private_key'] = True
        if cert[i].certificate_type == 'server':
            path_private_key = PATH_SERVER_CERT_KEY.format(cert[i].name)
        else:
            path_private_key = PATH_CLIENT_CERT_KEY.format(cert[i].name)
        if not os.path.exists(path_private_key):
            res[i]['fields']['is_private_key'] = False
        list_cert.append(res[i]['fields'])
    return list_cert


def get_one_certificate(id):
    """Getting a Certificate by id from database"""
    try:
        Certificate.objects.get(pk=id)
    except Certificate.DoesNotExist:
        return False
    cert = Certificate.objects.filter(pk=id)
    cert_dict = serializers.serialize("json", cert)
    res = json.loads(cert_dict)
    res[0].pop('model')
    res[0]['fields']['id'] = res[0].pop('pk')
    # Send a boolean variable to test the existance of private key
    res[0]['fields']['is_private_key'] = True
    if cert[0].certificate_type == 'server':
        path_private_key = PATH_SERVER_CERT_KEY.format(cert[0].name)
    else:
        path_private_key = PATH_CLIENT_CERT_KEY.format(cert[0].name)
    if not os.path.exists(path_private_key):
        res[0]['fields']['is_private_key'] = False
    return res[0]['fields']
