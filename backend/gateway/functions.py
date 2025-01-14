# this import to run this on local machine
from backend.gateway.models import Gateway, GatewayInterface
from backend.gateway.serializers import GatewaySerializer
from backend.network.models import Interface
from backend.network.functions import run_command
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


CONSTANT_INTERFACE_GATEWAY = _('Gateway DHCP')
ERROR_MESSAGES_NOTFOUND = _("does not found")

def save_gateway_static_ip(gateway4,uuid,name_interface,id_interface):
    list_metric = []
    cmdgw4=None
    if gateway4!="Auto Detect":
        list_metric = []
        gateway_object=Gateway.objects.get(Q(gwaddress=gateway4) & Q(staticgw=True) )
        #################
        # default_aux=GatewayObject.default_aux
        far_aux=gateway_object.far_aux
        multiwan_aux=gateway_object.multiwan_aux
        addrgw4=gateway_object.gwaddress
        ############# generete metric statiquement
        metric=0
        all_gateway_interface = GatewayInterface.objects.all()
        if multiwan_aux:
            for i in all_gateway_interface:
                if i.metric is not None:
                    list_metric.append(i.metric)
            metric=different_metric(list_metric)
        cmdgw4=return_gateway_system(uuid,addrgw4,far_aux,multiwan_aux,metric)
        ipv4_gw_interface=True
        add_gateway_interface_db(gateway_object,name_interface,metric,ipv4_gw_interface)
    elif GatewayInterface.objects.filter(interface_id=id_interface).exists():
        interface = GatewayInterface.objects.get(interface_id=id_interface)
        interface.delete()
    return cmdgw4,list_metric

# this import to run this on macine distant
def add_gateway_db(data):
    gateway_serializer = GatewaySerializer(data=data)
    if gateway_serializer.is_valid():
        gateway_serializer.save()
        return True
    return next(iter(gateway_serializer.errors.values()))[0]



def update_gateway_db(data,id):
    gateways = Gateway.objects.get(id=id)
    gateway_serializer = GatewaySerializer(gateways, data=data)
    if gateway_serializer.is_valid():
        gateway_serializer.save()
        return True
    return gateway_serializer.errors


def add_gateway_interface_db(gateway_object, name_interface, metric, ipv4_gw_interface):
    """function to add gateway to interface in DB """
    id_interface = Interface.objects.get(name_interface=name_interface).id
    if GatewayInterface.objects.filter(Q(interface=id_interface)& Q(ipv4_gw_interface=ipv4_gw_interface)).exists():
        id_gateway_interface = GatewayInterface.objects.get(Q(interface=id_interface)& Q(ipv4_gw_interface=ipv4_gw_interface)).id
        gateway_interface = GatewayInterface.objects.get(id=id_gateway_interface)
        gateway_interface.gateway = Gateway.objects.get(id=gateway_object.id)  
    else:
        gateway_interface = GatewayInterface()
        gateway_interface.gateway=Gateway.objects.get(id=gateway_object.id)
        gateway_interface.interface=Interface.objects.get(name_interface=name_interface)
    gateway_interface.metric=metric  
    gateway_interface.ipv4_gw_interface=ipv4_gw_interface  
    gateway_interface.save()


def different_metric(exclude_list):
    """get different metric"""
    exclude_list=[x for x in exclude_list if x is not None]
    if exclude_list ==[]:
        exclude_list = [0]
    num_start = min(exclude_list)+1
    while num_start < max(exclude_list):
        if num_start in exclude_list:
            num_start+=1
        else:
            return num_start
    return max(exclude_list)+1


def return_gateway_system(uuid,addrgw, far_aux, multiwan_aux, metric):
    """function to return gateway wwith choices"""
    cmd=""
    if addrgw =="Auto Detect":
        cmd= "sudo nmcli connection modify {} ipv4.gateway {} ".format(uuid,"")
    else:
        cmd= "sudo nmcli connection modify {} ipv4.gateway {} ".format(uuid,addrgw)
        ##test multiwan is true
        if multiwan_aux:
            cmd+=" ipv4.route-metric {}".format(metric)
    return cmd


def return_gateway6_system(uuid,addrgw, far_aux, multiwan_aux, metric):
    """function to return gateway6 wwith choices"""
    cmd=""
    if addrgw =="Auto Detect":
        cmd= "sudo nmcli connection modify {} ipv6.gateway {} ".format(uuid,"")
    else:     
        cmd= "sudo nmcli connection modify {} ipv6.gateway {} ".format(uuid,addrgw)
    
        ##test multiwan is true
        if multiwan_aux:
            cmd+=" ipv6.route-metric {}".format(metric)
    return cmd


###########DHCP
def get_gateway_dhcp(ifname,aux_ip):
    command="sudo ip -{} route show default | grep {} | grep 'proto'| cut -d ' ' -f 3-".format(aux_ip,ifname)
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


####
def save_gateways_database(gwaddr,name_interface,default_aux,far_aux,multiwan_aux,metric,ipv4_gw_interface,ipv4_gw):
    if gwaddr:
        data_gw = {"gwname":"DHCP_GW_{}".format(gwaddr),
                   "gwaddress":"{}".format(gwaddr),
                   "description":"DHCP gateway generated automatically ",
                   "default_aux":default_aux,
                   "far_aux":far_aux,
                   "multiwan_aux":multiwan_aux,
                   "ipv4_gw":ipv4_gw,
                   "staticgw":True
                   }
        aux_exist=Gateway.objects.filter(Q(gwaddress=gwaddr) & Q(staticgw=True)).exists()
        if not aux_exist:
            aux_gw=add_gateway_db(data_gw)
        else:
            gateway_object=Gateway.objects.get(Q(gwaddress=gwaddr) & Q(staticgw=True) )
            id_gw=gateway_object.id
            aux_gw=update_gateway_db(data_gw,id_gw)
        if aux_gw:
            gateway_object=Gateway.objects.get(Q(gwaddress=gwaddr) & Q(staticgw=True) )
            add_gateway_interface_db(gateway_object,name_interface,metric,ipv4_gw_interface)  
            return True
        else:
            msg=aux_gw
           
    else:
            msg=True
             
    return msg
