from django.http import JsonResponse
from network.serializers import *
from .models import *
from settings.serializers import *
from rest_framework.parsers import JSONParser
import json
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core import serializers
from authentification.views import *
from .functions import *
from django.views.decorators.csrf import csrf_exempt
from gateway.models import *
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
# @api_view(['PUT'])
# @authentication_classes([AllowAny])
# @authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
@csrf_exempt
def conf(request,name_interface):
    msg="Failed to configure Network!"
    list_metric = []
    if (request.method == 'PUT'):
        interfaceObject = Interface.objects.get(name_interface=name_interface)
        id_interface = interfaceObject.id
        print("id_interface",id_interface)
        #get object of interface type
        deviceInfo = device_nameInterface(name_interface)
        print({"ifname":deviceInfo.ifname})
        print({"name_interface":deviceInfo.name_interface})
        #get interface name to execute command systeme
        ifname=deviceInfo.ifname
        nameInterface=deviceInfo.name_interface
        ####
        # parse the incoming information
        data = JSONParser().parse(request)
        # return JsonResponse({"data":data})
        setuptypeIP4 = data.get('setuptypeIP4')
        description = data.get('description')
        bogon_aux = data.get('bogon_aux')
        private_aux = data.get('private_aux')
        # addmac = data.get('addmac')
        mtuV = data.get('mtuV')
        mssV = data.get('mssV')
        speed_duplex = data.get('speed_duplex') 
        commandes=[]
        commandes_final=[]
        commandesIPV6=[]
        cmd_final_ipv6=[]
        cmd_final_ipv4=[]

        ##get old configuration in service
        output_service,error=get_old_config()
        if error:
            msg=error
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
                        addmac = data.get('addmac')
                         #call function to convert address to None
                        commandes,output_service,cmd_final_ipv4=update_conn_None_IPV4(output_service,ifname)
                    case "static":
                        typeDHCP4=''
                        addmac = data.get('addmac')
                        ip_address4 = data.get('value_setup_Ipv4')['ip_address4']
                        netmask4 = data.get('value_setup_Ipv4')['netmask4']
                        gateway4=data.get('value_setup_Ipv4')['gateway4']
                        print({"gateway": gateway4['value']})
                        GatewayObject = Gateway.objects.get(gwaddress=gateway4['value'])
                        print({"IdGateway":GatewayObject.id})
                        default_aux=GatewayObject.default_aux
                        far_aux=GatewayObject.far_aux
                        multiWan_aux=GatewayObject.multiwan_aux
                        multiWan_aux=GatewayObject.multiwan_aux
                        addrgw=GatewayObject.gwaddress
                        metric=0
                        allGatewayInterface = GatewayInterface.objects.all()
                        if multiWan_aux:
                            for i in allGatewayInterface:
                                list_metric.append(i.metric)
                            metric=differentMetric(list_metric)
                            print("metric==",metric)

                        cmdgw=return_Gateway_system(ifname,addrgw,far_aux,multiWan_aux,metric)
                        addGatewayInterfaceDB(GatewayObject,name_interface,metric)
                        #gateway ??????????
                        #call function to convert address to static
                        commandes,output_service,cmd_final_ipv4=update_conn_static_IPV4(output_service,ifname,ip_address4,netmask4,cmdgw)
                        jsonIPV4={
                    "nameInterface":nameInterface,"ifname":ifname,
                    "ip_address":ip_address4,"netmask":netmask4,
                    "typeIP4":setuptypeIP4}
                    case "dhcp":
                        addmac = None
                        typeDHCP4 = data.get('value_setup_Ipv4')['typeDHCP4']
                        if typeDHCP4=="Base" :
                            alias_add = data.get('value_setup_Ipv4')['alias_add']
                            alias_mask = data.get('value_setup_Ipv4')['alias_mask']
                            reject = data.get('value_setup_Ipv4')['reject']
                            hostname = data.get('value_setup_Ipv4')['hostname']
                            #call function to convert mask format to bits
                            alias_mask=convert_to_subnet_mask(alias_mask)
                            #contenu de dhclient.conf dhcp Base
                            configContenu=return_config_base_IPV4(ifname,reject,hostname,alias_add,alias_mask)
                            jsonIPV4={
                    "nameInterface":nameInterface,"ifname":ifname,
                    "typeIP4":setuptypeIP4,"typeDHCP":typeDHCP4,
                    "alias_add":alias_add,"alias_mask":alias_mask,
                    "reject":reject,"hostname":hostname}
                        if typeDHCP4=="Advanced":
                            alias_add = data.get('value_setup_Ipv4')['alias_add']
                            alias_mask = data.get('value_setup_Ipv4')['alias_mask']
                            reject = data.get('value_setup_Ipv4')['reject']
                            hostname = data.get('value_setup_Ipv4')['hostname']
                            timeout = data.get('value_setup_Ipv4')['timeout']
                            retry = data.get('value_setup_Ipv4')['retry']
                            select_timeout = data.get('value_setup_Ipv4')['select_timeout']
                            reboot = data.get('value_setup_Ipv4')['reboot']
                            backoff = data.get('value_setup_Ipv4')['backoff']
                            initial_interval = data.get('value_setup_Ipv4')['initial_interval']
                            send_options_dhcp_client = data.get('value_setup_Ipv4')['send_options_dhcp_client']
                            send_options_lease_time = data.get('value_setup_Ipv4')['send_options_lease_time']
                            request = data.get('value_setup_Ipv4')['request']
                            require = data.get('value_setup_Ipv4')['require']
                            supersede_domaine_name = data.get('value_setup_Ipv4')['supersede_domaine_name']
                            prepend_domain_server = data.get('value_setup_Ipv4')['prepend_domain_server']
                            #call function to convert mask format to bits
                            alias_mask=convert_to_subnet_mask(alias_mask)
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
                        commandes,output_service,cmd_final_ipv4=update_conn_dhcp_IPV4(output_service,ifname)
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
                cmds,output_service,cmd_final_Gen=generic_config(output_service,ifname,speed_duplex,addmac,mtuV,mssV)
                ##blocages des adresses
                cmdsBlock=[]
                configs=[]
                #call function to block address
                configs,cmdsBlock,output_service,cmd_final_Block=block_address_commandes(output_service,ifname,bogon_aux,private_aux)
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
                if run_all_commands(commandes_final,setuptypeIP4,typeDHCP4,5):
                    stdin, stdout, stderr = ssh.exec_command(cmd_asguard)  
                    if not (stderr.read().decode('utf-8')):
                        if setuptypeIP4=="dhcp":
                            ##function to get gateway if typeIPV4 est DHCP Base or Advanced
                            gwaddr=get_gateway_dhcp(ifname,ssh)
                            if gwaddr is not None:
                                GatewayObject = Gateway.objects.get(gwaddress=gwaddr)
                                metric=0 
                                addGatewayInterfaceDB(GatewayObject,name_interface,metric)
                        #update changes in DB ip4
                        aux_ipv4=update_DB(id_interface,jsonIPV4,IP4Config,IP4ConfigSerializer)
                        #update changes in DB ip6
                        # update_DB(id,data,IP6Config,IP6ConfigSerializer)
                        #update changes in DB generic config
                        aux_gen=update_DB(id_interface,data,GenericConfig,GenericConfigSerializer)
                        #update changes in DB interface config
                        aux_inter=update_interface_table(name_interface,data,InterfaceSerializer)
                        print(aux_ipv4 and aux_gen and aux_inter)
                        if aux_ipv4 and aux_gen and aux_inter:
                            msg="Your interface {} was configured Successfully!!".format(name_interface)

                

        
    return JsonResponse({"Message:": msg})

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
            