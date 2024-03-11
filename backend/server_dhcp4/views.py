import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.core import serializers
from backend.network.models import Interface
from backend.server_dhcp4.functions import init_file_dhcp4, is_ip_in_range, parse_server_info, retur_config_file, save_config_in_system

from backend.server_dhcp4.models import ServerDhcp4
from backend.server_dhcp4.serializers import DHCP4ServerSerializer
# # Create your views here.

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_all_server_dhcp4(request):
    """API to get all vlan from database """
    if (request.method == 'GET'):
        list_dhcp4_server=[]
        # parse the incoming information
        dhcp4_object=ServerDhcp4.objects.all()
        dhcp4 = serializers.serialize("json", dhcp4_object)
        res = json.loads(dhcp4)
        for i in range(len(res)):
            res[i]['fields']['id']=res[i]["pk"]
            list_dhcp4_server.append(res[i]['fields'])
    return JsonResponse({"response": list_dhcp4_server})  

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_config_dhcp4_server(request,id_server):
    """API to assign vlan to interface  and create new interface of vlan to configure it """
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input=request.data
        ##parse data 
        available_range=None if data_input.get('available_range', None) == "" else data_input.get('available_range', None)
        ranges_from=[] if data_input.get('ranges_from', []) == "" else data_input.get('ranges_from', [])
        ranges_to=[] if data_input.get('ranges_to', []) == "" else data_input.get('ranges_to', [])
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
                        range_from = ' , '.join(filter(None, ranges_from)) if len(ranges_from)!=0 else None
                        range_to = ' , '.join(filter(None, ranges_to)) if len(ranges_to)!=0 else None
                        data['range_from']=range_from
                        data['range_to']=range_to
                        serializer_server=DHCP4ServerSerializer(server_object,data=data)
                        if serializer_server.is_valid():
                            serializer_server.save()
                            msg="Config server DHPV4 saved successfully!"
                            status=200
                    else:
                        msg=aux_save_sys
                        status=400
                else:
                    msg=aux_init
                    status=400    
        else:
            msg="Range from or to not in available range!"
            status=400 
                
            
    return JsonResponse({"response": msg},status=status)  