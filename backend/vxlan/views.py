from django.shortcuts import render
import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from backend.network.models import Interface
from backend.network.serializers import InterfaceSerializer
from backend.vxlan.functions import add_vxlan_sys, delete_vxlan_sys, get_all_nmcli_uuids,save_in_db, update_vxlan_sys
from backend.vxlan.models import Vxlan
from django.core import serializers
from django.utils.translation import gettext_lazy as _
from backend.vxlan.serializers import VxlanSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# Constants
CONSTANT_VXLAN_CONFIG = _('Configuration VxLAN')
CONSTANT_VXLAN_INTERFACE = _('Interface VxLAN')

# Success messages
SUCCESS_MESSAGES_SAVED = _("Saved")
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")


# Error messages
ERROR_MESSAGES_EXISTANT = _("Already exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")




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

@swagger_auto_schema(
    method='POST',
    request_body=VxlanSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD VXLAN",
    operation_description="This API add VXLAN with their caracteristique in database",
)
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
            msg= f"{CONSTANT_VXLAN_CONFIG} {SUCCESS_MESSAGES_CREATING}"
            status=200
        else:
            msg=str(next(iter(vxlan_serializer.errors.values()))[0]).strip('.')+"!"
            status=400
    return JsonResponse({"msg": msg},status=status)  
 
 
@swagger_auto_schema(
    method='PUT',
    request_body=VxlanSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD VXLAN",
    operation_description="This API add VXLAN with their caracteristique in database",
)     
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_vxlan(request,id):
    """API to update vlan in system and database"""
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input =request.data
        if Vxlan.objects.filter(id=id).exists():
            vlan_object=Vxlan.objects.get(id=id)
            vlan_serializer=VxlanSerializer(vlan_object,data=data_input)
            if vlan_serializer.is_valid():
                old_vxlan=vlan_object.vxlan_interface_name
                old_vxlan_id=vlan_object.vxlan_connection_uuid
                ##new attributs
                parent_interface=Interface.objects.get(id=data_input['parent_interface']).ifname
                vxlan_id=data_input['vxlan_id']
                vxlan_interface_name=data_input['vxlan_interface_name']
                vxlan_source_address=data_input['vxlan_source_address']
                vxlan_destination_address=data_input['vxlan_destination_address']
                vxlan_destination_port=data_input['vxlan_destination_port']
                vxlan_connection_uuid=data_input['vxlan_connection_uuid']
                if Interface.objects.filter(ifname=old_vxlan).exists(): 
                    interface_object=Interface.objects.get(ifname=old_vxlan)
                    aux_save=update_vxlan_sys(old_vxlan_id,parent_interface,vxlan_id,vxlan_interface_name,vxlan_source_address,vxlan_destination_address,vxlan_destination_port,vxlan_connection_uuid) 
                    data_save={
                        "ifname":f"{vxlan_interface_name}",
                        "private_aux":False,
                        "bogon_aux":False,
                        "description":f"update default config {vxlan_interface_name}",
                        }
                    if aux_save:
                        interface_serializer=InterfaceSerializer(interface_object,data=data_save)
                        msg,status=save_in_db(aux_save,interface_serializer)
                        
                    else:
                        msg=aux_save
                        status=400
                else:
                    msg=f"{CONSTANT_VXLAN_CONFIG} {SUCCESS_MESSAGES_SAVED}"
                    status=200
                vlan_serializer.save()
            else:
                msg=str(next(iter(vlan_serializer.errors.values()))[0]).strip('.')+"!"
                status=400
      
        else:
            msg=f"{CONSTANT_VXLAN_CONFIG} {ERROR_MESSAGES_INEXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status) 

@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Deleted', 400: 'Bad Request'},
    operation_summary="API DELETE VXLAN",
    operation_description="This API delete VXLAN by id ",
)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_vxlan(request,id):
    """API to delete vlan from database only"""
    if (request.method == 'DELETE'):
        # parse the incoming information
        if Vxlan.objects.filter(id=id):
            vlan_object=Vxlan.objects.get(id=id)
            vxlan_ifname=vlan_object.vxlan_interface_name
            vxlan_connection=vlan_object.vxlan_connection_uuid
            if Interface.objects.filter(ifname=vxlan_ifname).exists():
                interface_object=Interface.objects.get(ifname=vxlan_ifname)
                aux_delete=delete_vxlan_sys(vxlan_connection,vxlan_ifname)
                if aux_delete:
                    interface_object.delete()
            vlan_object.delete()
            msg=f"{CONSTANT_VXLAN_CONFIG} {SUCCESS_MESSAGES_DELETING}"
            status=200
        else:
            msg=f"{CONSTANT_VXLAN_CONFIG} {ERROR_MESSAGES_INEXISTANT}"
            status=404
    return JsonResponse({"msg": msg},status=status)  

