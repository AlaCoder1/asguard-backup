import json
from backend.network.models import Interface
from backend.server_dhcp4.models import ServerDhcp4
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
            res[i]['fields']['name_interface']=Interface.objects.get(id=res[i]['fields']['parent_interface']).name_interface
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
            vlan_tag=res[i]['fields']['ifname'].split("@")[0].strip("vlan").strip()
            interface=Vlan.objects.get(vlan_tag=vlan_tag).parent_interface_id
            id_vlan=Vlan.objects.get(vlan_tag=vlan_tag).id
            ifname_parent=Interface.objects.get(id=interface).ifname      
            data={
                "id":res[i]['pk'],
                "id_vlan":id_vlan,
                "name_interface":res[i]['fields']['name_interface'],
                "network_port":f"VLAN {vlan_tag} on {ifname_parent}"
            }
            list_vlan_interface.append(data)
    return list_vlan_interface

def get_all_server_dhcp4(request):
    """API to get all dhcp4 server from database """
    if (request.method == 'GET'):
        list_dhcp4_server=[]
        # parse the incoming information
        dhcp4_object=ServerDhcp4.objects.all()
        dhcp4 = serializers.serialize("json", dhcp4_object)
        res = json.loads(dhcp4)
        for i in range(len(res)):
            res[i]['fields']['id']=res[i]["pk"]
            res[i]['fields']['range_from']=res[i]['fields']['range_from'].split(',') if res[i]['fields']['range_from'] is not None else None
            res[i]['fields']['range_to']=res[i]['fields']['range_to'].split(',') if res[i]['fields']['range_to'] is not None else None
            res[i]['fields']['dns_server']=res[i]['fields']['dns_server'].split(',') if res[i]['fields']['dns_server'] is not None else None
            res[i]['fields']['name_interface']=Interface.objects.get(id=res[i]['fields']['interface']).name_interface
            list_dhcp4_server.append(res[i]['fields'])
    return list_dhcp4_server