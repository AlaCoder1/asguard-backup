from django.shortcuts import render
import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from backend.network.models import Interface
from backend.network.serializers import InterfaceSerializer
from backend.vxlan.functions import add_vxlan_sys, get_all_nmcli_uuids,save_in_db
from backend.vxlan.models import Vxlan
from django.core import serializers
from django.utils.translation import gettext_lazy as _
from backend.vxlan.serializers import VxlanSerializer


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_vxlan(request):
    """API to get all vxlan from database """
    if (request.method == 'GET'):
        list_vxlan=[]
        # parse the incoming information
        vxlan_object=Vxlan.objects.all()
        vxlan = serializers.serialize("json", vxlan_object)
        res = json.loads(vxlan)
        for i in range(len(res)):
            res[i]['fields']['id']=res[i]["pk"]
            res[i]['fields']['name_interface']=Interface.objects.get(id=res[i]['fields']['parent_interface']).name_interface
            list_vxlan.append(res[i]['fields'])
    return JsonResponse({"msg": list_vxlan})  


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_vxlan(request):
    """API to add vlan in database only"""
    if (request.method == 'POST'):
        # parse the incoming information
        data_input=request.data
        vxlan_serializer=VxlanSerializer(data=data_input)
        if vxlan_serializer.is_valid():
            vxlan_serializer.save()
            msg= "Vxlan Added successfully"
            status=200
        else:
            msg=str(next(iter(vxlan_serializer.errors.values()))[0]).strip('.')+"!"
            status=400
    return JsonResponse({"msg": msg},status=status)  
    

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def assign_vxlan_interface(request):
    """API to assign vxlan to interface  and create new interface of vxlan to configure it """
    if (request.method == 'POST'):
        data_input =request.data
        interface_name=data_input["ifname"]
        if Vxlan.objects.filter(vxlan_connection_uuid=interface_name).exists():
            vxlan_object=Vxlan.objects.get(vxlan_connection_uuid=interface_name)
            vxlan = serializers.serialize("json", [vxlan_object])
            res_vxlan = json.loads(vxlan)[0]['fields']
            parent_interface=Interface.objects.get(id=res_vxlan["parent_interface"]).ifname
            vxlan_id=res_vxlan["vxlan_id"]
            vxlan_interface_name=res_vxlan["vxlan_interface_name"]
            vxlan_source_address=res_vxlan["vxlan_source_address"]
            vxlan_destination_address=res_vxlan["vxlan_destination_address"]
            vxlan_destination_port=res_vxlan["vxlan_destination_port"]
            vxlan_connection_uuid=res_vxlan["vxlan_connection_uuid"]
             
            data_save={
                        "ifname":data_input["ifname"],
                        "private_aux":False,
                        "bogon_aux":False,
                        "name_interface":data_input['name_interface'],
                        "description":f"test default config vxlan {vxlan_id}"
                    }
            if not Interface.objects.filter(ifname=vxlan_interface_name).exists():
                aux_save=add_vxlan_sys(parent_interface,vxlan_id,vxlan_interface_name,vxlan_source_address,vxlan_destination_address,vxlan_destination_port,vxlan_connection_uuid)
                if aux_save is True:
                    interface_serializer=InterfaceSerializer(data=data_save)
                    msg,status=save_in_db(aux_save,interface_serializer)
                else:
                    msg=aux_save
                    status=400
            else:
                msg= "Vxlan interface already exist"
                status=400
        else:
            msg="Vxlan interface not exist"
            status=400
    return JsonResponse({"msg": msg},status=status)  