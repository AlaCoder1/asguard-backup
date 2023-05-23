from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
from authentification.views import *
import socket
import datetime
import subprocess
# Create your views here.

@csrf_exempt
def Settings(request,id):
    return JsonResponse(getSystem(request, id))


@csrf_exempt
def getSystem(request, id):
    if (request.method == 'GET'):
        system = System.objects.filter(id=id)
        systemDict = serializers.serialize("json", system)
        res = json.loads(systemDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        systemJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(systemJson)


@csrf_exempt
def getNetwork(request, id):
    if (request.method == 'GET'):
        network = Network.objects.filter(id=id)
        networkDict = serializers.serialize("json", network)
        res = json.loads(networkDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        networkJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(networkJson)


@csrf_exempt
def getServerReseau(request, id):
    if (request.method == 'GET'):
        serverReseau = ServerReseau.objects.filter(id=id)
        serverReseauDict = serializers.serialize("json", serverReseau)
        res = json.loads(serverReseauDict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields']['id'] = id
        serverReseauJson = res[0]['fields']
        # return a no content response.
        return JsonResponse(serverReseauJson)


@csrf_exempt
def createSystem(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        serializerSystem = SystemSerializer(data=data)
        # check if the sent information is okay
        if (serializerSystem.is_valid()):
            msg = 'system added succesfully'
                # if okay, save it on the database
            serializerSystem.save()
                # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
        # provide a Json Response with the necessary error information
        return JsonResponse(SystemSerializer.errors, status=400)






@csrf_exempt
def createServerReseau(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        serializerServerReseau = ServerReseauSerializer(data=data)
        # check if the sent information is okay
        if (serializerServerReseau.is_valid()):
            msg = 'ServerReseau added succesfully'
                # if okay, save it on the database
            serializerServerReseau.save()
                # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
            # provide a Json Response with the necessary error information
            return JsonResponse(serializerUser.errors, status=400)
        # provide a Json Response with the necessary error information
        return JsonResponse(SystemSerializer.errors, status=400)




def sys(request):
    #hostname
    hostname = socket.gethostname()
    
    # Get the IP address of the machine
    ip_address = socket.gethostbyname(socket.gethostname())

    # Perform a reverse DNS lookup to get the domain name
    domain_name = socket.getfqdn(ip_address)

    
    # Get the local timezone
    local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    print(local_timezone)
    a=datetime.timezone(datetime.timedelta(0))
    print(a)
    # Get the timezone name
    print({"Timezone": local_timezone})
    
    # Get the hostname
    hostname = subprocess.check_output(["hostname"]).decode().strip()

    # Get the IP address of the machine
    ip_address = socket.gethostbyname(hostname)
    print({"ipadress":ip_address})
    # Perform a reverse DNS lookup to get the domain name
    domain_name = socket.getfqdn(ip_address)
    print({"domain_name":domain_name})
    # Extract the domain name from the FQDN
    domain = '.'.join(domain_name.split('.')[1:])
    return JsonResponse({"hostname": hostname,"domain":domain_name}, status=201)




############################################   gateway and Interface ############################################################
def InsertGateway():
    liste_getway =[]
    cmd1="ip route list | grep default | cut -d ' ' -f 3-5"
    stdin1, stdout1, stderr1 = ssh.exec_command(cmd1)
    print({'stderr1':stderr1.read().decode('utf-8')})
    output_getway_interface=stdout1.read().decode('utf-8').split('\n')
    output_getway_interface.pop()
    print({'output_getway_interface':output_getway_interface})
    print({'len_output_getway_interface':len(output_getway_interface)})
    for i in output_getway_interface:
        liste_getway.append(i.split(' ')[0])
        Gateway_Interface = GateWayInterface(gateway=i.split(' ')[0],interface=i.split(' ')[2])
        Gateway_Interface.save()
    print({'liste_getway':liste_getway})
    return "all gateway are saved" 

def InterfaceFromGateway(gateway):
    interfaceFromGateway = GateWayInterface.objects.filter(gateway=gateway)
    interfaceDict = serializers.serialize("json", interfaceFromGateway)
    res = json.loads(interfaceDict)
    interface=res[0]['fields']['interface']
    return interface

def AllGateway():
    list_gateways=[]
    gateways=GateWayInterface.objects.all()
    gatewaysDict = serializers.serialize("json", gateways)
    res = json.loads(gatewaysDict)
    print(res)
    for i in range(0, len(res)):
        list_gateways.append(res[i]['fields']['gateway'])
    
    # return JsonResponse({"list_gateways": list_gateways})
    return list_gateways
############################################   gateway and Interface ############################################################

############################################   TimeZone ############################################################


def initDB_by_timeZone(request):
    msg=""
    if (request.method == 'GET'):
        cmd = "timedatectl list-timezones"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        error_str = stderr.read().decode('utf-8')
        listesOfTimezone = stdout.read().decode('utf-8').split('\n')
        listesOfTimezone.pop()
        print({"error_str":error_str})
        if error_str =='':
            for time_data in listesOfTimezone:
                timezone = Timezone(name=time_data)
                timezone.save()
                msg="timezone added succesfully"
        else:
            msg=error_str
        return JsonResponse({"msg": msg})

from django.core import serializers   
def timeZones(request):
    list_timezones=[]
    if (request.method == 'GET'):
        timezones=Timezone.objects.all()
        timezonesDict = serializers.serialize("json", timezones)
        res = json.loads(timezonesDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_timezones.append(res[i]['fields'])
        return JsonResponse({"timezones": list_timezones})

############################################   TimeZone ############################################################

############################################   createNetwork ############################################################


@csrf_exempt
def createNetwork(request):
    # cmdNetwork = []
    # interface="eth0"
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        serializerNetwork = NetworkSerializer(data=data)
        print({'allGatway':AllGateway()})
        InterfaceFromGateway(data['gateway'])
        # check if the sent information is okay
        if (serializerNetwork.is_valid()):
            if data['prever_IPV4_IPV6']:
                cmdNetwork="nmcli connection mod "+InterfaceFromGateway(data['gateway'])+" +ipv4.dns "+data['server_DNS']
            else:
                cmdNetwork="nmcli connection mod "+InterfaceFromGateway(data['gateway'])+" +ipv6.dns "+data['server_DNS']+" ipv6.method auto"
            # Execute the command on the remote machine
            stdin, stdout, stderr = ssh.exec_command(cmdNetwork)
            print({'stdout':stdout.read().decode('utf-8')})
            print({'stderr':stderr.read().decode('utf-8')})
            if stderr.read().decode('utf-8') =="":
                msg = 'Network added succesfully'
                # if okay, save it on the database
                serializerNetwork.save()
            # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
        # provide a Json Response with the necessary error information
        return JsonResponse(SystemSerializer.errors, status=400)
    
    
############################################   createNetwork ############################################################