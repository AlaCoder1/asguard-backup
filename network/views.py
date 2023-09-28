from django.http import JsonResponse
from network.serializers import *
from .models import *
from settings.serializers import *
from rest_framework.parsers import JSONParser
import json
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentification.views import *
from .functions import *
from django.views.decorators.csrf import csrf_exempt
from gateway.models import *
from gateway.functions import *
from django.db.models import Q
from django.core import serializers

def device_nameInterface(name_interface):
    data = Interface.objects.get(name_interface=name_interface)
    return data

###########################

#################################
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def add_interface(request):
    data = request.data
    serializerIP4Config = InterfaceSerializer(data=data)
    print(serializerIP4Config.is_valid())
    if (serializerIP4Config.is_valid()):
        serializerIP4Config.save()
    return JsonResponse({"msg:": "interface added successfully!!!!!"})

###########################
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def conf(request,name_interface):
    msg="Failed to configure Network!"
    status=400
    list_metric = []
    if (request.method == 'PUT'):
        interfaceObject = Interface.objects.get(name_interface=name_interface)
        id_interface = interfaceObject.id
        ###### get object Config
        IP4ConfigObject=""
        genericConfigObject=""
        if IP4Config.objects.filter(interface_id=id_interface).exists():
            IP4ConfigObject=IP4Config.objects.get(interface_id=id_interface)
        if GenericConfig.objects.filter(interface_id=id_interface).exists():
            genericConfigObject=GenericConfig.objects.get(interface_id=id_interface)
        ###############
        #get object of interface type
        deviceInfo = device_nameInterface(name_interface)
        #get interface name to execute command systeme
        ifname=deviceInfo.ifname
        nameInterface=deviceInfo.name_interface
        ##get uuid to reference to connection
        uuid=get_conn_name(ifname)
        ####
        # parse the incoming information
        data = request.data
        # return JsonResponse({"data":data})
        setuptypeIP4 = data.get('setuptypeIP4')
        description = data.get('description')
        bogon_aux = data.get('bogon_aux')
        private_aux = data.get('private_aux')
        mtuV =  None if data.get('mtuV', None) == "" else data.get('mtuV', None)
        mssV =  None if data.get('mssV', None) == "" else data.get('mssV', None)
        speed_duplex =  None if data.get('speed_duplex', None) == "" else data.get('speed_duplex', None)
        addmac =  None if data.get('addmac', None) == "" else data.get('addmac', None)
        data["mtuV"]=mtuV
        data["mssV"]=mssV
        data["speed_duplex"]=speed_duplex
        data["addmac"]=addmac
        commandes=[]
        commandes_final=[]
        commandesIPV6=[]
        cmd_final_ipv6=[]
        cmd_final_ipv4=[]
        ##get old configuration in service
        output_service,error=get_old_config()
        if error!="":
            msg=error
            status=400
        else:
            if len(output_service)!=0:
                #delete empty value
                output_service = [x for x in output_service if x]
                ##add requirement service
                output_service=add_requirement(ifname,output_service)
                ###set gatewayObject to None
                GatewayObject=None
                ##IPV4 configuration cases 
                match setuptypeIP4:
                    case "None":
                         #call function to convert address to None
                        commandes,output_service,cmd_final_ipv4=update_conn_None_IPV4(output_service,ifname)
                    case "static":
                        typeDHCP4=''
                        ip_address4 =  None if data['value_setup_Ipv4'].get('ip_address4', None) == "" else  data['value_setup_Ipv4'].get('ip_address4', None)
                        netmask4 =  None if data['value_setup_Ipv4'].get('netmask4', None) == "" else  data['value_setup_Ipv4'].get('netmask4', None)
                        gateway4 =  None if data['value_setup_Ipv4']['gateway4'].get('value', None) == "" else  data['value_setup_Ipv4']['gateway4'].get('value', None)
                        GatewayObject=Gateway.objects.get(Q(gwaddress=gateway4) & Q(staticgw=True) )
                        #################
                        default_aux=GatewayObject.default_aux
                        far_aux=GatewayObject.far_aux
                        multiWan_aux=GatewayObject.multiwan_aux
                        multiWan_aux=GatewayObject.multiwan_aux
                        addrgw4=GatewayObject.gwaddress
                        #############
                        metric=0
                        allGatewayInterface = GatewayInterface.objects.all()
                        if multiWan_aux:
                            for i in allGatewayInterface:
                                list_metric.append(i.metric)
                            metric=differentMetric(list_metric)
                        cmdgw4=return_Gateway_system(uuid,addrgw4,far_aux,multiWan_aux,metric,IP4ConfigObject)
                        addGatewayInterfaceDB(GatewayObject,name_interface,metric)
                        #call function to convert address to static
                        commandes,output_service,cmd_final_ipv4=update_conn_static_IPV4(output_service,ifname,uuid,ip_address4,netmask4,cmdgw4,IP4ConfigObject)
                        jsonIPV4={
                    "nameInterface":nameInterface,"ifname":ifname,
                    "ip_address":ip_address4,"netmask":netmask4,
                    "addrgw":addrgw4,
                    "typeIP4":setuptypeIP4}
                    case "dhcp":
                        addmac = None
                        typeDHCP4 = data.get('value_setup_Ipv4')['typeDHCP4']
                        alias_add =  None if data['value_setup_Ipv4'].get('alias_add', None) == "" else  data['value_setup_Ipv4'].get('alias_add', None)
                        alias_mask =  None if data['value_setup_Ipv4'].get('alias_mask', None) == "" else  data['value_setup_Ipv4'].get('alias_mask', None)
                        reject =  None if data['value_setup_Ipv4'].get('reject', None) == "" else  data['value_setup_Ipv4'].get('reject', None)
                        hostname =  None if data['value_setup_Ipv4'].get('hostname', None) == "" else  data['value_setup_Ipv4'].get('hostname', None)
                        data["alias_add"]=alias_add
                        data["alias_mask"]=alias_mask
                        data["reject"]=reject
                        data["hostname"]=hostname
                        #call function to convert mask format to bits
                        if alias_mask is not None:
                            alias_mask=convert_to_subnet_mask(alias_mask)
                        ####
                        if typeDHCP4=="Base" :
                            #contenu de dhclient.conf dhcp Base
                            configContenu=return_config_base_IPV4(ifname,reject,hostname,alias_add,alias_mask)
                            jsonIPV4={
                    "nameInterface":nameInterface,"ifname":ifname,
                    "typeIP4":setuptypeIP4,"typeDHCP":typeDHCP4,
                    "alias_add":alias_add,"alias_mask":alias_mask,
                    "reject":reject,"hostname":hostname}
                        if typeDHCP4=="Advanced":
                            timeout =  None if data['value_setup_Ipv4'].get('timeout', None) == "" else  data['value_setup_Ipv4'].get('timeout', None)
                            retry =  None if data['value_setup_Ipv4'].get('retry', None) == "" else  data['value_setup_Ipv4'].get('retry', None)
                            select_timeout =  None if data['value_setup_Ipv4'].get('select_timeout', None) == "" else  data['value_setup_Ipv4'].get('select_timeout', None)
                            reboot =  None if data['value_setup_Ipv4'].get('reboot', None) == "" else  data['value_setup_Ipv4'].get('reboot', None)
                            backoff =  None if data['value_setup_Ipv4'].get('backoff', None) == "" else  data['value_setup_Ipv4'].get('backoff', None)
                            initial_interval =  None if data['value_setup_Ipv4'].get('initial_interval', None) == "" else  data['value_setup_Ipv4'].get('initial_interval', None)
                            send_options_dhcp_client =  None if data['value_setup_Ipv4'].get('send_options_dhcp_client', None) == "" else  data['value_setup_Ipv4'].get('send_options_dhcp_client', None)
                            send_options_lease_time  =  None if data['value_setup_Ipv4'].get('send_options_lease_time ', None) == "" else  data['value_setup_Ipv4'].get('send_options_lease_time', None)
                            request =  None if data['value_setup_Ipv4'].get('request', None) == "" else  data['value_setup_Ipv4'].get('request', None)
                            require =  None if data['value_setup_Ipv4'].get('require', None) == "" else  data['value_setup_Ipv4'].get('require', None)
                            supersede_domaine_name =  None if data['value_setup_Ipv4'].get('supersede_domaine_name', None) == "" else  data['value_setup_Ipv4'].get('supersede_domaine_name', None)
                            prepend_domain_server =  None if data['value_setup_Ipv4'].get('prepend_domain_server', None) == "" else  data['value_setup_Ipv4'].get('prepend_domain_server', None)
                            data["timeout"]=timeout
                            data["retry"]=retry
                            data["select_timeout"]=select_timeout
                            data["reboot"]=reboot
                            data["backoff"]=backoff
                            data["initial_interval"]=initial_interval
                            data["send_options_dhcp_client"]=send_options_dhcp_client
                            data["send_options_lease_time"]=send_options_lease_time
                            data["request"]=request
                            data["require"]=require
                            data["supersede_domaine_name"]=supersede_domaine_name
                            data["prepend_domain_server"]=prepend_domain_server
                        #contenu de dhclient.conf dhcp advanced
                            configContenu=return_config_advanced_IPV4(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,send_options_dhcp_client,supersede_domaine_name,prepend_domain_server,send_options_lease_time,request,require)
                            jsonIPV4={
                    "nameInterface":nameInterface,"ifname":ifname,
                    "typeIP4":setuptypeIP4,"typeDHCP":typeDHCP4,
                    "alias_add":alias_add,"alias_mask":alias_mask,
                    "reject":reject,"hostname":hostname,
                    "timeout":timeout,"retry":retry,
                    "select_timeout":select_timeout,"reboot":reboot,
                    "backoff":backoff,"initial_interval":initial_interval,
                    "dhcp_client":send_options_dhcp_client,
                    "lease_time":send_options_lease_time,
                    "request":request,"require":require,
                    "domaine_name":supersede_domaine_name,
                    "domain_server":prepend_domain_server
                    }
                        #add commands of create file dhclient to list of commandes to execute    
                        commandes_final+=create_file_IPV4(ifname,configContenu)
                        #call function to convert address to dhcp advanced /Base  in service
                        commandes,output_service,cmd_final_ipv4=update_conn_dhcp_IPV4(output_service,ifname,uuid)
                # match typeIP6:
                    # case "None":
                    #     pass
                    # case "static":
                    #     #call function to convert address to static ipv6
                    #     commandesIPV6,output_service,cmd_final_ipv6=update_conn_static_ipv6(output_service,ifname,ip6_address,netmask6)
                    # case "dhcp":
                    #     if typeDHCP=="Base" :
                    #     #contenu de dhclient.conf dhcp Base
                    #         configContenu=return_config_base_ipv6(ifname,id,Request_only,Prefix_delegation,prefix_hint,IPv4_connectivity,VLAN_priority)
                    #     if typeDHCP=="Advanced":
                    #     #contenu de dhclient.conf dhcp advanced
                    #         configContenu=return_config_advanced_ipv6(ifname,id,Request_only,Prefix_delegation,prefix_hint,IPv4_connectivity,VLAN_priority)
                    #     #add commands of create file dhclient to list of commandes to execute    
                    #     commandes_final+=create_file_ipv6(ifname,configContenu)
                    #     #call function to convert address to dhcp advanced /Base  in service
                    #     commandesIPV6,output_service,cmd_final_ipv6=update_conn_dhcp_ipv6(output_service,ifname)
                                #clean list of cmd to block address
                
                
                ##for generic config 
                cmds=[]       
                cmds,output_service,cmd_final_Gen=generic_config(output_service,ifname,speed_duplex,addmac,mtuV,mssV,genericConfigObject)
                ##blocages des adresses
                cmdsBlock=[]
                configs=[]
                #call function to block address
                configs,cmdsBlock,output_service,cmd_final_Block=block_address_commandes(output_service,ifname,bogon_aux,private_aux,interfaceObject)
                #clean list of cmd to block address
                cmdsBlock = [x for x in cmdsBlock if x not in output_service]
                #contenu final des cmds pour lancer le service (execStart)
                commandes+=commandesIPV6+cmds+cmdsBlock
                ###call function to add all commandes to the service
                output_service = add_cmd(output_service,commandes)
                #ajouter au liste des commandes finales à executer (ssh.exec_command) 
                commandes_final+=configs+cmd_final_ipv4+cmd_final_ipv6+cmd_final_Gen+cmd_final_Block
                cmd_asguard="""sudo cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output_service))
                # print("1111",run_all_commands(commandes_final,setuptypeIP4,typeDHCP4))
                if run_all_commands(commandes_final,setuptypeIP4,typeDHCP4,10) is True:
                    stdin, stdout, stderr = ssh.exec_command(cmd_asguard)  
                    if  (stderr.read().decode('utf-8')==""):
                        if setuptypeIP4=="dhcp":
                            ##function to get gateway if typeIPV4 est DHCP Base or Advanced
                            gwaddr4,metric,default_aux,far_aux,multiwan_aux=get_gateway_dhcp(ifname,ssh)
                            jsonIPV4["addrgw"]=gwaddr4
                            ip_address4,netmask4=get_address_dhcp(ifname,ssh)
                            # print(ip_address4,"======>",netmask4)
                            jsonIPV4["ip_address"]=ip_address4
                            jsonIPV4["netmask"]=netmask4
                            # print(gwaddr4,metric,default_aux,far_aux,multiwan_aux)
                            if gwaddr4 is not None:
                                dataGw={
                                "gwname":"DHCP_GW_{}".format(name_interface),
                                "gwaddress":"{}".format(gwaddr4),
                                "description":"DHCP gateway generated automatically ",
                                "default_aux":default_aux,
                                "far_aux":far_aux,
                                "multiwan_aux":multiwan_aux
                                    }
                                aux_exist=Gateway.objects.filter(Q(gwaddress=gwaddr4) & Q(staticgw=False)).exists()
                                if not aux_exist:
                                    aux_GW=add_gateway_DB(dataGw)
                                else:
                                    GatewayObject=Gateway.objects.get(Q(gwaddress=gwaddr4) & Q(staticgw=False) )
                                    idGW=GatewayObject.id
                                    aux_GW=update_gateway_DB(dataGw,idGW)
                                if aux_GW is True:
                                    addGatewayInterfaceDB(GatewayObject,name_interface,metric)  
                                else:
                                    msg=aux_GW
                                    status=400
                            else:
                                msg="Gateway DHCP not found!"
                                status=400        
                        #update changes in DB ip4
                        aux_ipv4=update_DB(id_interface,jsonIPV4,IP4Config,IP4ConfigSerializer)
                        #update changes in DB ip6
                        # update_DB(id,data,IP6Config,IP6ConfigSerializer)
                        #update changes in DB generic config
                        aux_gen=update_DB(id_interface,data,GenericConfig,GenericConfigSerializer)
                        #update changes in DB interface config
                        aux_inter=update_interface_table(name_interface,data,InterfaceSerializer)
                        # print(aux_ipv4 and aux_gen and aux_inter)
                        if aux_ipv4 is True:
                            if aux_gen is True:
                                if aux_inter is True:
                                    msg="Your interface {} was configured Successfully!!".format(name_interface)
                                    status=200
                                else:
                                    msg=aux_inter
                                    status=400
                            else:
                                msg=aux_gen
                                status=400
                        else:
                            msg=aux_ipv4
                            status=400
                    else:
                        msg=stderr.read().decode('utf-8')
                        status=400        
                else:
                    msg=run_all_commands(commandes_final,setuptypeIP4,typeDHCP4,10)
                    status=400
            else:
                msg="Failed to configure Network Service not found!!"
                status=400
    return JsonResponse({"Message:": msg},status=status)

##API to delete config 
###########################
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_interface(request,id):
    msg="failed to delete interface!"
    print(request.method=="DELETE")
    if request.method=="DELETE":
        print("aaaa",Interface.objects.filter(id=id).exists())
        if (Interface.objects.filter(id=id).exists()):
                interfaceObject = Interface.objects.get(id=id)
                ifname=interfaceObject.ifname
                output_service,error= get_old_config()
                if not error:
                    print(desactiver_interface_remote(ifname,output_service))
                    if desactiver_interface_remote(ifname,output_service):
                        interfaceObject.delete() 
                        msg="Delete interface Successfully!!"
                
    return JsonResponse({"mssg":msg})
            
            
@api_view(['GET'])
@permission_classes([AllowAny])            
def AllInterfaces(request):
    list_interface = []
    if (request.method == 'GET'):
        interfaces = Interface.objects.all()
        interfaceDict = serializers.serialize("json", interfaces)
        res = json.loads(interfaceDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_interface.append(res[i]['fields'])
        # return a Json response
        return JsonResponse(list_interface, safe=False)
    
def GetInformationsByInterface(request,name_interface):
    info={}
    interface={}
    if (request.method == 'GET'):
        interfaceObject = Interface.objects.get(name_interface=name_interface)
        interface['id']=interfaceObject.id
        interface['ifname']=interfaceObject.ifname
        interface['private_aux']=interfaceObject.private_aux
        interface['bogon_aux']=interfaceObject.bogon_aux
        interface['service_status']=interfaceObject.service_status
        interface['name_interface']=interfaceObject.name_interface
        interface['description']=interfaceObject.description
        info['interface']=interface
        print({"interfaceObject":interfaceObject})
        genericConfigObject = GenericConfig.objects.filter(interface_id=interfaceObject.id)
        genericConfigDict = serializers.serialize("json", genericConfigObject)
        res = json.loads(genericConfigDict)
        genericConfigList = list(genericConfigDict)
        print({"genericConfigList":res})
        if res != []:
            id = res[0]['pk']
            res[0]['fields']['id'] = id
            res[0].pop('model')
            res[0].pop('pk')
            res[0]['fields'].pop('interface')
            info['genericConfig']=res[0]['fields']
        else:
            info['genericConfig']=[]
        # print({"res":res[0]['fields']})
        IPV4ConfigObject = IP4Config.objects.filter(interface_id=interfaceObject.id)
        print({"IPV4ConfigObject":IPV4ConfigObject})
        IPV4ConfigObjectDict = serializers.serialize("json", IPV4ConfigObject)
        resultat = json.loads(IPV4ConfigObjectDict)
        if resultat != []:
            id = resultat[0]['pk']
            resultat[0]['fields']['id'] = id
            resultat[0].pop('model')
            resultat[0].pop('pk')
            resultat[0]['fields'].pop('interface')
            info['IPV4Config']=resultat[0]['fields']
        else:
            info['IPV4Config']=[]
        # print({"resultat":resultat[0]['fields']})
    return JsonResponse(info)