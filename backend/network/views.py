from django.http import JsonResponse
from backend.network.serializers import *
from backend.server_dhcp4.functions import create_dhcpv4_db, delete_dhcp4_server
from .models import *
from backend.settings.serializers import *
import json
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import  AllowAny
from backend.authentification.views import *
from .functions_ipv4 import *
from .functions_ipv6 import *
from .functions_generic_conf import *
from .functions_block_address import *
from backend.gateway.models import *
from backend.gateway.functions import *
from django.db.models import Q
from django.core import serializers
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Constants
CONSTANT_INTERFACE_NETWORK = _('Interface')
CONSTANT_INTERFACE_CONNECTION = _('Connection')

# Success messages
SUCCESS_MESSAGES_CONFIGURED = _("is configured")
SUCCESS_MESSAGES_DELETING = _("is deleted")


# Error messages
ERROR_MESSAGES_NOACTIVE = _("is not active")
ERROR_MESSAGES_FAILED = _("Failed to configure")
ERROR_MESSAGES_FAILED_DELETE = _("Failed to delete")
WARNING_CONNECTION=_("You need to delete the interface and set it up again")



###########################
@swagger_auto_schema(
    method='PUT',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
            openapi.Parameter(
                'name_interface',
                openapi.IN_PATH,
                description="Name of interface to update",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        properties={
            # 'device': openapi.Schema(type=openapi.TYPE_STRING, description='Device name associated with the interface'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the network interface'),
            'bogon_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Enable or disable bogon filtering'),
            'private_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Enable or disable private network filtering'),
            'addmac': openapi.Schema(type=openapi.TYPE_STRING, description='MAC address to add (if applicable)',
                                     example='00:50:56:aa:bb:cc'
                                     ),
            'mtuv': openapi.Schema(type=openapi.TYPE_INTEGER, description='MTU value for the interface (optional)',
                                   example=1500,  
                                   ),
            'mssv': openapi.Schema(type=openapi.TYPE_INTEGER, description='MSS value for the interface',
                                   example=1005
                                   ),
            'speed_duplex': openapi.Schema(type=openapi.TYPE_STRING, description='Speed and duplex setting',
                enum=['100baseTx-FD', '100baseTx-HD',"10baseT-FD",'10baseT-HD'],
                example="100baseTx-FD"),
            'setuptypeIP4': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='IPv4 setup type (STATIC, DHCP Base, DHCP Advanced)',
                enum=['STATIC', 'DHCP']
            ),
            'value_setup_Ipv4': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description='Configuration details for IPv4 based on the setup type',
                properties={
                    # Static configuration
                    'ip_address4': openapi.Schema(
                        type=openapi.FORMAT_IPV4,
                        description='IPv4 address (STATIC only)',
                        example='10.1.12.70'
                    ),
                    'netmask4': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Netmask for IPv4 (STATIC only)',
                        example=24
                    ),
                    'gateway4': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'value': openapi.Schema(
                                type=openapi.FORMAT_IPV4,
                                description='IPv4 gateway address (STATIC only)',
                                example='10.1.12.1'
                            )
                        }
                    ),
                    # DHCP Base configuration
                    'typeDHCP4': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='DHCP type (Base or Advanced)',
                        enum=['Base', 'Advanced'],
                        example='Base'
                    ),
                    'alias_add': openapi.Schema(
                        type=openapi.FORMAT_IPV4,
                        description='Alias IPv4 address (DHCP only)',
                        example='192.5.5.215'
                    ),
                    'alias_mask': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Alias mask (DHCP only)',
                        example=32
                    ),
                    'reject': openapi.Schema(
                        type=openapi.FORMAT_IPV4,
                        description='Rejected IPv4 address (DHCP only)',
                        example='192.33.137.209'
                    ),
                    'hostname': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Hostname for DHCP client (DHCP only)',
                        example='andare.fugue.com'
                    ),
                    # DHCP Advanced configuration
                    'timeout': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='DHCP timeout (Advanced only)',
                        example=10
                    ),
                    'retry': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='DHCP retry interval (Advanced only)',
                        example=60
                    ),
                    'select_timeout': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='DHCP select timeout (Advanced only)',
                        example=5
                    ),
                    'reboot': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Reboot interval for DHCP (Advanced only)',
                        example=10
                    ),
                    'backoff': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Backoff interval (Advanced only)',
                        example=10
                    ),
                    'initial_interval': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Initial interval for DHCP (Advanced only)',
                        example=2
                    ),
                    'dhcp_client': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='DHCP client identifier (Advanced only)',
                        example='00:a0:24:ab:fb:9c'
                    ),
                    'lease_time': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Lease time in seconds (Advanced only)',
                        example=36
                    ),
                    'request': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Requested options (Advanced only)',
                        example='subnet-mask, broadcast-address, time-offset, routers, domain-name, domain-name-servers, host-name, routers'
                    ),
                    'require': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Required options (Advanced only)',
                        example='subnet-mask, domain-name-servers'
                    ),
                    'domain_name': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Domain names (Advanced only)',
                        example='fugue.comrc.vix.comhome.vix.com'
                    ),
                    'domain_server': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Prepend domain servers (Advanced only)',
                        example='127.0.0.1'
                    ),
                },
            ),
            # IPv6 configuration
        },
        required=['nameInterface', 'device', 'setuptypeIP4', 'value_setup_Ipv4'],
    ),
    responses={
        200: "Successfully configured the network interface",
        400: "Invalid request payload",
        500: "Internal server error",
    },
    operation_summary="API to configure network for a chosen interface.",
)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def conf(request,name_interface): 
    """ API to configure interface 
        This function configure network for an interface including :
            -IPV4 configuration
            -IPV6 configuration
            - generic configuration
            - bogon range
        Parameters:
            request (HttpRequest): An instance of HttpRequest containing the incoming request data.
            name_interface (str): The name of the interface to be configured.
        Returns:
            JsonResponse: A JSON response containing the configuration status for the interface.
            The response includes a status code.

    """
    msg=f"{ERROR_MESSAGES_FAILED} {CONSTANT_INTERFACE_NETWORK}"
    status=400
    if (request.method == 'PUT'):
        data = request.data
        resulltat=validate_data_input(data,name_interface)
        if resulltat is  None:
            # print("hello")
            device_info,ifname,id_interface,aux_main,generic_config_object,uuid = device_name_interface(name_interface)
            if uuid is not None:
                    commandes=[]
                    commandes_final=[]
                    commandes_ipv6=[]
                    cmd_final_ipv6=[]
                    data,setuptype_ip4,setuptype_ip6,bogon_aux,private_aux,mtuv,mssv,speed_duplex,addmac=parse_data_generic(data)
                    output_service,error=get_old_config()
                    if error!="" or len(output_service)==0:
                        msg=f"{ERROR_MESSAGES_FAILED} {CONSTANT_INTERFACE_NETWORK}"
                        status=400
                    else:
                            output_service=add_requirement(ifname,output_service)
                            json_ipv4={}
                            json_ipv4,commandes_final,commandes,cmd_final_ipv4,list_metric=configuration_ipv4(data,setuptype_ip4,uuid,ifname,name_interface,id_interface,aux_main,commandes_final,output_service)
                            json_ipv6=data
                            if  setuptype_ip6 is not None:
                                configuration_ipv6(commandes_final,data,setuptype_ip6,Gateway,GatewayInterface,list_metric,ifname,name_interface,uuid,id_interface)
                            cmds,output_service,cmd_final_gen=generic_config(output_service,ifname,speed_duplex,addmac,mtuv,mssv,generic_config_object)
                            configs,cmds_block,output_service,cmd_final_block=block_address_commandes(output_service,ifname,bogon_aux,private_aux,device_info)
                            commandes+=commandes_ipv6+cmds+cmds_block
                            commandes = [x for x in commandes if x not in output_service]
                            output_service = add_cmd(output_service,commandes)
                            cmd_final_conf=refresh_conf_system(uuid,aux_main)
                            commandes_final+=configs+cmd_final_ipv4+cmd_final_ipv6+cmd_final_conf+cmd_final_gen+cmd_final_block
                            aux_run=run_all_commands(commandes_final,setuptype_ip4,10,output_service)
                            if aux_run is True:
                                    aux_gw_dhcp,json_ipv4=save_address_dhcp_ip4(setuptype_ip4,aux_main,ifname,name_interface,json_ipv4)
                                    aux_gw6_dhcp,json_ipv6=save_address_dhcp_ip6(setuptype_ip4,setuptype_ip6,ifname,name_interface,json_ipv6)
                                    aux_ipv4=update_DB(id_interface,json_ipv4,IP4Config,IP4ConfigSerializer) if not aux_main else True
                                    aux_ipv6=update_DB(id_interface,json_ipv6,IP6Config,IP6ConfigSerializer) if not aux_main else True
                                    aux_gen=update_DB(id_interface,data,GenericConfig,GenericConfigSerializer)
                                    aux_inter=update_interface_table(name_interface,data,InterfaceSerializer)     
                                    if aux_ipv4 is True and  aux_ipv6 is True and aux_gen  is True and aux_inter is True and aux_gw_dhcp is True and aux_gw6_dhcp is True:
                                        if setuptype_ip4.lower()=="static":
                                            aux_server=create_dhcpv4_db(id_interface,json_ipv4["ip_address"],json_ipv4["netmask"])
                                        elif setuptype_ip4.lower()=="dhcp":
                                            aux_server=delete_dhcp4_server(id_interface,ifname)
                                        else:
                                            aux_server=True
                                        if aux_server is True:
                                                msg=f"{CONSTANT_INTERFACE_NETWORK} {SUCCESS_MESSAGES_CONFIGURED}"
                                                status=200
               
            else:
                msg=f"{CONSTANT_INTERFACE_CONNECTION } {ERROR_MESSAGES_NOACTIVE}! | {WARNING_CONNECTION} "
                status=400
        else:
            print(resulltat)
            msg=resulltat
            status=400
        return JsonResponse({"message": msg},status=status)
             


