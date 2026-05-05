from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_BOOLEAN, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from backend.gateway.models import Gateway, GatewayInterface

from backend.network.models import Interface
from backend.routing.list_routing import get_list_all_gateway, get_list_all_routing, get_one_gateway, get_one_routing
from backend.routing.models import Routing
from backend.routing.serializers import RoutingSerializer
from backend.routing.utils import check_gateway_address, create_gateway
from backend.routing.utils_system import routing_in_system
from utils.errors_utils import CommandExecutionError

from django.views.decorators.http import require_http_methods
from decouple import config
request_body_routing=Schema(
        type=TYPE_OBJECT, required=['destination_address', 'gateway_create', 'gateway'],
        properties={
            'destination_address': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="format of address"),
            'gateway_create': Schema(type=TYPE_BOOLEAN, default=True, description="Sent True if the user want to create a new gateway"),
            'gateway': Schema(
                type=TYPE_OBJECT,
                description="""If the user want to use an existent gateway then gateway will take the id of the gateway, like 1, 
                but when creating a new gateway it will contains fields of the new gateway that the user wants to create it""",
                properties={
                    'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface"),
                    'gateway_address': Schema(type=TYPE_STRING, example=config('IP_ADDRESS'), description="format of address"),
                    'metric': Schema(type=TYPE_INTEGER, example=20111)}),
            'interface': Schema(type=TYPE_INTEGER, example=1, description="Id of the interface related to the choosed gateway, only used when gateway_create is False (use an existent gateway)"),
            'description': Schema(type=TYPE_STRING, example="Description of Route", description="description of the route"),
            }
            )
