import json
from django.core import serializers

from backend.managementKeypairs.models import PrivateKey, PublicKey


def get_list_all_private_key():
    list_private_key = []
    private_key = PrivateKey.objects.all()
    caDict = serializers.serialize("json", private_key)
    res = json.loads(caDict)
    for priv_key in res:
        priv_key.pop('model')
        id = priv_key['pk']
        priv_key.pop('pk')
        priv_key['fields']['id'] = id
        list_private_key.append(priv_key['fields'])
    
    return list_private_key


def get_one_private_key(id):
    private_key = PrivateKey.objects.filter(pk=id)
    private_keyDict = serializers.serialize("json", private_key)
    res = json.loads(private_keyDict)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    return res[0]['fields']


def get_list_all_public_key():
    list_public_key = []
    public_key = PublicKey.objects.all()
    caDict = serializers.serialize("json", public_key)
    res = json.loads(caDict)
    for pub_key in res:
        pub_key.pop('model')
        id = pub_key['pk']
        pub_key.pop('pk')
        pub_key['fields']['id'] = id
        list_public_key.append(pub_key['fields'])
    
    return list_public_key


def get_one_public_key(id):
    public_key = PublicKey.objects.filter(pk=id)
    public_keyDict = serializers.serialize("json", public_key)
    res = json.loads(public_keyDict)
    res[0].pop('model')
    id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = id
    return res[0]['fields']
