import json

from backend.managementCertificates.models import Certificate, CertificateAuthority

from django.core import serializers


def get_list_all_cert_auth():
    """Getting all Certificates Authority from database"""
    list_ca = []
    ca = CertificateAuthority.objects.all()
    caDict = serializers.serialize("json",ca)
    res = json.loads(caDict)
    for i in range(len(res)):
        list_certs_auth_by_ca = len(Certificate.objects.filter(certificate_authority=ca[i].pk))
        list_revoke_ca = Certificate.objects.filter(certificate_authority=ca[i].pk, activation=False)
        list_revokation = []
        for revoke in list_revoke_ca:
            list_revokation.append({"id": revoke.id,
                                    "name": revoke.name,
                                    "reason": revoke.reason_revocation})
        res[i].pop('model')
        id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id
        res[i]['fields']['certificates'] = list_certs_auth_by_ca
        res[i]['fields']['list_revokation'] = list_revokation
        list_ca.append(res[i]['fields'])
    return list_ca


def get_one_cert_auth(id):
    """Getting a Certificates Authority by id from database"""
    ca = CertificateAuthority.objects.filter(pk=id)
    caDict = serializers.serialize("json", ca)
    res = json.loads(caDict)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    return res[0]['fields']


def get_list_all_certificates():
    """Getting all Certificates from database"""
    list_cert = []
    cert = Certificate.objects.all()
    certDict = serializers.serialize("json",cert)
    res = json.loads(certDict)
    for i in range(len(res)):
        res[i].pop('model')
        id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = id
        list_cert.append(res[i]['fields'])
    return list_cert


def get_one_certificate(id):
    """Getting a Certificate by id from database"""
    cert = Certificate.objects.filter(pk=id)
    certDict = serializers.serialize("json", cert)
    res = json.loads(certDict)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    return res[0]['fields']
