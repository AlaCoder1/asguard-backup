from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from django.core import serializers
import json
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
# API to get all gateways
@api_view(['GET'])
@permission_classes([])
def getAllGateways(request):
    if (request.method == 'GET'):
        gateways = Gateway.objects.all()
        gatewaysDict = serializers.serialize("json", gateways)
        resGateways = json.loads(gatewaysDict)
    return JsonResponse({"Gateways:": resGateways})
# API to get all static gateways
@api_view(['GET'])
@permission_classes([])
def getAllStaticGateways(request):
    if (request.method == 'GET'):
        gateways= Gateway.objects.filter(staticgw=True)
        gatewaysDict = serializers.serialize("json", gateways)
        resgateways = json.loads(gatewaysDict)
    return JsonResponse({"Gateways:": resgateways})
            
# API to add  static gateway
@api_view(['POST'])
@permission_classes([])
def addStaticGateway(request):
    if (request.method == 'POST'):
        data = JSONParser().parse(request)
        gwname=data.get('namegw', None)
        gwaddress = data.get('gwaddress', None)
        description = data.get('description', None)
        default_aux = data.get('default_aux', None)
        far_aux = data.get('far_aux', None)
        multiwan_aux = data.get('multiwan_aux', None)
        interfaces = data.get('interfaces', None)
        data['staticgw']=True
        msg=""
        print({"interfaces":interfaces})
        Gatewayerializer = GatewaySerializer(data=data)
        Gatewayerializer.is_valid(raise_exception=True)
        if Gatewayerializer.is_valid():
            Gatewayerializer.save()
            msg="Add gateway Successfully!!"
        else: 
            msg="Failed to add gateway!"
        last_id = Gateway.objects.last().id
        for interface in interfaces:
            gatewayInterface = GatewayInterface()
            gatewayInterface.gateway=Gateway.objects.get(id=last_id)
            gatewayInterface.interface=Interface.objects.get(id=interface)
            gatewayInterface.metric=0
            gatewayInterface.save()
        
        print({"last_id":last_id})
            
    return JsonResponse({"msg:": msg})       
   
@api_view(['DELETE'])
@permission_classes([])
###API to delete gateway
def deleteGateway(request,id):
    if (request.method == 'DELETE'):
        msg="failed to delete gateway!!"
        #tester si rule exist ou non
        if (Gateway.objects.filter(id=id).exists()):
            gateways = Gateway.objects.get(id=id)
            gwaddr=gateways.gwaddress
            gateways.delete()
            msg="Delete gateway successfully!!"
            
    return JsonResponse({"msg:": msg})      

@api_view(['PUT'])
@permission_classes([])
###API to delete gateway
def updateGateway(request,id):
    if (request.method == 'PUT'):
        msg="failed to update gateway!!"
        #tester si rule exist ou non
        if (Gateway.objects.filter(id=id).exists()):
            gateways = Gateway.objects.get(id=id)
            data = JSONParser().parse(request)
            gwname=data.get('namegw', None)
            gwaddress = data.get('gwaddress', None)
            description = data.get('description', None)
            default_aux = data.get('default_aux', None)
            far_aux = data.get('far_aux', None)
            multiwan_aux = data.get('multiwan_aux', None)
            Gatewayerializer = GatewaySerializer(gateways,data=data)
            msg="Update gateway successfully!!"
            if Gatewayerializer.is_valid():
                Gatewayerializer.save()
                msg="update gateway Successfully!!"
    return JsonResponse({"msg:": msg})      
