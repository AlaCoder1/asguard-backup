import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from backend.network.models import Interface
from backend.vlan.functions import add_vlan_sys
from backend.vlan.models import Vlan
from django.core import serializers
from backend.vlan.serializers import VlanSerializer
# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_vlan(request):
    """API to get all vlan from database """
    if (request.method == 'GET'):
        # parse the incoming information
        vlan_object=Vlan.objects.all()
        vlan = serializers.serialize("json", vlan_object)
        res = json.loads(vlan)
    return JsonResponse({"response": res})  


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_vlan(request):
    """API to add vlan in database only"""
    if (request.method == 'POST'):
        # parse the incoming information
        data_input=request.data
        vlan_serializer=VlanSerializer(data=data_input)
        if vlan_serializer.is_valid():
            vlan_serializer.save()
            msg="Vlan added Successfully!"
            status=200
        else:
            msg=vlan_serializer.errors
            status=400
    return JsonResponse({"response": msg},status=status)  
    
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_vlan(request,id):
    """API to update vlan in database only"""
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input =request.data
        if Vlan.objects.filter(id=id):
            vlan_object=Vlan.objects.get(id=id)
            vlan_serializer=VlanSerializer(vlan_object,data=data_input)
            if vlan_serializer.is_valid():
                vlan_serializer.save()
                msg="Vlan updated Successfully!"
                status=200
            else:
                msg=vlan_serializer.errors
                status=400
        else:
            msg="Vlan not exist!"
            status=400
    return JsonResponse({"response": msg},status=status)  

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_vlan(request,id):
    """API to delete vlan from database only"""
    if (request.method == 'DELETE'):
        # parse the incoming information
        if Vlan.objects.filter(id=id):
            vlan_object=Vlan.objects.get(id=id)
            vlan_object.delete()
            msg="Vlan deleted Successfully!"
            status=200
        else:
            msg="Vlan not exist!"
            status=400
    return JsonResponse({"response": msg},status=status)  

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def assign_vlan_interface(request):
    """API to assign vlan to interface"""
    if (request.method == 'POST'):
        # parse the incoming information
        data_input =request.data
        id_vlan = None if data_input.get('id', None) == "" else data_input.get('id', None)
        if Vlan.objects.filter(id=id_vlan):
            vlan_object=Vlan.objects.get(id=id_vlan)
            vlan = serializers.serialize("json", [vlan_object])
            res_vlan = json.loads(vlan)[0]['fields']
            print(res_vlan)
            parent_interface=Interface.objects.get(id=res_vlan["parent_interface"]).ifname
            vlan_tag=res_vlan["vlan_tag"]
            vlan_priority=res_vlan["vlan_priority"]
            aux_add=add_vlan_sys(parent_interface,vlan_tag,vlan_priority)      
            if aux_add is True:
                msg=res_vlan
                status=200
            else:
                msg=aux_add
                status=400
                
     
        else:
            msg="Vlan not exist!"
            status=400
    return JsonResponse({"response": msg},status=status)  