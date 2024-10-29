from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from backend.gateway.models import Gateway, GatewayInterface

from backend.routing.list_routing import get_list_all_gateway, get_list_all_routing, get_one_gateway, get_one_routing
from backend.routing.models import Routing
from backend.routing.serializers import RoutingSerializer
from backend.routing.utils import create_gateway
from backend.routing.utils_system import routing_in_system
from utils.errors_utils import CommandExecutionError


# Constants
CONSTANT_ROUTE = _("Route")
CONSTANT_INTERFACE = _("Interface")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("Error in creating")
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_USED_ITEM = _("Unable to use this ")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ROUTINGS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_routing(request):
    """Getting all routing from database"""
    list_routing = get_list_all_routing()
    return JsonResponse(list_routing, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A ROUTING",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_routing(request, id):
    """Getting routing by id from database"""
    routing = get_one_routing(id)
    return JsonResponse(routing, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL GATEWAYS",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_gateway(request):
    """Getting all gateway from database"""
    list_gateway = get_list_all_gateway()
    return JsonResponse(list_gateway, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A GATEWAY",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_gateway(request, id):
    """Getting gateway by id from database"""
    gateway = get_one_gateway(id)
    return JsonResponse(gateway, safe=False)


@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO CREATE AN ROUTE", request_body=Schema(
                         type=TYPE_OBJECT, required=['destination_address', 'gateway_create', 'gateway'],
                         properties={'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'gateway_create': Schema(type=TYPE_BOOLEAN, description="Sent True if the user want to create a new gateway"),
                                     'gateway': Schema(type=TYPE_OBJECT, description="Contains fields of the new gateway that the user want to create it",
                                                       required=['interface', 'gateway_address'],
                                                       properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                                                   'gateway_address': Schema(type=TYPE_STRING, description="format of address/mask"),
                                                                   'metric': Schema(type=TYPE_INTEGER)}),
                                     'description': Schema(type=TYPE_STRING, description="description of the route"),
                                     }
                                     ))
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_routing(request):
    """Creating a new Route and adding it to the database"""
    try:
        data = request.data
        gateway = data.get("gateway", "")
        gateway_data = data.get("gateway", "")

        # Create a new Gateway and GatewayInterface
        if data.get("gateway_create"):
            result_gateway = create_gateway(gateway)
            if result_gateway["gateway"]:
                gateway = result_gateway["gateway"]
                data["gateway"] = gateway
            elif result_gateway["error"] == "":
                return JsonResponse({"error": f"{ERROR_MESSAGES_USED_ITEM} {CONSTANT_INTERFACE}"}, status=400)
            else:
                return JsonResponse({"error": result_gateway["error"]}, status=400)
        
        serializer_routing = RoutingSerializer(data=data)
        if serializer_routing.is_valid():
            gateway_instance = Gateway.objects.get(id=gateway)
            gateway_interface_instance = GatewayInterface.objects.get(gateway=gateway_instance)
            gateway_address = gateway_instance.gwaddress
            interface_ifname = gateway_interface_instance.interface.ifname
            routing_in_system("add", data["destination_address"], gateway_address, interface_ifname, 
                              gateway_interface_instance.metric)
            serializer_routing.save()
            return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_CREATING}"}, status=201)

        return JsonResponse({"error": list(serializer_routing.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        if data.get("gateway_create"):
            gwname = f'static_gw_{gateway_data["gateway_address"]}'
            if len(Gateway.objects.filter(gwname=gwname, gwaddress=gateway_data["gateway_address"])) == 1:
                gateway = Gateway.objects.get(gwname=gwname, gwaddress=gateway_data["gateway_address"])
                gateway.delete()
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_ROUTE}"}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN ROUTE",)
@api_view(['Delete'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_routing(request, id):
    """Deleting a routing from database"""
    try:
        routing = Routing.objects.get(id=id)
        
        gateway_interface_instance = GatewayInterface.objects.get(gateway=routing.gateway.pk)
        interface_ifname = gateway_interface_instance.interface.ifname
        routing_in_system("del", routing.destination_address, routing.gateway.gwaddress, interface_ifname, 
                          gateway_interface_instance.metric)

        # delete rule from database
        routing.delete()
        return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_DELETING} {CONSTANT_ROUTE}"}, status=400)
    except Routing.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ROUTE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO UPDATE A ROUTE", request_body=Schema(
                         type=TYPE_OBJECT, required=['destination_address', 'gateway_create', 'gateway'],
                         properties={'destination_address': Schema(type=TYPE_STRING, description="format of address/mask or blank for Any"),
                                     'gateway_create': Schema(type=TYPE_BOOLEAN, description="Sent True if the user want to create a new gateway"),
                                     'gateway': Schema(type=TYPE_OBJECT, description="Contains fields of the new gateway that the user want to create it",
                                                       required=['interface', 'gateway_address'],
                                                       properties={'interface': Schema(type=TYPE_INTEGER, description="Id of the interface"),
                                                                   'gateway_address': Schema(type=TYPE_STRING, description="format of address/mask"),
                                                                   'metric': Schema(type=TYPE_INTEGER)}),
                                     'description': Schema(type=TYPE_STRING, description="description of the route"),
                                     }
                                     ))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_routing(request, id):
    """Updating a Route by deleting and adding it again"""
    try:
        data = request.data
        routing = Routing.objects.get(id=id)
        
        # Delete a route
        gateway_interface_instance = GatewayInterface.objects.get(gateway=routing.gateway.pk)
        interface_ifname = gateway_interface_instance.interface.ifname
        routing_in_system("del", routing.destination_address, routing.gateway.gwaddress, interface_ifname, 
                          gateway_interface_instance.metric)
        
        gateway = data.get("gateway")

        # Create a new Gateway and GatewayInterface
        if data.get("gateway_create"):
            result_gateway = create_gateway(gateway)
            if result_gateway["gateway"]:
                gateway = result_gateway["gateway"]
                data["gateway"] = gateway
            else:
                return JsonResponse({"error": result_gateway["error"]}, status=400)
        
        gateway_instance = Gateway.objects.get(id=gateway)
        gateway_interface_instance = GatewayInterface.objects.get(gateway=gateway_instance)
        gateway_address = gateway_instance.gwaddress
        interface_ifname = gateway_interface_instance.interface.ifname
        routing_in_system("add", data["destination_address"], gateway_address, interface_ifname, 
                          gateway_interface_instance.metric)
        
        serializer_routing = RoutingSerializer(routing, data=data)
        if serializer_routing.is_valid():
            serializer_routing.save()
            return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

        return JsonResponse({"error": list(serializer_routing.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_ROUTE}"}, status=400)
    except Routing.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ROUTE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