# Constants
CONSTANT_ROUTE = _("Route")
CONSTANT_GATEWAY = _("Gateway")
CONSTANT_INTERFACE = _("Interface")
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("System error in creating")
ERROR_MESSAGES_DELETING = _("System error in deleting")
ERROR_MESSAGES_UPDATING = _("System error in updating")
ERROR_MESSAGES_EXISTING_NETWORK_GATEWAY = _("Route with this network and gateway exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")
ERROR_MESSAGES_USED_INTERFACE = _("Gateway for this interface exist")
ERROR_MESSAGES_INCORRECT_GATEWAY = _("Check your gateway address, must belongs to the same Subnet as the Host and can't take the same address")
ERROR_MESSAGES_INCORRECT_GATEWAY_LOADING = _("If you want to use an existing gateway, then the 'gateway' field should contain the ID of the gateway")
ERROR_MESSAGES_INCORRECT_GATEWAY_CREATING = _("If you want to create a new gateway, then the 'gateway' field must contain all the fields of the new gateway")


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL ROUTINGS",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_routing(request):
    """Getting all routing from database"""
    list_routing = get_list_all_routing()
    return JsonResponse(list_routing, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A ROUTING",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_routing(request, id):
    """Getting routing by id from database"""
    routing = get_one_routing(id)
    return JsonResponse(routing, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF ALL GATEWAYS",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_gateway(request):
    """Getting all gateway from database"""
    list_gateway = get_list_all_gateway()
    return JsonResponse(list_gateway, safe=False)


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET A GATEWAY",)
@api_view(['GET'])
@require_http_methods(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_gateway(request, id):
    """Getting gateway by id from database"""
    gateway = get_one_gateway(id)
    return JsonResponse(gateway, safe=False)


@swagger_auto_schema(
    'POST', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN ROUTE", 
    request_body=request_body_routing)
@api_view(['POST'])
@require_http_methods(['POST'])
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
            # Check if a gateway satisfy to the constraints of a correct gateway
            if not check_gateway_address(gateway_data["gateway_address"], gateway_data["interface"]):
                return JsonResponse({"error": ERROR_MESSAGES_INCORRECT_GATEWAY}, status=400)
            result_gateway = create_gateway(gateway)
            if result_gateway["gateway"]:
                gateway = result_gateway["gateway"]
                interface = result_gateway["interface"]
                data["gateway"] = gateway
                data["interface"] = interface
            elif result_gateway["error"] == "":
                return JsonResponse({"error": ERROR_MESSAGES_USED_INTERFACE}, status=400)
            else:
                return JsonResponse({"error": result_gateway["error"]}, status=400)
        
        # Raise an error message for unique constraints of Network and Gateway 
        if len(Routing.objects.filter(destination_address=data["destination_address"], gateway=gateway)) > 0:
            return JsonResponse({"error": ERROR_MESSAGES_EXISTING_NETWORK_GATEWAY}, status=400)
        
        # Get the gateway, interface and gateway_interface instance
        gateway_instance = Gateway.objects.get(id=gateway)
        interface_instance = Interface.objects.get(id=data["interface"])
        gateway_interface_instance = GatewayInterface.objects.get(gateway=gateway_instance, interface=interface_instance)
        
        serializer_routing = RoutingSerializer(data=data)
        if serializer_routing.is_valid():
            gateway_address = gateway_instance.gwaddress
            interface_ifname = interface_instance.ifname
            routing_in_system("add", data["destination_address"], gateway_address, interface_ifname, 
                              gateway_interface_instance.metric)
            serializer_routing.save()
            return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_CREATING}"}, status=201)
        return JsonResponse({"error": list(serializer_routing.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        # Delete the created gateway if system doesn't accept the new routing
        if data.get("gateway_create"):
            gwname = f'static_gw_{gateway_data["gateway_address"]}'
            if len(Gateway.objects.filter(gwname=gwname, gwaddress=gateway_data["gateway_address"])) == 1:
                gateway = Gateway.objects.get(gwname=gwname, gwaddress=gateway_data["gateway_address"])
                gateway.delete()
        return JsonResponse({"error": f"{ERROR_MESSAGES_CREATING} {CONSTANT_ROUTE}"}, status=400)
    except (Gateway.DoesNotExist, GatewayInterface.DoesNotExist):
        return JsonResponse({"error": f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except TypeError:
        # Catching the error when choosing to create a new gateway
        if data.get("gateway_create"):
            return JsonResponse({"error": ERROR_MESSAGES_INCORRECT_GATEWAY_CREATING}, status=400)
        # Catching the error when choosing to load a gateway
        return JsonResponse({"error": ERROR_MESSAGES_INCORRECT_GATEWAY_LOADING}, status=400)


@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE AN ROUTE",)
@api_view(['Delete'])
@require_http_methods(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_routing(request, id):
    """Deleting a routing from database"""
    try:
        routing = Routing.objects.get(id=id)
        
        gateway_interface_instance = GatewayInterface.objects.filter(gateway=routing.gateway.pk).first()
        interface_ifname = routing.interface.ifname
        routing_in_system("del", routing.destination_address, routing.gateway.gwaddress, interface_ifname, 
                          gateway_interface_instance.metric)

        # delete rule from database
        routing.delete()
        return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
        
    except CommandExecutionError:
        # deleting routing from database even when the route does not exist in system
        routing.delete()
        return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
    except GatewayInterface.DoesNotExist:
    # deleting routing from database even when the gateway does not exist
        routing.delete()
        return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_DELETING}"}, status=201)
    except Routing.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ROUTE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@swagger_auto_schema(
    'PUT', responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CREATE AN ROUTE", 
    request_body=request_body_routing)
@api_view(['PUT'])
@require_http_methods(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_routing(request, id):
    """Updating a Route by deleting and adding it again"""
    try:
        routing = Routing.objects.get(id=id)
    except Routing.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_ROUTE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    
    data = request.data
    try:
        # Delete a route
        gateway_interface_instance = GatewayInterface.objects.get(gateway=routing.gateway.pk)
        interface_ifname = gateway_interface_instance.interface.ifname
        routing_in_system("del", routing.destination_address, routing.gateway.gwaddress, interface_ifname, 
                          gateway_interface_instance.metric)
    except (CommandExecutionError, GatewayInterface.DoesNotExist, GatewayInterface.MultipleObjectsReturned):
        pass
    
    try:    
        gateway = data.get("gateway")

        # Create a new Gateway and GatewayInterface
        if data.get("gateway_create"):
            result_gateway = create_gateway(gateway)
            if result_gateway["gateway"]:
                gateway = result_gateway["gateway"]
                interface = result_gateway["interface"]
                data["gateway"] = gateway
                data["interface"] = interface
            elif result_gateway["error"] == "":
                return JsonResponse({"error": ERROR_MESSAGES_USED_INTERFACE}, status=400)
            else:
                return JsonResponse({"error": result_gateway["error"]}, status=400)
        
        # Raise an error message for unique constraints of Network and Gateway
        if len(Routing.objects.filter(destination_address=data["destination_address"], gateway=gateway).exclude(id=id)) > 0:
            return JsonResponse({"error": ERROR_MESSAGES_EXISTING_NETWORK_GATEWAY}, status=400)
        
        # Get the gateway, interface and gateway_interface instance
        gateway_instance = Gateway.objects.get(id=gateway)
        interface_instance = Interface.objects.get(id=data["interface"])
        gateway_interface_instance = GatewayInterface.objects.get(gateway=gateway_instance, interface=interface_instance)

        gateway_address = gateway_instance.gwaddress
        interface_ifname = interface_instance.ifname
        routing_in_system("add", data["destination_address"], gateway_address, interface_ifname, 
                          gateway_interface_instance.metric)
        
        serializer_routing = RoutingSerializer(routing, data=data)
        if serializer_routing.is_valid():
            serializer_routing.save()
            return JsonResponse({"msg": f"{CONSTANT_ROUTE} {SUCCESS_MESSAGES_UPDATING}"}, status=201)

        return JsonResponse({"error": list(serializer_routing.errors.values())[0][0]}, status=400)
        
    except CommandExecutionError:
        return JsonResponse({"error": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_ROUTE}"}, status=400)
    except (Gateway.DoesNotExist, GatewayInterface.DoesNotExist):
        return JsonResponse({"error": f"{CONSTANT_GATEWAY} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"{CONSTANT_INTERFACE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    except TypeError:
        # Catching the error when choosing to create a new gateway
        if data.get("gateway_create"):
            return JsonResponse({"error": ERROR_MESSAGES_INCORRECT_GATEWAY_CREATING}, status=400)
        # Catching the error when choosing to load a gateway
        return JsonResponse({"error": ERROR_MESSAGES_INCORRECT_GATEWAY_LOADING}, status=400)
