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


@csrf_exempt
def createNetwork(request):
    # cmdNetwork = []
    interface="eth0"
    msg = ''
    liste_getway =[]
    if (request.method == 'POST'):
        # parse the incoming information
        data = request.data
        # instanciate with the serializer
        serializerNetwork = NetworkSerializer(data=data)
        # check if the sent information is okay
        if (serializerNetwork.is_valid()):
            if data['prever_IPV4_IPV6']:
                cmdNetwork="nmcli connection mod "+interface+" +ipv4.dns "+data['server_DNS']
            else:
                cmdNetwork="nmcli connection mod "+interface+" +ipv6.dns "+data['server_DNS']
            # Execute the command on the remote machine
            stdin, stdout, stderr = ssh.exec_command(cmdNetwork)
            print({'stdout':stdout.read().decode('utf-8')})
            print({'stderr':stderr.read().decode('utf-8')})
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
            # b=output_getway_interface[0].split(' ')
            # c=output_getway_interface[1].split(' ')
            # liste_getway.append(b[0])
            # liste_getway.append(c[0])
            # print({'b':b})
            # print({'c':c})
            print({'liste_getway':liste_getway})
            msg = 'Network added succesfully'
                # if okay, save it on the database
            serializerNetwork.save()
                # provide a Json Response with the data that was saved
            return JsonResponse({"msg": msg}, status=201)
        # provide a Json Response with the necessary error information
        return JsonResponse(SystemSerializer.errors, status=400)



@csrf_exempt
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
    data = request.data
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
    data = request.data
    configure_network(data['interface'], data['ip_address'], data['netmask'], data['gateway'], data['dns_servers'])
    return JsonResponse({"hostname": "domain"}, status=201) 

import os
def getAddressByInterface(interface):
    command = f"ip a | grep {interface} | grep inet | awk '{{ print $2 }}'" 
    return subprocess.run(command, shell=True, capture_output=True, text=True)

@csrf_exempt
def getInterface(request):
    data = request.data
    
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
    data = request.data
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


############################################   TimeZone ############################################################

from authentification.views import *
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

# import psycopg2
# def deleteDB(request):
#     if (request.method == 'POST'):
#         dbname = 'app-db-container'
#         user = 'postgres' # default username for a PostgreSQL Docker container
#         password = 'mypassword'
#         host = 'db' # name of the Docker container running the PostgreSQL database
#         port = '5432' # default port for a PostgreSQL database

#         # Connect to the database server
#         conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

#         # Open a cursor to perform database operations
#         cur = conn.cursor()

#         # Drop the database
#         cur.execute(f"DROP DATABASE {dbname}")

#         # Close the cursor and connection
#         cur.close()
#         conn.close()