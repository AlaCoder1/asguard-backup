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

# Apply the swagger_auto_schema with methods argument
@swagger_auto_schema(
    methods=['GET'],
    operation_summary="API to get all VLANs from the database.",
    responses={
        200: openapi.Response(
            description="List of VLANs retrieved successfully. Each VLAN configuration is represented as a dictionary with the following fields:\n"
                        "-\t  parent_interface: The ID of the parent interface.\n"
                        "-\t  vlan_tag: The VLAN tag.\n"
                        "-\t  vlan_priority: The priority level of the VLAN.\n"
                        "-\t  description: A description of the VLAN.\n"
                        "-\t  id: The ID of the VLAN.\n"
                        "-\t  name_interface: The name of the associated interface.\n"
        )
    }
)
# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_vlan(request):
    """
    API to get all VLANs from the database.
    This function retrieves all VLAN configurations from the database and returns them as a JSON response.
   
    Parameters:
    request (HttpRequest): The incoming request object containing the GET data.

    Returns:
    JsonResponse: A JSON response containing a list of VLANs contains informations,
    Each VLAN configuration is represented as a dictionary with the following fields:
        - parent_interface: The ID of the parent interface.
        - vlan_tag: The VLAN tag.
        - "vlan_priority: The priority level of the VLAN.
        - description: A description of the VLAN.
        - id: The ID of the VLAN.
        - name_interface: The name of the associated interface.

   
    """
    if (request.method == 'GET'):
        list_vlan=[]
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
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'parent_interface': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the parent interface',
                example=1
            ),
            'vlan_tag': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='VLAN tag identifier',
                example=15
            ),
            'vlan_priority': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='VLAN priority level, e.g., Voice (5)',
                enum=["Best Effort ( 0 , default )",
                      'Background ( 1, lowest)',
                      'Excellent Effort (2)',
                      'Critical Applications (3)',
                      'Video (4)',
                      'Voice (5)',
                      'Internetwork Control (6)',
                      'Network Control (7)'
                      
                      ],
                default="Best Effort ( 0 , default )"
            ),
            'description': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Description of the VLAN configuration',
                example='test config vlan 15'
            ),
        },
        required=['parent_interface', 'vlan_tag', 'vlan_priority', 'description']
    ),
    responses={
        200: f'{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_CREATING}',
        400: 'Bad Request'
    },
    operation_summary="API to Add VLAN Configuration",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_vlan(request):
    """
    API to add a VLAN to the database.
    Parameters:
        request (HttpRequest): The incoming request object containing the POST data.
    Returns:
        JsonResponse: A JSON response containing a message indicating the success or failure of the operation.
    """
    if (request.method == 'POST'):
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
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of VLAN to update",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
        properties={
            'parent_interface': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the parent interface',
                example=1
            ),
            'vlan_tag': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='VLAN tag identifier',
                example=15
            ),
            'vlan_priority': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='VLAN priority level, e.g., Voice (5), Data (0)',
                enum=["Best Effort ( 0 , default )",
                      'Background ( 1, lowest)',
                      'Excellent Effort (2)',
                      'Critical Applications (3)',
                      'Video (4)',
                      'Voice (5)',
                      'Internetwork Control (6)',
                      'Network Control (7)'
                      
                      ],
                default="Best Effort ( 0 , default )"
            ),
            'description': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Description of the VLAN configuration',
                example='test config vlan 15'
            ),
        },
        required=['parent_interface', 'vlan_tag', 'vlan_priority', 'description']
    ),
    responses={
        200: f"{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_SAVED}",
        400: 'Bad Request'
    },
    operation_summary="API to Add VLAN Configuration",
)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_vlan(request,id):
    """
    API to update VLAN in the system and database.
    Parameters:
        request (HttpRequest): An instance of HttpRequest containing the incoming request data.
        id (int): The ID of the VLAN to be updated.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.
    """#+
    if (request.method == 'PUT'):
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
                if Interface.objects.filter(ifname=f"vlan{vlan_tag}").exists(): 
                    interface_object=Interface.objects.get(ifname=f"vlan{vlan_tag}")
                    aux_save=update_vlan_sys(interface_object.ifname,new_parent_interface,new_vlan_tag,new_vlan_priority)  
                    data_save={
                        "ifname":f"vlan{new_vlan_tag}",
                        "private_aux":False,
                        "bogon_aux":False,
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
     manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of VLAN to delete",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={200:f"{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_DELETING}",
               400: f"{CONSTANT_VLAN_CONFIG} {ERROR_MESSAGES_INEXISTANT}"},
    operation_summary="API DELETE VLAN",
)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_vlan(request,id):
    """
    Delete a VLAN from the database.
    This function removes a VLAN configuration from both the system and the database.
    Parameters:
        request (HttpRequest): The incoming request object containing the DELETE data.#+
        id (int): The ID of the VLAN to be deleted.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        The response includes a message and a status code. The status can be "success" or "error".
        If the VLAN is found and deleted, the response message will indicate successful deletion.
        If the VLAN is not found, the response will indicate an error.
    """
    if (request.method == 'DELETE'):
        if Vlan.objects.filter(id=id):
            vlan_object=Vlan.objects.get(id=id)
            name_interface=Interface.objects.get(id=vlan_object.parent_interface_id).ifname
            if Interface.objects.filter(ifname=f"vlan{vlan_object.vlan_tag}").exists():
                interface_object=Interface.objects.get(ifname=f"vlan{vlan_object.vlan_tag}")
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





