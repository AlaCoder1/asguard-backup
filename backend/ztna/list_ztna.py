from backend.ztna.models import Identities, Relays, Services, RelaysPolicy,ServicesPolicy, ServicesRelaysPolicy, InterceptConfigs, HostConfigs
from backend.ztna.utils import get_data, get_local_domain_from_system
from django.core import serializers
import json


def get_identities():
    list_identities = []
    identities = Identities.objects.all()

    # Synchronize identites in system with database
    try:
        endpoint = "identities/"
        identities_from_ziti=get_data(endpoint)
        for identity in identities:
            matching_ziti_identity = next((z for z in identities_from_ziti if z['id'] == identity.ref_identitie), None)        
            if matching_ziti_identity and 'envInfo' in matching_ziti_identity and 'hostname' in matching_ziti_identity['envInfo']:
                new_hostname = matching_ziti_identity['envInfo']['hostname']
                identity.hostname = new_hostname
                identity.token = None           
                identity.save()
    except Exception:
        pass

    identitie_dict = serializers.serialize("json", identities)
    res = json.loads(identitie_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        identitie_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = identitie_id
        list_identities.append(res[i]['fields'])
    return list_identities


def get_routers():
    list_relays = []
    relays = Relays.objects.all()

    # Synchronize routers in system with database
    try:
        endpoint = "edge-routers/"
        routers_from_ziti=get_data(endpoint)
        for relay in relays:
            matching_ziti_relay = next((z for z in routers_from_ziti if z['id'] == relay.ref_relay), None)
            relay.online = matching_ziti_relay['isOnline']
            relay.verified = matching_ziti_relay['isVerified']           
            relay.save()
    except Exception:
        pass

    relays_dict = serializers.serialize("json", relays)
    res = json.loads(relays_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        relay_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = relay_id
        list_relays.append(res[i]['fields'])
    return list_relays


def get_intercept_configs():
    list_intercept = []
    intercept = InterceptConfigs.objects.all()
    intercept_dict = serializers.serialize("json", intercept)
    res = json.loads(intercept_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        relay_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = relay_id
        list_intercept.append(res[i]['fields'])
    return list_intercept


def get_host_configs():
    list_host = []
    host = HostConfigs.objects.all()
    host_dict = serializers.serialize("json", host)
    res = json.loads(host_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        relay_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = relay_id
        list_host.append(res[i]['fields'])
    return list_host


def get_services():
    list_services = []
    services = Services.objects.all()
    services_dict = serializers.serialize("json", services)
    res = json.loads(services_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        relay_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = relay_id
        list_services.append(res[i]['fields'])
    return list_services


def get_edge_router_policies():
    list_relay_policies = []
    relay_policy = RelaysPolicy.objects.all()
    relay_policy_dict = serializers.serialize("json", relay_policy)
    res = json.loads(relay_policy_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        relay_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = relay_id
        list_relay_policies.append(res[i]['fields'])
    return list_relay_policies


def get_service_policies():
    list_services_policies = []
    service_policy = ServicesPolicy.objects.all()
    service_policy_dict = serializers.serialize("json", service_policy)
    res = json.loads(service_policy_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        relay_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = relay_id
        list_services_policies.append(res[i]['fields'])
    return list_services_policies


def get_service_edge_router_policies():
    list_services_relays_policies = []
    service_relay_policy = ServicesRelaysPolicy.objects.all()
    service_relay_policy_dict = serializers.serialize("json", service_relay_policy)
    res = json.loads(service_relay_policy_dict)
    for i in range(0, len(res)):
        res[i].pop('model')
        relay_id = res[i]['pk']
        res[i].pop('pk')
        res[i]['fields']['id'] = relay_id
        list_services_relays_policies.append(res[i]['fields'])
    return list_services_relays_policies


def get_local_domain(os="linux"):
    """Get the local domain for linux os"""

    file_content = get_local_domain_from_system(os)

    if file_content:
        content_dict = {
            'os': os,
            'content': file_content
        }
        return [content_dict]
    return []