@swagger_auto_schema(
    method='delete',
    operation_summary="API to delete interface from the database and system.",
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of the interface to delete",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200:f"{CONSTANT_INTERFACE_NETWORK} {SUCCESS_MESSAGES_DELETING}",
        400: f"{ERROR_MESSAGES_FAILED_DELETE} {CONSTANT_INTERFACE_NETWORK}"
    }
)
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_interface(request,id):
    """
    Delete interface from the database and system.
    This function removes an interface configuration from both the system and the database.
    Parameters:
        request (HttpRequest): The incoming request object containing the DELETE data.#+
        id (int): The ID of the interface to be deleted.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        The response includes a message and a status code. The status can be "success" or "error".
    """
    msg=f"{ERROR_MESSAGES_FAILED_DELETE} {CONSTANT_INTERFACE_NETWORK}"
    if request.method=="DELETE":
        if (Interface.objects.filter(id=id).exists()):
                interfaceObject = Interface.objects.get(id=id)
                ifname=interfaceObject.ifname
                output_service,error= get_old_config()
                if not error:
                    if desactiver_interface_remote(ifname,output_service):
                        interfaceObject.delete() 
                        msg=f"{CONSTANT_INTERFACE_NETWORK} {SUCCESS_MESSAGES_DELETING}"
                
    return JsonResponse({"msg":msg})