@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Unique identifier for the interface',
                example=18
            ),
            'name_interface': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Name of the interface',
                example='vlan20'
            ),
        },
        required=['id', 'name_interface']
    ),
    responses={
        200: f"{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_SAVED}",
        400:"Bad request"
    },
    operation_summary="API TO ASSIGN VLAN Interface",
)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def assign_vlan_interface(request):
    """
    API to assign VLAN to an interface and create a new interface of VLAN to configure it.
    Parameters:
        request (HttpRequest): An instance of HttpRequest containing the incoming request data.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.#+
    """
    if (request.method == 'POST'):

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
                        "ifname":f"vlan{vlan_object.vlan_tag}",
                        "private_aux":False,
                        "bogon_aux":False,
                        "name_interface":f"VLAN{vlan_object.vlan_tag}",
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



@swagger_auto_schema(
    method='PUT',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        manual_parameters=[
        openapi.Parameter(
            'id_interface',
            openapi.IN_PATH,
            description="ID of interface VLAN to update",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
        properties={
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Unique identifier for the interface',
                example=18
            ),
            'name_interface': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Name of the interface',
                example='vlan20'
            ),
        },
        required=['id', 'name_interface']
    ),
    responses={
        200: 'Created',
        400: 'Bad Request'
    },
    operation_summary="API TO update VLAN interface",
)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_vlan_interface(request,id_interface):
    """
    Update a VLAN interface in the system and database.
    Parameters:
        request (HttpRequest): An instance of HttpRequest containing the incoming request data.
        id_interface (int): The ID of the VLAN interface to be updated.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.
    """
    if (request.method == 'PUT'):
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
                        "name_interface":f"VLAN{vlan_object.vlan_tag}",
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
    manual_parameters=[
        openapi.Parameter(
            'id_interface',
            openapi.IN_PATH,
            description="ID of interface VLAN to delete",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={200: f"{CONSTANT_VLAN_INTERFACE} {SUCCESS_MESSAGES_DELETING}", 
               400: f"{CONSTANT_VLAN_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"},
    operation_summary="API DELETE VLAN interface",
)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_vlan_interface(request,id_interface):
    """
    Delete a VLAN interface from the system and database.
    Parameters:
        request (HttpRequest): An instance of HttpRequest containing the incoming request data.
        id_interface (int): The ID of the VLAN interface to be deleted.
    Returns:
        JsonResponse: A JSON response with a message indicating the success or failure of the operation.
        The response includes a status code.
    """#+
    if (request.method == 'DELETE'):
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

@swagger_auto_schema(
    method='GET',
    operation_summary="API TO GET VLAN interface",
    responses={
        200: openapi.Response(
            description="List of VLAN interfaces retrieved successfully. Each interface is represented as a dictionary with the following keys:\n"
                         "-\t  id: The ID of the VLAN interface.\n"
                        "-\t  name_interface: The name of the VLAN interface. \n"
                        "-\t  network_port: A string describing the network port to which the VLAN interface is assigned. \n"

                        
                   
        )
    }
)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def get_vlan_interface(request):
    """
    API to get all VLAN interfaces assigned from the database.
    Parameters:
        request (HttpRequest): The incoming request object containing the GET data.
    Returns:
        JsonResponse: A JSON response containing a list of VLAN interfaces. 
        Each interface is represented as a dictionary with the following keys:
            - "id": The ID of the VLAN interface.
            - "name_interface": The name of the VLAN interface.
            - "network_port": A string describing the network port to which the VLAN interface is assigned.

    """
    if (request.method == 'GET'):
        list_vlan_interface=[]
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