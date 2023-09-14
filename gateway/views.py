
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from django.core import serializers
import json
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from .functions import *
from django.core import serializers
# API to get all gateways
@api_view(['GET'])
@permission_classes([])
def getAllGateways(request):
    if (request.method == 'GET'):
        gateways = Gateway.objects.all()
        gatewaysDict = serializers.serialize("json", gateways)
        res = json.loads(gatewaysDict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_gateways.append(res[i]['fields'])
    return JsonResponse({"Gateways:": list_gateways})
# API to get all static gateways
@api_view(['GET'])
@permission_classes([])
def getAllStaticGateways(request):
    if (request.method == 'GET'):
        gateways= Gateway.objects.filter(staticgw=True)
        gatewaysDict = serializers.serialize("json", gateways)
        res = json.loads(gatewaysDict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_gateways.append(res[i]['fields'])
    return JsonResponse({"Gateways:": list_gateways})

@api_view(['GET'])
@permission_classes([AllowAny])
def getGatewayById(request, id):
    if request.method == 'GET':
        try:
            gateway = Gateway.objects.get(id=id)
            gateway_data = serializers.serialize("json", [gateway])
            res = json.loads(gateway_data)
            list_gateways=[]
            for i in range(0, len(res)):
                res[i].pop('model')
                id = res[i]['pk']
                res[i].pop('pk')
                res[i]['fields']['id'] = id
                list_gateways.append(res[i]['fields'])
            return JsonResponse({"Gateway": list_gateways})
        except Gateway.DoesNotExist:
            return JsonResponse({"error": "Gateway not found"}, status=404)     
# API to add  static gateway
@api_view(['POST'])
@permission_classes(["SessionAuthentication"])
def addStaticGateway(request):
    msg="Failed to add gateway!" 
    if (request.method == 'POST'):
        data = JSONParser().parse(request)
        gwaddress = data.get('gwaddress', None)
        data['staticgw']=True
        msg=""
        if Gateway.objects.filter(gwaddress=gwaddress).exists():
            gatewayObject=Gateway.objects.get(gwaddress=gwaddress)
            if gatewayObject.staticgw==True:
                msg="Gateway Already exist!"
        else:
            if add_gateway_DB(data):
                msg="Add gateway Successfully!!"
           
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
            data = JSONParser().parse(request)
            if update_gateway_DB(data,id):
                msg="update gateway Successfully!!"
    return JsonResponse({"msg:": msg})      
