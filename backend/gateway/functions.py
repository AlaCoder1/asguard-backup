from .models import *
from .serializers import *
# this import to run this on local machine
from backend.network.functions import *
# this import to run this on macine distant
# from network.Remotefunctions import *
########### 
def add_gateway_DB(data):
    Gatewayerializer = GatewaySerializer(data=data)
    if Gatewayerializer.is_valid():
            Gatewayerializer.save()
            return True
    return Gatewayerializer.errors
#####
def update_gateway_DB(data,id):
    gateways = Gateway.objects.get(id=id)
    Gatewayerializer = GatewaySerializer(gateways,data=data)
    if Gatewayerializer.is_valid():
        Gatewayerializer.save()
        return True
    return Gatewayerializer.errors
##########
###function to add gateway to interface in DB
def addGatewayInterfaceDB(GatewayObject,name_interface,metric):
    id_interface = Interface.objects.get(name_interface=name_interface).id
    if GatewayInterface.objects.filter(interface=id_interface).exists():
        id_GatewayInterface = GatewayInterface.objects.get(interface=id_interface).id
        gatewayInterface = GatewayInterface.objects.get(id=id_GatewayInterface)
        gatewayInterface.gateway = Gateway.objects.get(id=GatewayObject.id)  
    else:
        gatewayInterface = GatewayInterface()
        gatewayInterface.gateway=Gateway.objects.get(id=GatewayObject.id)
        gatewayInterface.interface=Interface.objects.get(name_interface=name_interface)
    gatewayInterface.metric=metric    
    gatewayInterface.save()
### get different metric
def differentMetric(exclude_list):
    if exclude_list ==[]:
        exclude_list = [0]
        
    num_start = min(exclude_list)+1
    while num_start < max(exclude_list):
        if num_start in exclude_list:
            num_start+=1
        else:
            return num_start
    return max(exclude_list)+1
#######
### function to return gateway wwith choices
def return_Gateway_system(uuid,addrgw,far_aux,multiWan_aux,metric,IP4ConfigObject):
    cmd=""
    if addrgw is not None :
        cmd= "sudo nmcli connection modify {} ipv4.gateway {} ".format(uuid,addrgw)
        ##test multiwan is true
        if multiWan_aux:
            cmd+=" ipv4.route-metric {}".format(metric)
    return cmd
###########DHCP
def get_gateway_dhcp(ifname):
    command="ip route show default | grep {} | grep 'proto'| cut -d ' ' -f 3-".format(ifname)
    output, error = run_command(command)
    if  not output.strip():
        return None, 0, False, False, False  # Return None and metric 0 in case of failure
    gwaddr = output.split()[0]
    metric_start = output.find('metric')
    metric = 0
    default_aux=True
    far_aux=False
    multi_aux=False
    if metric_start != -1:
        metric = output[metric_start + len('metric'):].strip()
        metric = ' '.join(word for word in metric.split() if not (word.isalpha()))
        metric=int(metric)
        multi_aux=True
    if output.find('onlink')!=-1:
           far_aux = True
    return gwaddr,metric,default_aux,far_aux,multi_aux
     
