
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.core import serializers
import json
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from django.core import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Gateway
from .serializers import GatewaySerializer
from .functions import add_gateway_db, update_gateway_db
from backend.routing.models import Routing
from django.views.decorators.http import require_http_methods
from decouple import config
# Constants
CONSTANT_GATEWAY = _("Gateway")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_EXISTANT = _("already exist")

@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve gateway details.",
    responses={
        200: openapi.Response(
            description="Gateway details retrieved successfully. The response includes the following fields:\n"
                        "-\t     `gwname`: Name of the gateway.\n"
                        "- \t   `gwaddress`: IP address of the gateway.\n"
                        "- \t   `staticgw`: Indicates if this is a static gateway.\n"
                        "- \t   `description`: Description of the gateway.\n"
                        "- \t   `default_aux`: Indicates if this is the default auxiliary gateway.\n"
                        "- \t   `far_aux`: Indicates if this is a far auxiliary gateway.\n"
                        "- \t   `multiwan_aux`: Indicates if this is a multi-WAN auxiliary gateway.\n"
                        "- \t   `ipv4_gw`: Indicates if this gateway is IPv4.\n"
                        "- \t   `created_at`: Creation timestamp of the gateway.\n"
                        "- \t   `updated_at`: Last updated timestamp of the gateway.\n"
                        "- \t   `id`: Unique ID of the gateway.",
        )
    }
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
def get_all_gateways(request):
    """
        API to get all GATEWAYS from the database.
        This function retrieves all GATEWAYS configurations from the database and returns them as a JSON response.
    
        Parameters:
        request (HttpRequest): The incoming request object containing the GET data.

        Returns:
        JsonResponse: A JSON response containing a list of GATEWAYS contains informations,
    """
    if (request.method == 'GET'):
        gateways = Gateway.objects.all()
        gateways_dict = serializers.serialize("json", gateways)
        res = json.loads(gateways_dict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            gateway_id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = gateway_id
            list_gateways.append(res[i]['fields'])
    return JsonResponse({"Gateways": list_gateways})
@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve static gateway details.",
    responses={
        200: openapi.Response(
            description="Gateway details retrieved successfully. The response includes the following fields:\n"
                        "-\t     `gwname`: Name of the gateway.\n"
                        "- \t   `gwaddress`: IP address of the gateway.\n"
                        "- \t   `staticgw`: Indicates if this is a static gateway.\n"
                        "- \t   `description`: Description of the gateway.\n"
                        "- \t   `default_aux`: Indicates if this is the default auxiliary gateway.\n"
                        "- \t   `far_aux`: Indicates if this is a far auxiliary gateway.\n"
                        "- \t   `multiwan_aux`: Indicates if this is a multi-WAN auxiliary gateway.\n"
                        "- \t   `ipv4_gw`: Indicates if this gateway is IPv4.\n"
                        "- \t   `created_at`: Creation timestamp of the gateway.\n"
                        "- \t   `updated_at`: Last updated timestamp of the gateway.\n"
                        "- \t   `id`: Unique ID of the gateway.",
        )
    }
)

@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
def get_all_static_gateways(request):
    """
        API to get all STATIC GATEWAYS from the database.
        This function retrieves all STATIC GATEWAYS configurations from the database and returns them as a JSON response.
    
        Parameters:
        request (HttpRequest): The incoming request object containing the GET data.

        Returns:
        JsonResponse: A JSON response containing a list of STATIC GATEWAYS contains informations.
    """
    if (request.method == 'GET'):
        gateways= Gateway.objects.filter(staticgw=True)
        gateways_dict = serializers.serialize("json", gateways)
        res = json.loads(gateways_dict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            gateway_id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = gateway_id
            list_gateways.append(res[i]['fields'])
    return JsonResponse({"Gateways": list_gateways})

@swagger_auto_schema(
    method='GET',
    operation_summary="API to retrieve  gateway by id details.",
      manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of gateway to get.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            description="Gateway details retrieved successfully. The response includes the following fields:\n"
                        "-\t     `gwname`: Name of the gateway.\n"
                        "- \t   `gwaddress`: IP address of the gateway.\n"
                        "- \t   `staticgw`: Indicates if this is a static gateway.\n"
                        "- \t   `description`: Description of the gateway.\n"
                        "- \t   `default_aux`: Indicates if this is the default auxiliary gateway.\n"
                        "- \t   `far_aux`: Indicates if this is a far auxiliary gateway.\n"
                        "- \t   `multiwan_aux`: Indicates if this is a multi-WAN auxiliary gateway.\n"
                        "- \t   `ipv4_gw`: Indicates if this gateway is IPv4.\n"
                        "- \t   `created_at`: Creation timestamp of the gateway.\n"
                        "- \t   `updated_at`: Last updated timestamp of the gateway.\n"
                        "- \t   `id`: Unique ID of the gateway.",
        )
    }
)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
def get_gateway_by_id(request, id):
    """
        API to get all  GATEWAY  by id from the database.
        This function retrieves GATEWAY  by id configurations from the database and returns them as a JSON response.
    
        Parameters:
        request (HttpRequest): The incoming request object containing the GET data.
        id (int) : The id of specific gateway

        Returns:
        JsonResponse: A JSON response containing a json of  GATEWAY  by id  contains informations.
    """
    if request.method == 'GET':
        try:
            gateway = Gateway.objects.get(id=id)
            gateway_data = serializers.serialize("json", [gateway])
            res = json.loads(gateway_data)
            list_gateways=[]
            for i in range(0, len(res)):
                res[i].pop('model')
                gateway_id = res[i]['pk']
                res[i].pop('pk')
                res[i]['fields']['id'] = gateway_id
                list_gateways.append(res[i]['fields'])
            return JsonResponse({"Gateway": list_gateways})
        except Gateway.DoesNotExist:
            return JsonResponse({"error": f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_INEXISTANT}"}, status=404)     



@swagger_auto_schema(
    method='POST',
    operation_summary="API to add a new gateway.",
    operation_description="This endpoint allows users to add a new gateway with necessary details.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'gwname': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the gateway', example='GWTest2'),
            'gwaddress': openapi.Schema(type=openapi.TYPE_STRING, description='IP address of the gateway', example=config('IP_ADDRESS')),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the gateway', example='just test'),
            'default_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if this is the default auxiliary gateway', example=True),
            'far_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if this is the far auxiliary gateway', example=False),
            'multiwan_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if this is the multi-WAN auxiliary gateway', example=True),
        },
        required=['gwname', 'gwaddress', 'description', 'default_aux',]
    ),
    responses={
        200: f"{CONSTANT_GATEWAY} {(SUCCESS_MESSAGES_CREATING)}",
        404:f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_EXISTANT}",
        400: "Bad request"
    }
)
@api_view(['POST'])
@require_http_methods(['POST'])
@authentication_classes([SessionAuthentication])
def add_static_gateway(request):
    """
    API to add a static gateway.

    This function handles the POST request to add a new static gateway to the database.
    It checks if the gateway with the same IP address already exists and returns an error message if it does.
    Otherwise, it adds the new gateway to the database and returns a success message.

    Parameters:
    request (HttpRequest): The incoming request object containing the POST data.

    Returns:
    JsonResponse: A JSON response containing a success or error message.
    """
    if (request.method == 'POST'):
        data = request.data
        gwaddress = data.get('gwaddress', None)
        data['staticgw']=True
        if Gateway.objects.filter(Q(gwaddress=gwaddress) & Q(staticgw=True)).exists():
            msg = f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_EXISTANT}"
            status=404
        else:
            aux_gateway=add_gateway_db(data)
            if  aux_gateway is True:
                msg = f"{CONSTANT_GATEWAY} {SUCCESS_MESSAGES_CREATING}"
                status=200
            else:
                msg =aux_gateway
                status=400

        return JsonResponse({"msg": msg},status=status)


