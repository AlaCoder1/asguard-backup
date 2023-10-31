from django.shortcuts import render
from django.http import JsonResponse

from backend.managementGroup.remoteFunctions import sudo
from backend.network.models import Interface
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
from backend.authentification.views import *
import socket
import datetime
import subprocess
import random
# Create your views here.

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def Settings(request,id):
    return JsonResponse(getSystem(request, id))


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
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


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createSystem(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
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






@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createServerReseau(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
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
@csrf_exempt
def InsertInterface(request):
    liste_getway =[]
    liste_interfaces =[]
    cmd1="ip route list | grep default | cut -d ' ' -f 3-5"
    stdin1, stdout1, stderr1 = ssh.exec_command(cmd1)
    print({'stderr1':stderr1.read().decode('utf-8')})
    output_getway_interface=stdout1.read().decode('utf-8').split('\n')
    output_getway_interface.pop()
    print({'output_getway_interface':output_getway_interface})
    print({'len_output_getway_interface':len(output_getway_interface)})
    for i in output_getway_interface:
        liste_getway.append(i.split(' ')[0])
        liste_interfaces.append(i.split(' ')[2])
    file_path = "/etc/ConfigInterfaces"
    # Open an SFTP session
    sftp = ssh.open_sftp()

    # Open the remote file in write mode
    remote_file = sftp.open(file_path, 'w')
    list_LAN_WAN = ['LAN', 'WAN', "LAN1", "WAN1"]
    content=""
    num_elements_to_select=len(liste_interfaces)
    print({"num_elements_to_select":num_elements_to_select})
    for i in liste_interfaces:
        if num_elements_to_select <= len(list_LAN_WAN):
            random_element = random.choice(list_LAN_WAN)
            print({"random_element":random_element})
        #content
        content+="{}: {} \n".format(i,random_element)
    # Write content to the remote file
    remote_file.write(content)

    # Close the remote file
    remote_file.close()

    # Close the SFTP session
    sftp.close()
    cmd = f"cat {file_path}"
    stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
    if stderr.read().decode('utf-8') == '':
        lines = stdout.read().decode('utf-8').split('\n')
        lines.pop()
        for i in range(0,len(lines)):
            # Check if an object with the same ifname exists
            existing_interface = Interface.objects.filter(ifname=lines[i].split(':')[0]).first()
            # print({"loul":lines[i].split(':')[0],"thani":lines[i].split(':')[1].strip()})
            if existing_interface:
                pass
            else:
                Interface.objects.create(ifname=lines[i].split(':')[0],name_interface=lines[i].split(':')[1].strip())
    else:
        return JsonResponse({"msg": "erreur: "+stderr.read().decode('utf-8')}) 
    # Gateway_Interface = GateWayInterface(gateway=i.split(' ')[0],interface=i.split(' ')[2])
    # Gateway_Interface.save()
    print({'liste_getway':liste_getway})
    print({'liste_interfaces':liste_interfaces})
    return JsonResponse({"msg": "all gateway are saved"}) 

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


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def createNetwork(request):
    # cmdNetwork = []
    # interface="eth0"
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
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