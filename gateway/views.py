
from django.shortcuts import render
import requests
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

# API to get gateway by id
# @api_view(['GET'])
# @permission_classes([])
# def getGatewayById(request,id):
#     if (request.method == 'GET'):
#          if (Gateway.objects.filter(id=id).exists()):
#             gateways = Gateway.objects.get(id=id)
#             gatewaysDict = serializers.serialize("json", gateways)
#             # resgateways = json.loads(gatewaysDict)
#     return JsonResponse({"Gateways:": gateways}) 
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
@authentication_classes([SessionAuthentication])
def addStaticGateway(request):
    msg="Failed to add gateway!" 
    if (request.method == 'POST'):
        data = request.data
        gwname=data.get('namegw', None)
        gwaddress = data.get('gwaddress', None)
        description = data.get('description', None)
        default_aux = data.get('default_aux', None)
        far_aux = data.get('far_aux', None)
        multiwan_aux = data.get('multiwan_aux', None)
        interfaces = data.get('interfaces', None)
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
            data = JSONParser().parse(request)
            gwname=data.get('namegw', None)
            gwaddress = data.get('gwaddress', None)
            description = data.get('description', None)
            default_aux = data.get('default_aux', None)
            far_aux = data.get('far_aux', None)
            multiwan_aux = data.get('multiwan_aux', None)
            if update_gateway_DB(data,id):
                msg="update gateway Successfully!!"
    return JsonResponse({"msg:": msg})      

from rest_framework.response import Response
from rest_framework.decorators import api_view
import paramiko
import time

def execute_remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    return stdout.readlines()

@api_view(['GET'])
def monitor_stats(request):
    host = request.query_params.get('host', "10.1.12.98")
    username = request.query_params.get('username', "root")
    password = request.query_params.get('password', "root")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    list_data=[]

    try:
        ssh_client.connect(host, username=username, password=password)
        while True:
            command = "top -bn 1 | awk 'NR==3{print $2}' && free | awk '/Mem/{printf \"%.2f\", $3/$2*100}'"
            output = execute_remote_command(ssh_client, command)
            cpu_usage, memory_usage = map(float, output)

            data = {
                'Timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'CPU Usage': cpu_usage,
                'Memory Usage': memory_usage
            }
            list_data.append(data)
            print({"list_data":list_data})

    except paramiko.AuthenticationException:
        return Response({"error": "Authentication failed, please check your credentials."}, status=401)
    except paramiko.SSHException as e:
        return Response({"error": f"SSH error: {e}"}, status=500)
    # finally:
    #     ssh_client.close()

# Add your helper function execute_remote_command and others here...