@swagger_auto_schema(
    method='DELETE',
     manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID of gateway to delete",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    responses={200: f"{CONSTANT_GATEWAY} {(SUCCESS_MESSAGES_DELETING)}", 
               400: f"{ERROR_MESSAGES_DELETING} {CONSTANT_GATEWAY}",
               404:f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_INEXISTANT}"
               },
    operation_summary="API DELETE GATEWAY",
    
)
@api_view(['DELETE'])
@require_http_methods(["DELETE"])
@authentication_classes([SessionAuthentication])
def delete_gateway(request, id):
    """
    Delete a gateway from the database.

    This function handles the DELETE request to remove a gateway from the database.
    It checks if the gateway exists and if it's not associated with any routes before deletion.

    Parameters:
    request (HttpRequest): The incoming request object. Not used in this function but required by Django.
    id (int): The unique identifier of the gateway to be deleted.

    Returns:
    JsonResponse: A JSON response containing a success or error message.
    - If successful, returns a 200 status code with a success message.
    - If the gateway is associated with a route, returns a 400 status code with an error message.
    - If the gateway doesn't exist, returns a 404 status code with an error message.
    """
    try:
        gateway = Gateway.objects.get(id=id)
        if len(Routing.objects.filter(gateway=gateway)):
            return JsonResponse({"msg": f"{ERROR_MESSAGES_DELETING} {CONSTANT_GATEWAY}"}, status=400)
        gateway.delete()
        return JsonResponse({"msg": f"{CONSTANT_GATEWAY} {(SUCCESS_MESSAGES_DELETING)}"}, status=200)
    except Gateway.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_INEXISTANT}"}, status=404)


@swagger_auto_schema(
    method='PUT',
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            required=True,
            description="ID of gateway to update",
        ),
    ],
      
    operation_summary="API to update  gateway.",
    operation_description="This endpoint allows users to update gateway with necessary details.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'gwname': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the gateway', example='GWTest2'),
            'gwaddress': openapi.Schema(type=openapi.TYPE_STRING, description='IP address of the gateway', example=config('IP_ADDRESS')),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the gateway', example='just test'),
            'default_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if this is the default auxiliary gateway', example=True),
            'far_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if this is the far auxiliary gateway', example=False),
            'multiwan_aux': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if this is the multi-WAN auxiliary gateway', example=True),
        },
        required=['gwname', 'gwaddress', 'description', 'default_aux',]
    ),
    responses={
        200: f"{CONSTANT_GATEWAY} {SUCCESS_MESSAGES_UPDATING}",
        400:  f"{ERROR_MESSAGES_UPDATING} {CONSTANT_GATEWAY}"
    }
)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
def update_gateway(request,id):
    """
    API to update a static gateway.

    This function handles the POST request to update a new static gateway to the database.
    It checks if the gateway with the same IP address already exists and returns an error message if it does.
    Otherwise, it updates the new gateway to the database and returns a success message.

    Parameters:
    request (HttpRequest): The incoming request object containing the POST data.
    id (int) : The id of existing gateway

    Returns:
    JsonResponse: A JSON response containing a success or error message.
    """
    if (request.method == 'PUT'):
        msg = f"{ERROR_MESSAGES_UPDATING} {CONSTANT_GATEWAY}"
        status=400
        #tester si rule exist ou non
        if (Gateway.objects.filter(id=id).exists()):
            data = JSONParser().parse(request)
            if update_gateway_db(data,id):
                msg = f"{CONSTANT_GATEWAY} {SUCCESS_MESSAGES_UPDATING}"
                status=200
    return JsonResponse({"msg": msg},status=status)