vxlan_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'ifname': openapi.Schema(type=openapi.TYPE_STRING, description='ifname of the VxLAN'),
        'name_interface': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the VxLAN interface')
    },
    required=['ifname', 'name_interface']
)



@swagger_auto_schema(
    method='POST',
    request_body=vxlan_request_schema,
    responses={200: "Created", 400: 'Bad Request'},
    operation_summary="API TO ASSIGN VXLAN Interface",
    operation_description="This API assign a VXLAN with its characteristics to the database and system",
)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def assign_vxlan_interface(request):
    """API to assign vxlan to interface  and create new interface of vxlan to configure it """
    if (request.method == 'POST'):
        data_input =request.data
        interface_name=data_input["ifname"]
        if Vxlan.objects.filter(vxlan_interface_name=interface_name).exists():
            vxlan_object=Vxlan.objects.get(vxlan_interface_name=interface_name)
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
                        "ifname":vxlan_interface_name,
                        "private_aux":False,
                        "bogon_aux":False,
                        "name_interface":f"VXLAN{vxlan_id}",
                        # "description":f"test default config {vxlan_interface_name}"
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
                msg= f"{CONSTANT_VXLAN_INTERFACE} {ERROR_MESSAGES_EXISTANT}"
                status=400
        else:
            msg=f"{CONSTANT_VXLAN_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status)  

vxlan_request_schema_update = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name_interface': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the VxLAN interface')
    },
    required=['name_interface']
)



@swagger_auto_schema(
    method='PUT',
    request_body=vxlan_request_schema_update,
    responses={200: "Created", 400: 'Bad Request'},
    operation_summary="API TO update ASSIGN VXLAN Interface",
    operation_description="This API update assign a VXLAN with its characteristics to the database and system",
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_vxlan_interface(request,id_interface):
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input=request.data
        if Interface.objects.filter(id=id_interface).exists():
            vlan_object=Interface.objects.get(id=id_interface)
            data_save={
                        "ifname":f"{vlan_object.ifname}",
                        "private_aux":False,
                        "bogon_aux":False,
                        "name_interface":f"VXLAN{vlan_object.vxlan_id}",
                    }
            interface_serializer=InterfaceSerializer(vlan_object,data=data_save)
            aux_save=True
            msg,status=save_in_db(aux_save,interface_serializer)
        else:
            msg=f"{CONSTANT_VXLAN_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status)  
   
@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Deleted', 400: 'Bad Request'},
    operation_summary="API DELETE VxLAN interface",
    operation_description="This API delete VxLAN interface by id ",
)    
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_vxlan_interface(request,id_interface):
    if (request.method == 'DELETE'):
        # parse the incoming information
        if Interface.objects.filter(id=id_interface).exists():
            vlan_object=Interface.objects.get(id=id_interface)
            ifname_vxlan=vlan_object.ifname
            vxlan_connection=Vxlan.objects.get(vxlan_interface_name=ifname_vxlan).vxlan_connection_uuid
            aux_delete=delete_vxlan_sys(vxlan_connection,ifname_vxlan)
            if aux_delete:
                vlan_object.delete()
                msg=f"{CONSTANT_VXLAN_INTERFACE} {SUCCESS_MESSAGES_DELETING}"
                status=200
            else:
                msg=aux_delete
                status=400
        else:
            msg=f"{CONSTANT_VXLAN_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"
            status=404
      
    return JsonResponse({"msg": msg},status=status) 


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_vxlan_interface(request):
    """API to get all vlan assigned from database """
    if (request.method == 'GET'):
        list_vlan_interface=[]
        # parse the incoming information
        vlan_object = Interface.objects.filter(name_interface__startswith='VXLAN')
        vlans = serializers.serialize("json", vlan_object)
        res = json.loads(vlans)
        for i in range(len(res)):
            vlan_ifname=res[i]['fields']['ifname']
            interface=Vxlan.objects.get(vxlan_interface_name=vlan_ifname).parent_interface_id
            ifname_parent=Interface.objects.get(id=interface).ifname      
            data={
                "id":res[i]['pk'],
                "name_interface":res[i]['fields']['name_interface'],
                "network_port":f"VXLAN {vlan_ifname} on {ifname_parent}"
            }
            list_vlan_interface.append(data)
    return JsonResponse({"msg": list_vlan_interface})  