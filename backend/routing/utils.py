from backend.gateway.models import Gateway, GatewayInterface
from backend.gateway.serializers import GatewayInterfaceSerializer, GatewaySerializer
from backend.network.models import IP4Config, Interface
from utils.utils_functions import is_same_subnet


def create_gateway(gateway):
    """Create a new Gateway and GatewayInterface in database"""
    if len(GatewayInterface.objects.filter(interface_id=gateway['interface'])) > 0:
        return {"gateway": None, "error": ""}
    gwname = f'static_gw_{gateway["gateway_address"]}'
    data_gateway = {"gwname": gwname,
                    "gwaddress": gateway["gateway_address"],
                    "staticgw": True}
    
    # Add a Gateway to the database
    if len(Gateway.objects.filter(gwname=gwname)) == 0:
        serializer_gateway = GatewaySerializer(data=data_gateway)
    # Update a Gateway in database
    else:
        gateway_instance = Gateway.objects.get(gwname=gwname)
        serializer_gateway = GatewaySerializer(gateway_instance, data=data_gateway)

    if serializer_gateway.is_valid():
        serializer_gateway.save()
        # Get the last added Gateway
        new_gateway = Gateway.objects.last()
        data_gateway_interface = {"interface": gateway["interface"],
                                  "gateway": new_gateway.pk}
        # The metric is optional
        if "metric" in gateway:
            data_gateway_interface["metric"] = gateway["metric"]
        
        # Add a new GatewayInterface if there is no one with this interface or just update if there is one with this interface
        if len(GatewayInterface.objects.filter(interface=Interface.objects.get(id=gateway["interface"]))) == 0:
            # Add a GatewayInterface to the database
            serializer_gateway_interface = GatewayInterfaceSerializer(data=data_gateway_interface)
        else:
            # Update a GatewayInterface in database
            gateway_interface = GatewayInterface.objects.get(interface=Interface.objects.get(id=gateway["interface"]))
            serializer_gateway_interface = GatewayInterfaceSerializer(gateway_interface, data=data_gateway_interface)
        
        if serializer_gateway_interface.is_valid():
            serializer_gateway_interface.save()
            return {"gateway": new_gateway.pk,
                    "interface": gateway["interface"]}
        # Remove the last added Gateway if the GatewayInterface data doesn't match
        new_gateway.delete()
        return {"gateway": None,
                "error": list(serializer_gateway_interface.errors.values())[0][0]}
    return {"gateway": None,
            "error": list(serializer_gateway.errors.values())[0][0]}


def check_gateway_address(gateway_address, interface_id):
    """Get a gateway address and the id of the interface and 
       check if a gateway address is correct or not:
            1.Must be different to the interface address
            2.Must be within the same subnet as the interface"""
    try:
        interface_address = IP4Config.objects.get(interface_id=interface_id).ip_address
        interface_mask = IP4Config.objects.get(interface_id=interface_id).netmask
        if gateway_address != interface_address:
            is_correct = is_same_subnet(gateway_address, f"{interface_address}/{interface_mask}")
            if is_correct:
                return True
        return False
    except (Interface.DoesNotExist, IP4Config.DoesNotExist):
        return False
