import json
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.utils.translation import gettext_lazy as _
from django.core import serializers
from backend.network.models import Interface
from backend.server_dhcp4.functions import  customize_error_msg, delete_dhcp4_server, init_file_dhcp4, is_ip_in_range, parse_range_address, parse_server_info, prepare_conf_server, retur_config_file, save_config_in_system, save_server_db
from django.db.models import Q
from backend.server_dhcp4.models import ServerDhcp4
from backend.server_dhcp4.serializers import DHCP4ServerSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Constants
CONSTANT_DHCP_SERVER = _('DHCP server')
CONSTANT_RANGE = _('The specified range is outside the available range')


# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
# Error messages
ERROR_MESSAGES_NOTFOUND = _("does not found")
ERROR_MESSAGES_NOACTIVE = _("does not active")
ERROR_MESSAGES_EXISTANT = _("Already exist")

@swagger_auto_schema(
    methods=['GET'],
    operation_summary="API to get all dhcp server from the database.",
    responses={
        200: openapi.Response(
            description="Server configuration details retrieved successfully. The response includes the following attributes:\n"
                        "- \t   `interface`: The ID of the network interface.\n"
                        "- \t   `enable_dhcpv4`: Indicates whether DHCPv4 is enabled or not.\n"
                        "- \t   `subnet_addr`: The IP address of the subnet.\n"
                        "- \t   `subnet_mask`: The subnet mask for the network.\n"
                        "- \t   `available_range`: The available IP address range for DHCP.\n"
                        "- \t   `range_from`: The starting IP address of the range (if defined).\n"
                        "- \t   `range_to`: The ending IP address of the range (if defined).\n"
                        "- \t   `dns_server`: The DNS server address for the network (if configured).\n"
                        "- \t   `gateway`: The gateway address for the network (if configured).\n"
                        "- \t   `domain_name`: The domain name associated with the network (if configured).\n"
                        "- \t   `id`: The unique ID of the network configuration.\n"
                        "- \t   `name_interface`: The name of the interface (e.g., 'LAN').",
            )
    }
)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_all_server_dhcp4(request):
    """
    API to get all dhcp4 server from the database.

    Parameters:
    request (HttpRequest): The incoming request object.

    Returns:
    JsonResponse: A JSON response containing a list of all dhcp4 servers. Each server is represented as a dictionary with the following keys:
    - id: The primary key of the server.
    - range_from: A list of starting IP addresses for the server's range.
    - range_to: A list of ending IP addresses for the server's range.
    - dns_server: A list of DNS server IP addresses for the server.
    - name_interface: The name of the interface associated with the server.
    """
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

