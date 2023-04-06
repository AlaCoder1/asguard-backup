from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
# Create your views here.

@csrf_exempt
def Settings(request,id):
    # getSystem(request, id)
    # getNetwork(request, id)
    # getServerReseau(request, id)
    # print(getSystem(request, id))
    # print(getNetwork(request, id))
    # print(getServerReseau(request, id))
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
def createNetwork(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        # instanciate with the serializer
        serializerNetwork = NetworkSerializer(data=data)
        # check if the sent information is okay
        if (serializerNetwork.is_valid()):
            msg = 'Network added succesfully'
                # if okay, save it on the database
            serializerNetwork.save()
                # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
            # provide a Json Response with the necessary error information
            return JsonResponse(serializerUser.errors, status=400)
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



import socket
import pytz
import datetime
import subprocess
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


@csrf_exempt
def updateHostname(request):
    msg=""
    data = JSONParser().parse(request)
    # Prompt the user for the new domain name

    # Update the hosts file
    subprocess.run(["sudo", "sed", "-i", "s/\(127\.0\.0\.1.*\)\(localhost\)/\\1\\2 " + data['newhostname'] + "/", "/etc/hosts"])

    # Update the hostname file
    subprocess.run(["sudo", "sed", "-i", "s/\\(.*\\.\\)\\?[^.]*$/\\1" + data['newhostname'] + "/", "/etc/hostname"])

    # Set the new hostname
    subprocess.run(["sudo", "hostnamectl", "set-hostname", data['newhostname']])

    # Restart the hostname service
    subprocess.run(["sudo", "systemctl", "restart", "systemd-hostnamed"])
    msg="Domain name updated successfully to "+ data['newhostname']
    # Print a message indicating success
    return JsonResponse({"msg":msg})

import time
def timezone(request):
    msg=""
    # get the current system time zone
    timezone = time.tzname[0]

    # get the pytz time zone object for the system time zone
    pytz_timezone = pytz.timezone(timezone)
    a=timezone
    # print the system time zone and the corresponding pytz time zone object
    print("System time zone:", timezone)
    print("pytz time zone object:", pytz_timezone)
    return JsonResponse({"msg":a})


def ipv4(request):
    addrinfo = socket.getaddrinfo("example.com", None, socket.AF_INET)[0]
    ip = addrinfo[4][0]
    return JsonResponse({"IPv4 address:":ip})


import subprocess
# def set_network_interface(interface_name, ip_address, netmask):
#     # Configure the network interface with the specified IP address and netmask
#     subprocess.run(['ip', 'addr', 'add', ip_address + '/' + netmask, 'dev', interface_name], check=True)
#     subprocess.run(['ip', 'link', 'set', interface_name, 'up'], check=True)

# def set_default_gateway(gateway_ip):
#     # Configure the default gateway
#     subprocess.run(['ip', 'route', 'add', 'default', 'via', gateway_ip], check=True)

# def set_dns_servers(dns_servers):
#     # Configure DNS servers
#     with open('/etc/resolv.conf', 'w') as resolv_conf:
#         for dns_server in dns_servers:
#             resolv_conf.write(f'nameserver {dns_server}\n')
# def configurationNetwork(request):
#     set_network_interface('eth0', '10.1.12.188', '24')
#     set_default_gateway('10.1.12.1')
#     set_dns_servers(['8.8.8.8', '8.8.4.4'])
#     return JsonResponse({"hostname": "domain"}, status=201) 

def configure_network(interface, ip_address, netmask, gateway, dns_servers):
    subprocess.call(['ip', 'link', 'set', interface, 'up'])
    subprocess.call(['ip', 'addr', 'add', ip_address+'/'+netmask, 'dev', interface])
    subprocess.call(['ip', 'route', 'add', 'default', 'via', gateway])
    
    with open('/etc/resolv.conf', 'w') as f:
        for dns_server in dns_servers:
            f.write('nameserver {}\n'.format(dns_server))
            
@csrf_exempt
def configurationNetwork(request):
    data = JSONParser().parse(request)
    configure_network(data['interface'], data['ip_address'], data['netmask'], data['gateway'], data['dns_servers'])
    return JsonResponse({"hostname": "domain"}, status=201) 

import os
def getAddressByInterface(interface):
    command = f"ip a | grep {interface} | grep inet | awk '{{ print $2 }}'" 
    return subprocess.run(command, shell=True, capture_output=True, text=True)

@csrf_exempt
def getInterface(request):
    data = JSONParser().parse(request)
    
    result = getAddressByInterface(data['interface'])
    if result.returncode == 0:
        ip_address = result.stdout.strip()
        print(f"IP address of {data['interface']}: {ip_address}")
    else:
        print(f"Error: {result.stderr}")
    address=ip_address.split('\n')
    return JsonResponse({"address": address}, status=201) 

def delete_address(ip_address,interface):
    subprocess.run(['ip', 'addr', 'del', ip_address, 'dev', interface], check=True)
        
@csrf_exempt
def deleteAddress(request):
    data = JSONParser().parse(request)
    a=delete_address(data['ip_address'],data['interface'])
    return JsonResponse({"address": "address"}, status=201) 

@csrf_exempt
def createFile(request):
    # Define the network configuration file path and contents
    file_path = '/etc/netctl/eth0-static'
    file_contents = """Description='Static IP address for eth0'
    Interface=eth0
    Connection=ethernet
    IP=static
    Address=('10.1.12.188/24')
    Gateway='10.1.12.1'
    DNS=('8.8.8.8')"""

    # # Check if the file already exists
    # if os.path.isfile(file_path):
    #     print(f"The file {file_path} already exists.")
    # else:
    #     # Create the new file with the specified contents
    #     with open(file_path, 'w') as f:
    #         f.write(file_contents)
    #         print(f"The file {file_path} has been created.")
    with open(file_path, 'w') as f:
        f.write(file_contents)
        print(f"The file {file_path} has been created.")
    return JsonResponse({"address": "address"}, status=201)

@csrf_exempt
def readFile(request):
    list=[]
    interface = 'eth0'  # Replace with the name of the interface you want to check
    filename = os.path.join('/etc/netctl', interface)

    # Read the contents of the configuration file
    with open(filename, 'r') as f:
        contents = f.read()

    # Search for lines in the file that contain IP addresses
    for line in contents.splitlines():
        if 'IP=' in line:
            ip_address = line.split('=')[1]
            print(ip_address)
            list.append(ip_address)
    return JsonResponse({"address": list}, status=201)