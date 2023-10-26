
import queue
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from .models import *
from .serializers import *
from django.core import serializers
import json
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from .functions import *
from django.core import serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema

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

@swagger_auto_schema(
    method='POST',
    request_body=GatewaySerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO ADD GATEWAY",
    operation_description="This API add gateway with their caracteristique in database",
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def addStaticGateway(request):
    if (request.method == 'POST'):
        data = request.data
        gwname=data.get('namegw', None)
        gwaddress = data.get('gwaddress', None)
        data['staticgw']=True
        if Gateway.objects.filter(Q(gwaddress=gwaddress) & Q(staticgw=True)).exists():
            msg="Gateway Already exist!"
        else:
            if add_gateway_DB(data) is True:
                msg="Add gateway Successfully!!"
            else:
                msg=add_gateway_DB(data)
           
        return JsonResponse({"msg:": msg})   
     
@swagger_auto_schema(
    method='DELETE',
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API DELETE GATEWAY",
    operation_description="This API delete gateway by id ",
)
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

@swagger_auto_schema(
    method='PUT',
    request_body=GatewaySerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE GATEWAY",
    operation_description="This API help us to update parametres in gateway added ",
)
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
