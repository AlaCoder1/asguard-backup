from django.http import JsonResponse
# from backend.managementGroup.remoteFunctions import sudo
from backend.network.models import Interface
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
import json
from backend.authentification.views import *
from backend.gateway.models import *
import socket
import datetime
import subprocess
import random
from .function import *
from django.core import serializers
from collections import defaultdict
from drf_yasg.openapi import Schema, TYPE_ARRAY, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_OBJECT, TYPE_STRING
from rest_framework.permissions import IsAuthenticated
# Create your views here.

@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, operation_summary="API TO UPDATE generale settings",
                     request_body=Schema(type=TYPE_OBJECT,  required=['hostname', 'domain', 'timezone', 'dns_servers'],
                                                 properties={'hostname': Schema(type=TYPE_STRING),
                                                             'domain': Schema(type=TYPE_STRING),
                                                             'timezone': Schema(type=TYPE_STRING),
                                                             'dns_servers': Schema(type=TYPE_OBJECT,
                                                                                properties={'dns_server': Schema(type=TYPE_STRING),
                                                                                            'gateway': Schema(type=TYPE_STRING),
                                                                                            'interface_id': Schema(type=TYPE_INTEGER),
                                                                                            'metric': Schema(type=TYPE_INTEGER)}),
                                                             }))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def generale_settings(request,id):
    msg = ''
    if (request.method == 'PUT'):
        system_object = System.objects.get(id=id)
        # network = Network.objects.get(id=id)
        
        data = request.data
        if change_hostname(data['hostname']) and '.' in data['domain'] and data['domain'][-1] != '.':
            system_object.hostname = data['hostname']
            change_domain(data['domain'])
            system_object.domaine = data['domain']
            timezone = Timezone.objects.get(name = data['timezone'])
            set_time_zone(timezone.name)
            system_object.time_zone = timezone
            system_object.save()
            # if "dns_servers" in data:
            for i in data['dns_servers']:
                add_dns_servers(i['dns_server'])
                if i['gateway'] != "" and i['interface_id'] != "":
                    gateway = Gateway.objects.get(gwaddress = i['gateway'])
                    interface = Interface.objects.get(id = i['interface_id'])
                # gateway_interface = GatewayInterface.objects.get(gateway_id = gateway.pk)
                
                    resultat,error = add_gateway_to_dns_servers(i['dns_server'],gateway.gwaddress,interface.ifname,i['metric'])
            # network.server_dns = data['dns_servers']
            # network.save()
            # data['dns_servers'][0]['name_interface'] = interface.name_interface
            # For adding if the table is empty
            if not Network.objects.exists():
                Network.objects.create(server_dns=data['dns_servers'])  # Replace field1, field2, value1, value2 with your actual field names and values

            # For updating if the table is not empty
            else:
                instance, created = Network.objects.update_or_create(
                    defaults={'server_dns': data['dns_servers']},  # Replace field1, field2, new_value1, new_value2 with your updated values
                )
            msg = "done"
            status = 200
        else:
            msg = "eroor"
            status = 400
    return JsonResponse({"msg": msg}, status=status)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def get_generale_settings(request,id):
    if (request.method == 'GET'):
        system_object = System.objects.get(id=id)
        time_zone = Timezone.objects.get(name = system_object.time_zone.name)
        system_dict = {
            "hostname":system_object.hostname,
            "domaine":system_object.domaine,
            "time_zone":{
                "name" :time_zone.name,
                "id":time_zone.pk
            }
        }
        return JsonResponse({"generale_settings":system_dict})
    
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def time_zones(request):
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


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def gatways_information(request):
    gatways_information=[]
    if (request.method == 'GET'):
        gateway=GatewayInterface.objects.all()
        gatewayDict = serializers.serialize("json", gateway)
        res = json.loads(gatewayDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            gatways_information.append(res[i]['fields'])
        
        output_data = defaultdict(list)
        for item in gatways_information:
            gateway = item["gateway"]
            fetch_gateway = Gateway.objects.get(id = gateway)
            del item["gateway"]
            output_data[gateway].append(item)
        output_data = [
            {
                "gateway": {"id": gateway, "address": fetch_gateway.gwaddress},
                "info": info
            } for gateway, info in output_data.items()
        ]
        return JsonResponse({"gatways_information": output_data})









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






# @api_view(['POST'])
# @authentication_classes([SessionAuthentication])
# #@permission_classes([IsAuthenticated])
# def createServerReseau(request):
#     msg = ''
#     if (request.method == 'POST'):
#         # parse the incoming information
#         data = request.data
#         # instanciate with the serializer
#         serializerServerReseau = ServerReseauSerializer(data=data)
#         # check if the sent information is okay
#         if (serializerServerReseau.is_valid()):
#             msg = 'ServerReseau added succesfully'
#                 # if okay, save it on the database
#             serializerServerReseau.save()
#                 # provide a Json Response with the data that was saved
#             return JsonResponse({"msg": msg}, status=201)
#             # provide a Json Response with the necessary error information
#             return JsonResponse(serializerUser.errors, status=400)
#         # provide a Json Response with the necessary error information
#         return JsonResponse(SystemSerializer.errors, status=400)




# def sys(request):
#     #hostname
#     hostname = socket.gethostname()
    
#     # Get the IP address of the machine
#     ip_address = socket.gethostbyname(socket.gethostname())

#     # Perform a reverse DNS lookup to get the domain name
#     domain_name = socket.getfqdn(ip_address)

    
#     # Get the local timezone
#     local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
#     print(local_timezone)
#     a=datetime.timezone(datetime.timedelta(0))
#     print(a)
#     # Get the timezone name
#     print({"Timezone": local_timezone})
    
#     # Get the hostname
#     hostname = subprocess.check_output(["hostname"]).decode().strip()

#     # Get the IP address of the machine
#     ip_address = socket.gethostbyname(hostname)
#     print({"ipadress":ip_address})
#     # Perform a reverse DNS lookup to get the domain name
#     domain_name = socket.getfqdn(ip_address)
#     print({"domain_name":domain_name})
#     # Extract the domain name from the FQDN
#     domain = '.'.join(domain_name.split('.')[1:])
#     return JsonResponse({"hostname": hostname,"domain":domain_name}, status=201)




# ############################################   gateway and Interface ############################################################
# @csrf_exempt
# def InsertInterface(request):
#     liste_getway =[]
#     liste_interfaces =[]
#     cmd1="ip route list | grep default | cut -d ' ' -f 3-5"
#     stdin1, stdout1, stderr1 = ssh.exec_command(cmd1)
#     print({'stderr1':stderr1.read().decode('utf-8')})
#     output_getway_interface=stdout1.read().decode('utf-8').split('\n')
#     output_getway_interface.pop()
#     print({'output_getway_interface':output_getway_interface})
#     print({'len_output_getway_interface':len(output_getway_interface)})
#     for i in output_getway_interface:
#         liste_getway.append(i.split(' ')[0])
#         liste_interfaces.append(i.split(' ')[2])
#     file_path = "/etc/ConfigInterfaces"
#     # Open an SFTP session
#     sftp = ssh.open_sftp()

#     # Open the remote file in write mode
#     remote_file = sftp.open(file_path, 'w')
#     list_LAN_WAN = ['LAN', 'WAN', "LAN1", "WAN1"]
#     content=""
#     num_elements_to_select=len(liste_interfaces)
#     print({"num_elements_to_select":num_elements_to_select})
#     for i in liste_interfaces:
#         if num_elements_to_select <= len(list_LAN_WAN):
#             random_element = random.choice(list_LAN_WAN)
#             print({"random_element":random_element})
#         #content
#         content+="{}: {} \n".format(i,random_element)
#     # Write content to the remote file
#     remote_file.write(content)

#     # Close the remote file
#     remote_file.close()

#     # Close the SFTP session
#     sftp.close()
#     cmd = f"cat {file_path}"
#     stdin, stdout, stderr = ssh.exec_command(sudo(cmd))
#     if stderr.read().decode('utf-8') == '':
#         lines = stdout.read().decode('utf-8').split('\n')
#         lines.pop()
#         for i in range(0,len(lines)):
#             # Check if an object with the same ifname exists
#             existing_interface = Interface.objects.filter(ifname=lines[i].split(':')[0]).first()
#             # print({"loul":lines[i].split(':')[0],"thani":lines[i].split(':')[1].strip()})
#             if existing_interface:
#                 pass
#             else:
#                 Interface.objects.create(ifname=lines[i].split(':')[0],name_interface=lines[i].split(':')[1].strip())
#     else:
#         return JsonResponse({"msg": "erreur: "+stderr.read().decode('utf-8')}) 
#     # Gateway_Interface = GateWayInterface(gateway=i.split(' ')[0],interface=i.split(' ')[2])
#     # Gateway_Interface.save()
#     print({'liste_getway':liste_getway})
#     print({'liste_interfaces':liste_interfaces})
#     return JsonResponse({"msg": "all gateway are saved"}) 

# def InterfaceFromGateway(gateway):
#     interfaceFromGateway = GateWayInterface.objects.filter(gateway=gateway)
#     interfaceDict = serializers.serialize("json", interfaceFromGateway)
#     res = json.loads(interfaceDict)
#     interface=res[0]['fields']['interface']
#     return interface

# def AllGateway():
#     list_gateways=[]
#     gateways=Gateway.objects.all()
#     gatewaysDict = serializers.serialize("json", gateways)
#     res = json.loads(gatewaysDict)
#     print(res)
#     for i in range(0, len(res)):
#         list_gateways.append(res[i]['fields']['gateway'])
    
#     # return JsonResponse({"list_gateways": list_gateways})
#     return list_gateways
# ############################################   gateway and Interface ############################################################

# ############################################   TimeZone ############################################################


# def timeZones(request):
#     list_timezones=[]
#     if (request.method == 'GET'):
#         timezones=Timezone.objects.all()
#         timezonesDict = serializers.serialize("json", timezones)
#         res = json.loads(timezonesDict)
#         for i in range(0, len(res)):
#             res[i].pop('model')
#             id = res[i]['pk']
#             res[i].pop('pk')
#             res[i]['fields']['id'] = id
#             list_timezones.append(res[i]['fields'])
#         return JsonResponse({"timezones": list_timezones})

# ############################################   TimeZone ############################################################

# ############################################   createNetwork ############################################################


# @api_view(['POST'])
# @authentication_classes([SessionAuthentication])
# #@permission_classes([IsAuthenticated])
# def createNetwork(request):
#     # cmdNetwork = []
#     # interface="eth0"
#     msg = ''
#     if (request.method == 'POST'):
#         # parse the incoming information
#         data = request.data
#         # instanciate with the serializer
#         serializerNetwork = NetworkSerializer(data=data)
#         print({'allGatway':AllGateway()})
#         InterfaceFromGateway(data['gateway'])
#         # check if the sent information is okay
#         if (serializerNetwork.is_valid()):
#             if data['prever_IPV4_IPV6']:
#                 cmdNetwork="nmcli connection mod "+InterfaceFromGateway(data['gateway'])+" +ipv4.dns "+data['server_DNS']
#             else:
#                 cmdNetwork="nmcli connection mod "+InterfaceFromGateway(data['gateway'])+" +ipv6.dns "+data['server_DNS']+" ipv6.method auto"
#             # Execute the command on the remote machine
#             stdin, stdout, stderr = ssh.exec_command(cmdNetwork)
#             print({'stdout':stdout.read().decode('utf-8')})
#             print({'stderr':stderr.read().decode('utf-8')})
#             if stderr.read().decode('utf-8') =="":
#                 msg = 'Network added succesfully'
#                 # if okay, save it on the database
#                 serializerNetwork.save()
#             # provide a Json Response with the data that was saved
#             return JsonResponse({"msg": msg}, status=201)
#         # provide a Json Response with the necessary error information
#         return JsonResponse(SystemSerializer.errors, status=400)
    
    
############################################   createNetwork ############################################################


@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET SYSTEM LANGUAGE",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_language(request):
    """Getting System language"""
    system = System.objects.get()
    return JsonResponse({"language": system.language})


@swagger_auto_schema(
        method='PUT', 
        responses={200: 'Created', 400: 'Bad Request'}, 
        operation_summary="API TO UPDATE SYSTEM LANGUAGE",
        request_body=Schema(type=TYPE_OBJECT, required=['language'], properties={'language': Schema(type=TYPE_STRING)}))
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_language(request, id):
    """Update profile language"""
    try:
        data = request.data
        system = System.objects.get()
        serializer_system = SystemSerializer(system, data=data, partial=True)
        if serializer_system.is_valid():
            serializer_system.save()
            return JsonResponse({"msg": "Language is updated"}, status=200)
        return JsonResponse({"error": list(serializer_system.errors.values())[0][0]}, status=400)
    except (System.DoesNotExist):
        return JsonResponse({"error": "No systm configuration exist"}, status=400)
