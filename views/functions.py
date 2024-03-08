import json
from backend.network.models import Interface
from backend.vlan.models import Vlan
from django.core import serializers


def get_vlan(request):
    """API to get all vlan from database """
    if (request.method == 'GET'):
        list_vlan=[]
        # parse the incoming information
        vlan_object=Vlan.objects.all()
        vlan = serializers.serialize("json", vlan_object)
        res = json.loads(vlan)
        for i in range(len(res)):
            res[i]['fields']['id']=res[i]["pk"]
            list_vlan.append(res[i]['fields'])
    return list_vlan

def get_vlan_interface(request):
    """API to get all vlan assigned from database """
    if (request.method == 'GET'):
        list_vlan_interface=[]
        # parse the incoming information
        vlan_object = Interface.objects.filter(ifname__startswith='vlan')
        vlans = serializers.serialize("json", vlan_object)
        res = json.loads(vlans)
        for i in range(len(res)):
            vlan_tag=res[i]['fields']['ifname'].strip("vlan")
            interface=Vlan.objects.get(vlan_tag=vlan_tag).parent_interface_id
            ifname_parent=Interface.objects.get(id=interface).ifname      
            data={
                "id":res[i]['pk'],
                "name_interface":res[i]['fields']['name_interface'],
                "network_port":f"VLAN {vlan_tag} on {ifname_parent}"
            }
            list_vlan_interface.append(data)
    return list_vlan_interface