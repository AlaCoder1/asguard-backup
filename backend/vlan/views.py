import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from backend.network.models import Interface
from backend.network.serializers import InterfaceSerializer
from backend.vlan.functions import add_vlan_sys, convert_priority, delete_vlan_sys, save_in_db, update_vlan_sys
from backend.vlan.models import Vlan
from django.core import serializers
from django.utils.translation import gettext_lazy as _
from backend.vlan.serializers import VlanSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Constants
CONSTANT_VLAN_CONFIG = _('Configuration VLAN')
CONSTANT_VLAN_INTERFACE = _('Interface VLAN')

# Success messages
SUCCESS_MESSAGES_SAVED = _("Saved")
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")


# Error messages
ERROR_MESSAGES_EXISTANT = _("Already exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
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
    return JsonResponse({"msg": list_vlan})  

@swagger_auto_schema(
    method='POST',
    request_body=VlanSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD VLAN",
    operation_description="This API add VLAN with their caracteristique in database",
)
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
            msg= f"{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_CREATING}"
            status=200
        else:
            msg=str(next(iter(vlan_serializer.errors.values()))[0]).strip('.')+"!"
            status=400
    return JsonResponse({"msg": msg},status=status)  
   
@swagger_auto_schema(
    method='PUT',
    request_body=VlanSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD VLAN",
    operation_description="This API add VLAN with their caracteristique in database",
) 
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_vlan(request,id):
    """API to update vlan in system and database"""
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input =request.data
        if Vlan.objects.filter(id=id).exists():
            vlan_object=Vlan.objects.get(id=id)
            vlan_serializer=VlanSerializer(vlan_object,data=data_input)
            if vlan_serializer.is_valid():
                parent_interface=Interface.objects.get(id=vlan_object.parent_interface_id).ifname
                vlan_tag=vlan_object.vlan_tag
                new_vlan_priority=convert_priority(data_input['vlan_priority']) if data_input["vlan_priority"] is not None else data_input["vlan_priority"]
                new_parent_interface=Interface.objects.get(id=data_input['parent_interface']).ifname
                new_vlan_tag=data_input['vlan_tag']
                if Interface.objects.filter(ifname=f"vlan{vlan_tag}@{parent_interface}").exists(): 
                    interface_object=Interface.objects.get(ifname=f"vlan{vlan_tag}@{parent_interface}")
                    aux_save=update_vlan_sys(interface_object.ifname,new_parent_interface,new_vlan_tag,new_vlan_priority)  
                    data_save={
                        "ifname":f"vlan{new_vlan_tag}@{new_parent_interface}",
                        "private_aux":False,
                        "bogon_aux":False,
                        "description":f"update default config vlan{new_vlan_tag}",
                        }
                    if aux_save:
                        interface_serializer=InterfaceSerializer(interface_object,data=data_save)
                        msg,status=save_in_db(aux_save,interface_serializer)
                        
                    else:
                        msg=aux_save
                        status=400
                else:
                    msg=f"{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_SAVED}"
                    status=200
                vlan_serializer.save()
            else:
                msg=str(next(iter(vlan_serializer.errors.values()))[0]).strip('.')+"!"
                status=400
      
        else:
            msg=f"{CONSTANT_VLAN_CONFIG} {ERROR_MESSAGES_INEXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status) 


@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Deleted', 400: 'Bad Request'},
    operation_summary="API DELETE VLAN",
    operation_description="This API delete VLAN by id ",
)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_vlan(request,id):
    """API to delete vlan from database only"""
    if (request.method == 'DELETE'):
        # parse the incoming information
        if Vlan.objects.filter(id=id):
            vlan_object=Vlan.objects.get(id=id)
            name_interface=Interface.objects.get(id=vlan_object.parent_interface_id).ifname
            if Interface.objects.filter(ifname=f"vlan{vlan_object.vlan_tag}@{name_interface}").exists():
                interface_object=Interface.objects.get(ifname=f"vlan{vlan_object.vlan_tag}@{name_interface}")
                aux_delete=delete_vlan_sys(interface_object.ifname)
                if aux_delete:
                    interface_object.delete()
            vlan_object.delete()
            msg=f"{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_DELETING}"
            status=200
        else:
            msg=f"{CONSTANT_VLAN_CONFIG} {ERROR_MESSAGES_INEXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status) 

vlan_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the VLAN'),
        'name_interface': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the VLAN interface')
    },
    required=['id', 'name_interface']
)



