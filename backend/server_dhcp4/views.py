import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.core import serializers
from backend.network.models import Interface
from backend.server_dhcp4.functions import create_dhcpv4_db, customize_error_msg, delete_dhcp4_server, init_file_dhcp4, is_ip_in_range, parse_range_address, parse_server_info, prepare_conf_server, retur_config_file, save_config_in_system, save_server_db
from django.db.models import Q
from backend.server_dhcp4.models import ServerDhcp4
from backend.server_dhcp4.serializers import DHCP4ServerSerializer
# # Create your views here.

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
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
    return JsonResponse({"list_dhcp4_server": list_dhcp4_server})  

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_server_dhcp4(request):
    """API to get all dhcp4 server from database """
    if (request.method == 'POST'):
        data=request.data
        id_interface=None if data.get('id_interface', None) == "" else data.get('id_interface', None)
        ip_address4=None if data.get('ip_address4', None) == "" else data.get('ip_address4', None)
        netmask4=None if data.get('netmask4', None) == "" else data.get('netmask4', None)
        data_save,subnet_addr,subnet_addr=prepare_conf_server(id_interface,ip_address4,netmask4)
        if not ServerDhcp4.objects.filter(Q(subnet_addr=subnet_addr)|Q(available_range=subnet_addr)).exists() :
            if ServerDhcp4.objects.filter(Q(interface_id=id_interface)).exists():
                server_object=ServerDhcp4.objects.get(interface_id=id_interface)
                server_serializer=DHCP4ServerSerializer(server_object,data=data_save)
            else:
                server_serializer=DHCP4ServerSerializer(data=data_save)
            if server_serializer.is_valid():
                server_serializer.save()
                msg="Server Created Successfully!!"
                status=201
            else:
                msg= customize_error_msg(server_serializer)
                status=400
        else:
            msg="Server already exist with this informations!"
            status=400
    return JsonResponse({"msg": msg},status=status) 

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_config_dhcp4_server(request,id_server):
    """API to assign vlan to interface  and create new interface of vlan to configure it """
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input=request.data
        ##parse data 
        available_range,ranges_from,ranges_to=parse_range_address(data_input)
        if is_ip_in_range(ranges_from,ranges_to, available_range) is True:
            data=parse_server_info(data_input)
            if ServerDhcp4.objects.filter(id=id_server).exists() and data['enable_dhcpv4'] is True :
                server_object=ServerDhcp4.objects.get(id=id_server)
                ifname=Interface.objects.get(id=server_object.interface_id).ifname
                aux_init=init_file_dhcp4(ifname) 
                if aux_init is True:
                    list_config=retur_config_file(data['subnet_addr'],data['subnet_mask'],ranges_from,ranges_to,data['dns_server'],data['gateway'],data['domain_name'])
                    aux_save_sys=save_config_in_system(list_config,ifname)
                    if aux_save_sys is True:
                       msg,status=save_server_db(data,ranges_from,ranges_to,server_object)
                    else:
                        msg=aux_save_sys
                        status=400
                else:
                    msg=aux_init
                    status=400  
            else:
                msg="Server not exist!"
                status=400   
        else:
            msg="Range from or to not in available range!"
            status=400      
    return JsonResponse({"msg": msg},status=status)  

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_server_dhcp4(request,server_id):
    """API to delete server dhcp4 created """
    if (request.method == 'DELETE'):
        # parse the incoming information
        if ServerDhcp4.objects.filter(id=server_id).exists():
            id_interface=ServerDhcp4.objects.get(id=server_id).interface_id
            ifname=Interface.objects.get(id=id_interface).ifname
            aux_delete=delete_dhcp4_server(id_interface,ifname)
            if aux_delete is True:
                msg="Server deleted Successfully"
                status=200
            else:
                msg=aux_delete
                status=400
        else:
            msg="Server not found!"
            status=400
    return JsonResponse({"msg": msg},status=status) 