@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve network interface configuration details.",
    responses={
        200: openapi.Response(
            description=(
                "Details of the network interface configuration retrieved successfully. "
                "Each interface configuration contains the following attributes:\n"
                "- **ifname**: The name of the network interface (e.g., 'enp0s9').\n"
                "- **private_aux**: A boolean indicating if the interface is private.\n"
                "- **bogon_aux**: A boolean indicating if bogon traffic blocking is enabled.\n"
                "- **service_status**: The current status of the service associated with the interface, if applicable.\n"
                "- **name_interface**: The logical name of the interface (e.g., 'LAN1').\n"
                "- **is_main**: A boolean indicating if this is the main network interface.\n"
                "- **description**: A text description of the interface.\n"
                "- **created_at**: The timestamp when the interface configuration was created.\n"
                "- **updated_at**: The timestamp when the interface configuration was last updated.\n"
                "- **id**: The unique identifier of the interface configuration."
            ),
        )            
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])         
def AllInterfaces(request):
    """
    API to get all interfaces from the database.

    Parameters:
    request (HttpRequest): The incoming request object.

    Returns:
    JsonResponse: A JSON response containing a list of all interfaces .
    
    """
    list_interface = []
    if (request.method == 'GET'):
        interfaces = Interface.objects.all()
        interfaceDict = serializers.serialize("json", interfaces)
        res = json.loads(interfaceDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_interface.append(res[i]['fields'])
        # return a Json response
        return JsonResponse(list_interface, safe=False)
    
def GetInformationsByInterface(request,name_interface):
    """" function to get infomation about each interface"""
    info={}
    interface={}
    if (request.method == 'GET'):
        interfaceObject = Interface.objects.get(name_interface=name_interface)
        interface['id']=interfaceObject.id
        interface['ifname']=interfaceObject.ifname
        interface['private_aux']=interfaceObject.private_aux
        interface['bogon_aux']=interfaceObject.bogon_aux
        interface['service_status']=interfaceObject.service_status
        interface['name_interface']=interfaceObject.name_interface
        interface['description']=interfaceObject.description
        info['interface']=interface
        genericConfigObject = GenericConfig.objects.filter(interface_id=interfaceObject.id)
        genericConfigDict = serializers.serialize("json", genericConfigObject)
        res = json.loads(genericConfigDict)
        genericConfigList = list(genericConfigDict)
        if res != []:
            id = res[0]['pk']
            res[0]['fields']['id'] = id
            res[0].pop('model')
            res[0].pop('pk')
            res[0]['fields'].pop('interface')
            info['genericConfig']=res[0]['fields']
        else:
            info['genericConfig']=[]
        IPV4ConfigObject = IP4Config.objects.filter(interface_id=interfaceObject.id)
        IPV4ConfigObjectDict = serializers.serialize("json", IPV4ConfigObject)
        resultat = json.loads(IPV4ConfigObjectDict)
        if resultat != []:
            id = resultat[0]['pk']
            resultat[0]['fields']['id'] = id
            resultat[0].pop('model')
            resultat[0].pop('pk')
            resultat[0]['fields'].pop('interface')
            info['IPV4Config']=resultat[0]['fields']
        else:
            info['IPV4Config']=[]
    return JsonResponse(info)