@swagger_auto_schema(
    method='POST',
    request_body=vlan_request_schema,
    responses={200: "Created", 400: 'Bad Request'},
    operation_summary="API TO ASSIGN VLAN Interface",
    operation_description="This API assign a VLAN with its characteristics to the database and system",
)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def assign_vlan_interface(request):
    """API to assign vlan to interface  and create new interface of vlan to configure it """
    if (request.method == 'POST'):
        # parse the incoming information
        data_input =request.data
        id_vlan = None if data_input.get('id', None) == "" else data_input.get('id', None)
        if Vlan.objects.filter(id=id_vlan).exists():
            vlan_object=Vlan.objects.get(id=id_vlan)
            vlan = serializers.serialize("json", [vlan_object])
            res_vlan = json.loads(vlan)[0]['fields']
            parent_interface=Interface.objects.get(id=res_vlan["parent_interface"]).ifname
            vlan_tag=res_vlan["vlan_tag"]
            vlan_priority=convert_priority(res_vlan["vlan_priority"]) if res_vlan["vlan_priority"] is not None else res_vlan["vlan_priority"]
            data_save={
                        "ifname":f"vlan{vlan_object.vlan_tag}@{parent_interface}",
                        "private_aux":False,
                        "bogon_aux":False,
                        "name_interface":data_input['name_interface'],
                        "description":f"test default config vlan {vlan_tag}"
                    }
            if not Interface.objects.filter(ifname=f"vlan{vlan_object.vlan_tag}@{parent_interface}").exists():
                aux_save=add_vlan_sys(parent_interface,vlan_tag,vlan_priority)
                if aux_save is True:
                    interface_serializer=InterfaceSerializer(data=data_save)
                    msg,status=save_in_db(aux_save,interface_serializer)
                else:
                    msg=aux_save
                    status=400
            else:
                msg=f"{CONSTANT_VLAN_INTERFACE} {ERROR_MESSAGES_EXISTANT}"
                status=400
        else:
            msg=f"{CONSTANT_VLAN_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status)  


vlan_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the VLAN'),
        'name_interface': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the VLAN interface')
    },
    required=['id', 'name_interface']
)



@swagger_auto_schema(
    method='PUT',
    request_body=vlan_request_schema,
    responses={200: "Created", 400: 'Bad Request'},
    operation_summary="API TO update VLAN interface",
    operation_description="This API adds a VLAN with its characteristics to the database",
)

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_vlan_interface(request,id_interface):
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input =request.data
        id_vlan = None if data_input.get('id', None) == "" else data_input.get('id', None)
        if Vlan.objects.filter(id=id_vlan).exists():
            vlan_object=Vlan.objects.get(id=id_vlan)
            vlan = serializers.serialize("json", [vlan_object])
            res_vlan = json.loads(vlan)[0]['fields']
            parent_interface=Interface.objects.get(id=res_vlan["parent_interface"]).ifname
            vlan_tag=res_vlan["vlan_tag"]
            vlan_priority=convert_priority(res_vlan["vlan_priority"]) if res_vlan["vlan_priority"] is not None else res_vlan["vlan_priority"]
            data_save={
                        "ifname":f"vlan{vlan_object.vlan_tag}@{parent_interface}",
                        "private_aux":False,
                        "bogon_aux":False,
                        "name_interface":data_input['name_interface'],
                        "description":f"default config vlan{vlan_object.vlan_tag}",
                    }
            
            vlan_object=Interface.objects.get(id=id_interface)
            aux_save=update_vlan_sys(vlan_object.ifname,parent_interface,vlan_tag,vlan_priority)
            if aux_save:
                interface_serializer=InterfaceSerializer(vlan_object,data=data_save)
                msg,status=save_in_db(aux_save,interface_serializer)
            else:
                msg=aux_save
                status=400
        else:
            msg=f"{CONSTANT_VLAN_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status)  
 
@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Deleted', 400: 'Bad Request'},
    operation_summary="API DELETE VLAN interface",
    operation_description="This API delete VLAN interface by id ",
)
   
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_vlan_interface(request,id_interface):
    if (request.method == 'DELETE'):
        # parse the incoming information
        if Interface.objects.filter(id=id_interface).exists():
            vlan_object=Interface.objects.get(id=id_interface)
            vlan_name=vlan_object.ifname
            aux_delete=delete_vlan_sys(vlan_name)
            if aux_delete:
                vlan_object.delete()
                msg=f"{CONSTANT_VLAN_INTERFACE} {SUCCESS_MESSAGES_DELETING}"
                status=200
            else:
                msg=aux_delete
                status=400
        else:
            msg=f"{CONSTANT_VLAN_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"
            status=400
      
    return JsonResponse({"msg": msg},status=status) 

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_vlan_interface(request):
    """API to get all vlan assigned from database """
    if (request.method == 'GET'):
        list_vlan_interface=[]
        # parse the incoming information
        vlan_object = Interface.objects.filter(ifname__startswith='vlan')
        vlans = serializers.serialize("json", vlan_object)
        res = json.loads(vlans)
        for i in range(len(res)):
            vlan_tag=res[i]['fields']['ifname'].strip("vlan").split("@")[0]
            interface=Vlan.objects.get(vlan_tag=vlan_tag).parent_interface_id
            ifname_parent=Interface.objects.get(id=interface).ifname      
            data={
                "id":res[i]['pk'],
                "name_interface":res[i]['fields']['name_interface'],
                "network_port":f"VLAN {vlan_tag} on {ifname_parent}"
            }
            list_vlan_interface.append(data)
    return JsonResponse({"msg": list_vlan_interface})  