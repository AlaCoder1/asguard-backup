from .models import *
from .serializers import *
def add_gateway_DB(data):
    Gatewayerializer = GatewaySerializer(data=data)
    if Gatewayerializer.is_valid():
            Gatewayerializer.save()
            return True
    return False
def update_gateway_DB(data,id):
    gateways = Gateway.objects.get(id=id)
    Gatewayerializer = GatewaySerializer(gateways,data=data)
    if Gatewayerializer.is_valid():
        Gatewayerializer.save()
        return True
    return False