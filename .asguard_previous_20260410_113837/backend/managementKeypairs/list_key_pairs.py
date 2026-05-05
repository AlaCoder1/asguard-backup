import json
from django.core import serializers
from backend.ipsec.constant_variables import PATH_IPSEC_D_CERTS

from backend.managementKeypairs.models import PrivateKey, PublicKey


def get_list_all_private_key():
    list_private_key = []
    private_key = PrivateKey.objects.all()
    private_key_dict = serializers.serialize("json", private_key)
    res = json.loads(private_key_dict)
    for priv_key in res:
        priv_key.pop('model')
        priv_key_id = priv_key['pk']
        priv_key.pop('pk')
        priv_key['fields']['id'] = priv_key_id
        list_private_key.append(priv_key['fields'])
    
    return list_private_key


def get_one_private_key(id):
    private_key = PrivateKey.objects.filter(pk=id)
    private_key_dict = serializers.serialize("json", private_key)
    res = json.loads(private_key_dict)
    res[0].pop('model')
    private_key_id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = private_key_id
    return res[0]['fields']


def get_list_all_public_key():
    list_public_key = []
    public_key = PublicKey.objects.all()
    public_key_dict = serializers.serialize("json", public_key)
    res = json.loads(public_key_dict)
    for pub_key in res:
        pub_key.pop('model')
        pub_key_id = pub_key['pk']
        pub_key.pop('pk')
        pub_key['fields']['id'] = pub_key_id

        # Send public key value
        with open(f'{PATH_IPSEC_D_CERTS}{pub_key["fields"]["name"]}.pem') as public_key_file:
            pub_key['fields']['public_key_value'] = public_key_file.read()
        list_public_key.append(pub_key['fields'])
    
    return list_public_key


def get_one_public_key(id):
    public_key = PublicKey.objects.filter(pk=id)
    public_key_dict = serializers.serialize("json", public_key)
    res = json.loads(public_key_dict)
    res[0].pop('model')
    public_key_id = res[0]['pk']
    res[0].pop('pk')
    res[0]['fields']['id'] = public_key_id

    # Send public key value
    with open(f'{PATH_IPSEC_D_CERTS}{res[0]["fields"]["name"]}.pem') as public_key_file:
        res[0]['fields']['public_key_value'] = public_key_file.read()

    return res[0]['fields']