@swagger_auto_schema(
    method='post',
    operation_summary="API to add a new DHCPv4 server to the database.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id_interface': openapi.Schema(type=openapi.TYPE_INTEGER, description='The ID of the interface associated with the server.'),
            'ip_address4': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_IPV4, description='The IPv4 address of the server.'),
            'netmask4': openapi.Schema(type=openapi.TYPE_STRING, description='The netmask of the server.',example=24),
        },
        required=['id_interface', 'ip_address4', 'netmask4']
    ),
    responses={
        201: openapi.Response(
            description="Successfully created the DHCPv4 server.",
            examples={
                "application/json": {
                    "msg": "DHCP server is created"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request due to invalid input or server already exists.",
            examples={
                "application/json": {
                    "msg": "DHCP server Already exist"
                }
            }
        ),
    }
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_server_dhcp4(request):
    """
    API to add a new DHCPv4 server to the database.

    This function handles the POST request to add a new DHCPv4 server. 

    Parameters:
    request (HttpRequest): The incoming request object containing the POST data. The data should include the following fields:
        - id_interface: The ID of the interface associated with the server.
        - ip_address4: The IPv4 address of the server.
        - netmask4: The netmask of the server.

    Returns:
    JsonResponse: A JSON response containing a message indicating the success or failure of the operation. The response includes
    the following fields:
        - msg: A message indicating the success or failure of the operation.
        - status: The HTTP status code (201 for success, 400 for failure).
    """
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
                msg=f"{CONSTANT_DHCP_SERVER} {SUCCESS_MESSAGES_CREATING}"
                status=201
            else:
                msg= customize_error_msg(server_serializer)
                status=400
        else:
            msg=f"{CONSTANT_DHCP_SERVER} {ERROR_MESSAGES_EXISTANT}"
            status=400
    return JsonResponse({"msg": msg},status=status)



@swagger_auto_schema(
    method='put',
    operation_summary="API to update the configuration of a DHCPv4 server.",
    manual_parameters=[
        openapi.Parameter(
            'id_server',
            openapi.IN_PATH,
            description="ID of the DHCP server to update",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            # 'subnet_addr': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_IPV4, description='Subnet address',example="192.168.20.0"),
            # 'subnet_mask': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_IPV4, description='Subnet mask',example="255.255.255.0"),
            # 'available_range': openapi.Schema(type=openapi.TYPE_STRING, description='Subnet address',example="192.168.20.1 - 192.168.20.254"),
            'dns_server': openapi.Schema(type=openapi.TYPE_ARRAY,
                                         items=openapi.Schema(
                                           type=openapi.TYPE_STRING
                                         )
                                         , description='DNS server(s)',example=["8.8.8.8"]),
            'gateway': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_IPV4, description='Gateway address',example="192.168.20.1"),
            'domain_name': openapi.Schema(type=openapi.TYPE_STRING, description='Domain name',example="test.com"),
            'enable_dhcpv4': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Enable/disable DHCPv4'),
            'ranges_address': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'range_from': openapi.Schema(type=openapi.TYPE_STRING, description='Start of the IP range',example="192.168.20.6"),
                        'range_to': openapi.Schema(type=openapi.TYPE_STRING, description='End of the IP range',example="192.168.20.58"),
                    }
            )
            , description='Enable/disable DHCPv4')
        },
        required=['subnet_addr', 'subnet_mask', 'range_from', 'range_to', 'enable_dhcpv4']
    ),
    responses={
        200: openapi.Response(
            description="Successfully updated the DHCPv4 server configuration.",
            examples={
                "application/json": {
                    "msg": "DHCP server configuration updated successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request due to invalid input or server not active.",
            examples={
                "application/json": {
                    "msg": "DHCP server does not active"
                }
            }
        ),
    }
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_config_dhcp4_server(request,id_server):
    """
    API to update DHCPv4 server to the database.

    This function handles the POST request to update DHCPv4 server. 

    Parameters:
    request (HttpRequest): The incoming request object containing the POST data.
    id_server (int): The id of server to configure
        
    Returns:
    JsonResponse: A JSON response containing a message indicating the success or failure of the operation. The response includes
    the following fields:
        - msg: A message indicating the success or failure of the operation.
        - status: The HTTP status code (201 for success, 400 for failure).
    """
    if (request.method == 'PUT'):
        # parse the incoming information
        data_input=request.data
        ##parse data 
        if ServerDhcp4.objects.filter(id=id_server).exists():
            object_server=ServerDhcp4.objects.get(id=id_server)
            data_input["available_range"]=object_server.available_range
            data_input['subnet_addr']=object_server.subnet_addr
            data_input['subnet_mask']=object_server.subnet_mask
            available_range,ranges_from,ranges_to=parse_range_address(data_input)
            if is_ip_in_range(ranges_from,ranges_to, available_range,data_input['subnet_addr'],data_input['subnet_mask']) is True:
                data=parse_server_info(data_input)
                if  data['enable_dhcpv4'] is True :
                    ifname=Interface.objects.get(id=object_server.interface_id).ifname
                    aux_init=init_file_dhcp4(ifname) 
                    if aux_init is True:
                        list_config=retur_config_file(data['subnet_addr'],data['subnet_mask'],ranges_from,ranges_to,data['dns_server'],data['gateway'],data['domain_name'])
                        aux_save_sys=save_config_in_system(list_config,ifname)
                        if aux_save_sys is True:
                            msg,status=save_server_db(data,ranges_from,ranges_to,object_server)
                        else:
                            msg=aux_save_sys
                            status=400
                    else:
                        msg=aux_init
                        status=400  
                else:
                    msg=f"{CONSTANT_DHCP_SERVER} {ERROR_MESSAGES_NOACTIVE}"
                    status=400   

            else:
                msg=f"{CONSTANT_RANGE}"
                status=400     
        else:
            msg=f"{CONSTANT_DHCP_SERVER} {ERROR_MESSAGES_NOTFOUND}"
            status=400
    return JsonResponse({"msg": msg},status=status)  
@swagger_auto_schema(
    method='delete',
    operation_summary="API to delete a DHCPv4 server from the database and system.",
    manual_parameters=[
        openapi.Parameter(
            'server_id',
            openapi.IN_PATH,
            description="ID of the DHCP server to delete",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            description="Successfully deleted the DHCPv4 server.",
            examples={
                "application/json": {
                    "msg": "DHCP server is deleted"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request due to server not found.",
            examples={
                "application/json": {
                    "msg": "DHCP server does not found"
                }
            }
        ),
    }
)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_server_dhcp4(request,server_id):
    """
    Delete a dhcp server from the database and system.
    This function removes a dhcp server configuration from both the system and the database.
    Parameters:
        request (HttpRequest): The incoming request object containing the DELETE data.#+
        server_id (int): The ID of the server to be deleted.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        The response includes a message and a status code. The status can be "success" or "error".
        If the dhcp server is found and deleted, the response message will indicate successful deletion.
        If the dhcp server is not found, the response will indicate an error.
    """
    if (request.method == 'DELETE'):
        if ServerDhcp4.objects.filter(id=server_id).exists():
            id_interface=ServerDhcp4.objects.get(id=server_id).interface_id
            ifname=Interface.objects.get(id=id_interface).ifname
            aux_delete=delete_dhcp4_server(id_interface,ifname)
            if aux_delete is True:
                msg=f"{CONSTANT_DHCP_SERVER} {SUCCESS_MESSAGES_DELETING}"
                status=200
            else:
                msg=aux_delete
                status=400
        else:
            msg=f"{CONSTANT_DHCP_SERVER} {ERROR_MESSAGES_NOTFOUND}"
            status=400
    return JsonResponse({"msg": msg},status=status)