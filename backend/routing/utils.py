from backend.gateway.models import Gateway
from backend.gateway.serializers import GatewayInterfaceSerializer, GatewaySerializer


def create_gateway(gateway):
    """Create a new Gateway and GatewayInterface in database"""
    # Add a Gateway to the database
    data_gateway = {"gwname": f'static_gw_{gateway["gateway_address"]}',
                    "gwaddress": gateway["gateway_address"],
                    "staticgw": True}
    serializer_gateway = GatewaySerializer(data=data_gateway)
    if serializer_gateway.is_valid():
        serializer_gateway.save()
        # Get the last added Gateway
        new_gateway = Gateway.objects.last()
        data_gateway_interface = {"interface": gateway["interface"],
                                  "gateway": new_gateway.pk}
        # The metric is optional
        if "metric" in gateway:
            data_gateway_interface["metric"] = gateway["metric"]
        # Add a GatewayInterface to the database
        serializer_gateway_interface = GatewayInterfaceSerializer(data=data_gateway_interface)
        if serializer_gateway_interface.is_valid():
            serializer_gateway_interface.save()
            return {"gateway": new_gateway.pk}
        # Remove the last added Gateway if the GatewayInterface data doesn't match
        new_gateway.delete()
        return {"gateway": None,
                "error": list(serializer_gateway_interface.errors.values())[0][0]}
    return {"gateway": None,
            "error": list(serializer_gateway.errors.values())[0][0]}
