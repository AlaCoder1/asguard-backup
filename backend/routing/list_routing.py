from django.core import serializers
import json

from backend.gateway.models import Gateway, GatewayInterface
from backend.routing.models import Routing


def get_list_all_routing():
    """Getting all routing from database"""
    list_routing = []
    routings = Routing.objects.all()
    routing_dict = serializers.serialize("json", routings)
    res = json.loads(routing_dict)
    for routing in res:
        routing_id = routing['pk']
        routing['fields']['id'] = routing_id
        routing['fields']['gateway_name'] = Routing.objects.get(id=routing_id).gateway.gwname
        list_routing.append(routing['fields'])
    return list_routing


def get_one_routing(id):
    """Getting routing by id from database"""
    routing = Routing.objects.filter(pk=id)
    routing_dict = serializers.serialize("json", routing)
    res = json.loads(routing_dict)
    routing_id = res[0]['pk']
    res[0]['fields']['id'] = routing_id
    res[0]['fields']['gateway_name'] = Routing.objects.get(id=routing_id).gateway.gwname
    return res[0]['fields']


def get_list_all_gateway():
    """Getting all gateway from database"""
    list_gateway = []
    gateways = Gateway.objects.all()
    gateway_dict = serializers.serialize("json", gateways)
    res = json.loads(gateway_dict)
    for gateway in res:
        gateway_id = gateway['pk']
        gateway['fields']['id'] = gateway_id
        if len(GatewayInterface.objects.filter(gateway=Gateway.objects.get(id=gateway_id))) > 0:
            list_gateway.append(gateway['fields'])
    return list_gateway


def get_one_gateway(id):
    """Getting gateway by id from database"""
    gateway = Gateway.objects.filter(pk=id)
    gateway_dict = serializers.serialize("json", gateway)
    res = json.loads(gateway_dict)
    gateway_id = res[0]['pk']
    res[0]['fields']['id'] = gateway_id
    if len(GatewayInterface.objects.filter(gateway=Gateway.objects.get(id=gateway_id))) > 0:
        return res[0]['fields']
