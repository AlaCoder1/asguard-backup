from django.http import JsonResponse
from backend.network.serializers import *
from backend.server_dhcp4.functions import create_dhcpv4_db, delete_dhcp4_server
from .models import *
from backend.settings.serializers import *
import json
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import  AllowAny
from backend.authentification.views import *
from .functions_ipv4 import *
from .functions_ipv6 import *
from .functions_generic_conf import *
from .functions_block_address import *
from backend.gateway.models import *
from backend.gateway.functions import *
from django.db.models import Q
from django.core import serializers

###########################
@swagger_auto_schema(
    method='PUT',
    request_body=GatewaySerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO CONFIG NETWORK INTERFACES",
    operation_description="This API help to configure advanced parametres in network and configure interfaces networrk to get addresses IPV4 and IPV6 in system then in database",
)
                
########################### 
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def conf(request,name_interface):
    msg="Failed to configure Network!"
    status=400
    list_metric = []
    if (request.method == 'PUT'):
        #get object of interface type
        deviceInfo = device_name_interface(name_interface)
        #get interface name to execute command systeme
        ifname=deviceInfo.ifname
        id_interface = deviceInfo.id
        ###### get object Config service
        genericConfigObject=None
        if GenericConfig.objects.filter(interface_id=id_interface).exists():
            genericConfigObject=GenericConfig.objects.get(interface_id=id_interface)
        ###############
        ##get uuid to reference to connection
        uuid=get_uuid_con(ifname)
        ####
        if uuid is not None:
            # parse the incoming information
            data = request.data
            setuptypeIP4 = data.get('setuptypeIP4')
            ## for ipv6
            setuptypeIP6 = data.get('setuptypeIP6')
            ####
            description = data.get('description')
            bogon_aux = data.get('bogon_aux')
            private_aux = data.get('private_aux')
            mtuv =  None if data.get('mtuv', None) == "" else data.get('mtuv', None)
            mssv =  None if data.get('mssv', None) == "" else data.get('mssv', None)
            speed_duplex =  None if data.get('speed_duplex', None) == "" else data.get('speed_duplex', None)
            addmac =  None if data.get('addmac', None) == "" else data.get('addmac', None)
            data["mtuv"]=mtuv
            data["mssv"]=mssv
            data["speed_duplex"]=speed_duplex
            data["addmac"]=addmac
            commandes=[]
            commandes_final=[]
            commandes_ipv6=[]
            cmd_final_ipv6=[]
            cmd_final_ipv4=[]
            ##get old configuration in service
            output_service,error=get_old_config()
            if error!="" or len(output_service)==0:
                msg="Failed to configure Network!"
                status=400
            else:
                    #delete empty value
                    output_service = [x for x in output_service if x]
                    ##add requirement service
                    output_service=add_requirement(ifname,output_service)
                    ###set gatewayObject to None
                    GatewayObject=None
                    ##IPV4 configuration cases 
                    match setuptypeIP4.lower():
                        case "none":
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
                            addrgw4=GatewayObject.gwaddress
                            ############# generete metric statiquement
                            metric=0
                            allGatewayInterface = GatewayInterface.objects.all()
                            if multiWan_aux:
                                for i in allGatewayInterface:
                                    list_metric.append(i.metric)
                                metric=differentMetric(list_metric)
                            cmdgw4=return_gateway_system(uuid,addrgw4,far_aux,multiWan_aux,metric)
                            ipv4_gw_interface=True
                            addGatewayInterfaceDB(GatewayObject,name_interface,metric,ipv4_gw_interface)
                            #call function to convert address to static
                            commandes,output_service,cmd_final_ipv4=update_conn_static_IPV4(output_service,ifname,uuid,ip_address4,netmask4,cmdgw4)
                            jsonIPV4={
                        "name_interface":name_interface,"ifname":ifname,
                        "ip_address":ip_address4,"netmask":netmask4,
                        "typeip4":setuptypeIP4}
                        case "dhcp":
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
                            alias_mask_converted=None
                            if alias_mask is not None:
                                alias_mask_converted=convert_to_subnet_mask(alias_mask)
                            ipv4_gw_interface=True
                            ####
                            if typeDHCP4.lower()=="base" :
                                #contenu de dhclient.conf dhcp Base
                                configContenu=return_config_base_IPV4(ifname,reject,hostname,alias_add,alias_mask_converted)
                                jsonIPV4={
                        "name_interface":name_interface,"ifname":ifname,
                        "typeip4":setuptypeIP4,"typedhcp":typeDHCP4,
                        "alias_add":alias_add,"alias_mask":alias_mask,
                        "reject":reject,"hostname":hostname}
                            if typeDHCP4.lower()=="advanced":
                                timeout =  None if data['value_setup_Ipv4'].get('timeout', None) == "" else  data['value_setup_Ipv4'].get('timeout', None)
                                retry =  None if data['value_setup_Ipv4'].get('retry', None) == "" else  data['value_setup_Ipv4'].get('retry', None)
                                select_timeout =  None if data['value_setup_Ipv4'].get('select_timeout', None) == "" else  data['value_setup_Ipv4'].get('select_timeout', None)
                                reboot =  None if data['value_setup_Ipv4'].get('reboot', None) == "" else  data['value_setup_Ipv4'].get('reboot', None)
                                backoff =  None if data['value_setup_Ipv4'].get('backoff', None) == "" else  data['value_setup_Ipv4'].get('backoff', None)
                                initial_interval =  None if data['value_setup_Ipv4'].get('initial_interval', None) == "" else  data['value_setup_Ipv4'].get('initial_interval', None)
                                dhcp_client =  None if data['value_setup_Ipv4'].get('dhcp_client', None) == "" else  data['value_setup_Ipv4'].get('dhcp_client', None)
                                lease_time  =  None if data['value_setup_Ipv4'].get('lease_time ', None) == "" else  data['value_setup_Ipv4'].get('lease_time', None)
                                request =  None if data['value_setup_Ipv4'].get('request', None) == "" else  data['value_setup_Ipv4'].get('request', None)
                                require =  None if data['value_setup_Ipv4'].get('require', None) == "" else  data['value_setup_Ipv4'].get('require', None)
                                domain_name =  None if data['value_setup_Ipv4'].get('domain_name', None) == "" else  data['value_setup_Ipv4'].get('domain_name', None)
                                domain_server =  None if data['value_setup_Ipv4'].get('domain_server', None) == "" else  data['value_setup_Ipv4'].get('domain_server', None)
                                data["timeout"]=timeout
                                data["retry"]=retry
                                data["select_timeout"]=select_timeout
                                data["reboot"]=reboot
                                data["backoff"]=backoff
                                data["initial_interval"]=initial_interval
                                data["dhcp_client"]=dhcp_client
                                data["lease_time"]=lease_time
                                data["request"]=request
                                data["require"]=require
                                data["domain_name"]=domain_name
                                data["domain_server"]=domain_server
                            #contenu de dhclient.conf dhcp advanced
                                configContenu=return_config_advanced_IPV4(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domain_name,domain_server,lease_time,request,require)
                                jsonIPV4={
                        "name_interface":name_interface,"ifname":ifname,
                        "typeip4":setuptypeIP4,"typedhcp":typeDHCP4,
                        "alias_add":alias_add,"alias_mask":alias_mask,
                        "reject":reject,"hostname":hostname,
                        "timeout":timeout,"retry":retry,
                        "select_timeout":select_timeout,"reboot":reboot,
                        "backoff":backoff,"initial_interval":initial_interval,
                        "dhcp_client":dhcp_client,
                        "lease_time":lease_time,
                        "request":request,"require":require,
                        "domain_name":domain_name,
                        "domain_server":domain_server
                        }
                            #add commands of create file dhclient to list of commandes to execute    
                            commandes_final+=create_file_IPV4(ifname,configContenu)
                            #call function to convert address to dhcp advanced /Base  in service
                            commandes,output_service,cmd_final_ipv4=update_conn_dhcp_IPV4(output_service,ifname,uuid)
                    jsonIPV6=data
                    if  setuptypeIP6 is not None:
                        match setuptypeIP6.lower():
                            case "none":
                                pass
                            case "static":
                                typeDHCP6=''
                                ip_address6 =  None if data['value_setup_Ipv6'].get('ip_address6', None) == "" else  data['value_setup_Ipv6'].get('ip_address6', None)
                                netmask6 =  None if data['value_setup_Ipv6'].get('netmask6', None) == "" else  data['value_setup_Ipv6'].get('netmask6', None)
                                gateway6 =  None if data['value_setup_Ipv6']['gateway6'].get('value', None) == "" else  data['value_setup_Ipv6']['gateway6'].get('value', None)
                                GatewayObject6=Gateway.objects.get(Q(gwaddress=gateway6) & Q(staticgw=True) )
                                #call function to convert address to static ipv6
                                #################
                                default_aux6=GatewayObject6.default_aux
                                far_aux6=GatewayObject6.far_aux
                                multiWan_aux6=GatewayObject6.multiwan_aux
                                addrgw6=GatewayObject6.gwaddress
                                ############# generete metric statiquement
                                metric=0
                                allGatewayInterface = GatewayInterface.objects.all()
                                if multiWan_aux:
                                    for i in allGatewayInterface:
                                        list_metric.append(i.metric)
                                    metric=differentMetric(list_metric)
                                cmdgw6=return_gateway6_system(uuid,addrgw6,far_aux6,multiWan_aux6,metric)
                                ipv4_gw_interface=False
                                addGatewayInterfaceDB(GatewayObject6,name_interface,metric,ipv4_gw_interface)
                                #call function to convert address to static
                                commandes,output_service,cmd_final_ipv6=update_conn_static_IPV6(output_service,ifname,uuid,ip_address6,netmask6,cmdgw6)
                                jsonIPV6={
                                "name_interface":name_interface,"ifname":ifname,
                                "ip_address6":ip_address6,"netmask6":netmask6,
                                "typeip6":setuptypeIP6}
                            case "dhcp":
                                typeDHCP6 = data.get('value_setup_Ipv6')['typeDHCP6']
                                #Base and Advanced
                                ipv4_connectivity =  None if data['value_setup_Ipv6'].get('ipv4_connectivity', None) == "" else  data['value_setup_Ipv6'].get('ipv4_connectivity', None)
                                vlan_priority =  None if data['value_setup_Ipv6'].get('vlan_priority', None) == "" else  data['value_setup_Ipv6'].get('vlan_priority', None)
                                if typeDHCP6.lower()=="base" :
                                    ###Base
                                    request_only =  None if data['value_setup_Ipv6'].get('request_only', None) == "" else  data['value_setup_Ipv6'].get('request_only', None)
                                    prefix_delegation_size =  None if data['value_setup_Ipv6'].get('prefix_delegation_size', None) == "" else  data['value_setup_Ipv6'].get('prefix_delegation_size', None)
                                    prefix_hint =  None if data['value_setup_Ipv6'].get('prefix_hint', None) == "" else  data['value_setup_Ipv6'].get('prefix_hint', None)
                                #contenu de dhclient.conf dhcp Base
                                    config_contenu_ipv6=return_config_base_ipv6(ifname,id_interface,request_only,prefix_delegation_size,prefix_hint,ipv4_connectivity,vlan_priority)
                                    jsonIPV6={
                                        "typeip6":setuptypeIP6,"typedhcp6":typeDHCP6,
                                        "request_only":request_only,"prefix_delegation_size":prefix_delegation_size,
                                        "prefix_hint":prefix_hint,"ipv4_connectivity":ipv4_connectivity,
                                        "vlan_priority":vlan_priority
                                        }
                                if typeDHCP6.lower()=="advanced":
                                    ###Advanced
                                    #interface status
                                    information_only =  None if data['value_setup_Ipv6'].get('information_only', None) == "" else  data['value_setup_Ipv6'].get('information_only', None)
                                    send_options =  None if data['value_setup_Ipv6'].get('send_options', None) == "" else  data['value_setup_Ipv6'].get('send_options', None)
                                    request_options =  None if data['value_setup_Ipv6'].get('request_options', None) == "" else  data['value_setup_Ipv6'].get('request_options', None)
                                    script =  None if data['value_setup_Ipv6'].get('script', None) == "" else  data['value_setup_Ipv6'].get('script', None)
                                    #####
                                    non_temporary =  None if data['value_setup_Ipv6'].get('non_temporary', None) == "" else  data['value_setup_Ipv6'].get('non_temporary', None)
                                    #### if non_temporary is true
                                    id_assoc =  None if data['value_setup_Ipv6'].get('id_assoc', None) == "" else  data['value_setup_Ipv6'].get('id_assoc', None)
                                    address =  None if data['value_setup_Ipv6'].get('address', None) == "" else  data['value_setup_Ipv6'].get('address', None)
                                    nlifetime =  None if data['value_setup_Ipv6'].get('nlifetime', None) == "" else  data['value_setup_Ipv6'].get('nlifetime', None)
                                    nvalid_time =  None if data['value_setup_Ipv6'].get('nvalid_time', None) == "" else  data['value_setup_Ipv6'].get('nvalid_time', None)
                                    #####
                                    prefix_delegation =  None if data['value_setup_Ipv6'].get('prefix_delegation', None) == "" else  data['value_setup_Ipv6'].get('prefix_delegation', None)
                                    #### if prefix_delegation is true
                                    id_assoc_pd =  None if data['value_setup_Ipv6'].get('id_assoc_pd', None) == "" else  data['value_setup_Ipv6'].get('id_assoc_pd', None)
                                    ipv6_prefix =  None if data['value_setup_Ipv6'].get('ipv6_prefix', None) == "" else  data['value_setup_Ipv6'].get('ipv6_prefix', None)
                                    plifetime =  None if data['value_setup_Ipv6'].get('plifetime', None) == "" else  data['value_setup_Ipv6'].get('plifetime', None)
                                    pvalid_time =  None if data['value_setup_Ipv6'].get('pvalid_time', None) == "" else  data['value_setup_Ipv6'].get('pvalid_time', None)
                                    ##auth
                                    authname =  None if data['value_setup_Ipv6'].get('authname', None) == "" else  data['value_setup_Ipv6'].get('authname', None)
                                    protocol =  None if data['value_setup_Ipv6'].get('protocol', None) == "" else  data['value_setup_Ipv6'].get('protocol', None)
                                    algorithm =  None if data['value_setup_Ipv6'].get('algorithm', None) == "" else  data['value_setup_Ipv6'].get('algorithm', None)
                                    rdm =  None if data['value_setup_Ipv6'].get('rdm', None) == "" else  data['value_setup_Ipv6'].get('rdm', None)
                                    ##key info
                                    keyname =  None if data['value_setup_Ipv6'].get('keyname', None) == "" else  data['value_setup_Ipv6'].get('keyname', None)
                                    royaume =  None if data['value_setup_Ipv6'].get('royaume', None) == "" else  data['value_setup_Ipv6'].get('royaume', None)
                                    keyid =  None if data['value_setup_Ipv6'].get('keyid', None) == "" else  data['value_setup_Ipv6'].get('keyid', None)
                                    secret =  None if data['value_setup_Ipv6'].get('secret', None) == "" else  data['value_setup_Ipv6'].get('secret', None)
                                    expire =  None if data['value_setup_Ipv6'].get('expire', None) == "" else  data['value_setup_Ipv6'].get('expire', None)
                                    ##
                                    ##contenu de dhcp6c.conf dhcp advanced
                                    config_contenu_ipv6=return_config_advanced_ipv6(ifname,
                                    id_interface,ipv4_connectivity,vlan_priority,information_only,
                                    send_options,request_options,script,non_temporary,id_assoc,address,nlifetime,nvalid_time,
                                    prefix_delegation,id_assoc_pd,ipv6_prefix,plifetime,pvalid_time,
                                    authname,protocol,algorithm,rdm,keyname,royaume,keyid,secret,expire)
                                    jsonIPV6={
                                    "typeip6":setuptypeIP6,"typedhcp6":typeDHCP6,
                                    "information_only":information_only,"send_options":send_options,
                                    "request_options":request_options,"script":script,
                                    "non_temporary":non_temporary,"id_assoc":id_assoc,
                                    "address":address,"nlifetime":nlifetime,"nvalid_time":nvalid_time,
                                    "prefix_delegation":prefix_delegation,
                                    "id_assoc_pd":id_assoc_pd,"ipv6_prefix":ipv6_prefix,"plifetime":plifetime,
                                    "pvalid_time":pvalid_time,"authname":authname,"protocol":protocol,
                                    "algorithm":algorithm,"rdm":rdm,"keyname":keyname,"royaume":royaume,
                                    "keyid":keyid,"secret":secret,"expire":expire,
                                    "ipv4_connectivity":ipv4_connectivity,"vlan_priority":vlan_priority
                                        }
                                #add commands of create file dhclient to list of commandes to execute    
                                commandes_final+=create_file_ipv6(ifname,config_contenu_ipv6)
                                #call function to convert address to dhcp advanced /Base  in service
                                commandes_ipv6,output_service,cmd_final_ipv6=update_conn_dhcp_ipv6(output_service,ifname,uuid)
                    ##for generic config 
                    cmds=[]       
                    cmds,output_service,cmd_final_Gen=generic_config(output_service,ifname,speed_duplex,addmac,mtuv,mssv,genericConfigObject)
                    ##blocages des adresses
                    cmdsBlock=[]
                    configs=[]
                    #call function to block address
                    configs,cmdsBlock,output_service,cmd_final_Block=block_address_commandes(output_service,ifname,bogon_aux,private_aux,deviceInfo)
                    #clean list of cmd to block address
                    cmdsBlock = [x for x in cmdsBlock if x not in output_service]
                    #contenu final des cmds pour lancer le service (execStart)
                    commandes+=commandes_ipv6+cmds+cmdsBlock
                    ###call function to add all commandes to the service
                    output_service = add_cmd(output_service,commandes)
                    ###cmd to refresh conf in system Network Manager
                    cmd_final_conf=refresh_conf_system(uuid)
                    #ajouter au liste des commandes finales à executer  
                    commandes_final+=configs+cmd_final_ipv4+cmd_final_ipv6+cmd_final_conf+cmd_final_Gen+cmd_final_Block
                    cmd_asguard="""sudo cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output_service))
                    aux_run=run_all_commands(commandes_final,setuptypeIP4,10)
                    if aux_run is True:
                        _, error=run_command(cmd_asguard)
                        if  (error==""):
                            ## for dhcp 4
                            if setuptypeIP4 is None or setuptypeIP4.lower()=="static" :
                                aux_gw_dhcp=True
                            if setuptypeIP4.lower()=="dhcp":
                                #function to get dhcp address and mask
                                ip_address4,netmask4=get_address_dhcp(ifname,"4")
                                jsonIPV4["ip_address"]=ip_address4
                                jsonIPV4["netmask"]=netmask4
                                ###
                                ##function to get gateway if typeIPV4 est DHCP Base or Advanced
                                gwaddr4,metric,default_aux,far_aux,multiwan_aux=get_gateway_dhcp(ifname,"4")
                                aux_gw_dhcp=save_gateways_database(gwaddr4,name_interface,default_aux,far_aux,multiwan_aux,metric,True,True)
                            ## for dhcp 6
                            aux_gw6_dhcp=True
                            if setuptypeIP4 is None or setuptypeIP4.lower()=="static" :
                                    aux_gw6_dhcp=True
                            if setuptypeIP6 is not None and setuptypeIP6.lower()=="dhcp":
                                #function to get dhcp address6 and mask6
                                ip_address6,netmask6=get_address_dhcp(ifname,"6")
                                jsonIPV6["ip_address6"]=ip_address6
                                jsonIPV6["netmask6"]=netmask6
                                ###
                                ##function to get gateway if typeIPV6 est DHCP Base or Advanced
                                gwaddr6,metric6,default_aux6,far_aux6,multiwan_aux6=get_gateway_dhcp(ifname,"6")
                                aux_gw6_dhcp=save_gateways_database(gwaddr6,name_interface,default_aux6,far_aux6,multiwan_aux6,metric6,False,False)
                            #update changes in DB ip4
                            aux_ipv4=update_DB(id_interface,jsonIPV4,IP4Config,IP4ConfigSerializer)
                            #update changes in DB ip6
                            aux_ipv6=update_DB(id_interface,jsonIPV6,IP6Config,IP6ConfigSerializer)
                            #update changes in DB generic config
                            aux_gen=update_DB(id_interface,data,GenericConfig,GenericConfigSerializer)
                            #update changes in DB interface config
                            aux_inter=update_interface_table(name_interface,data,InterfaceSerializer)
                            if aux_ipv4 is True:
                                if aux_ipv6 is True:
                                    if aux_gen is True:
                                        if aux_inter is True:  
                                            if aux_gw_dhcp is True:
                                                if aux_gw6_dhcp is True:
                                                    if setuptypeIP4.lower()=="static" :
                                                        aux_server=create_dhcpv4_db(id_interface,ip_address4,netmask4)
                                                    elif setuptypeIP4.lower()=="dhcp":
                                                        aux_server=delete_dhcp4_server(id_interface,ifname)
                                                    if aux_server is True:
                                                            ###### 
                                                            msg="Your interface {} was configured Successfully!!".format(name_interface)
                                                            status=200
                                                    else:
                                                        msg=aux_server
                                                        status=400
                                                    
                                                else:
                                                    msg=aux_gw6_dhcp
                                                    status=400
                                            else:
                                                msg=aux_gw_dhcp
                                                status=400
                                        else:
                                            msg=aux_inter
                                            status=400
                                    else:
                                        msg=aux_gen
                                        status=400
                                else:
                                    msg=aux_ipv6
                                    status=400
                            else:
                                msg=aux_ipv4
                                status=400
                        else:
                            msg=error
                            status=400        
                    else:
                        msg=aux_run
                        status=400
             
        else:
            
            msg="Connection is not active !!"
            status=400
    # print(msg)
    return JsonResponse({"message":msg},status=status)

##API to delete config 
###########################
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_interface(request,id):
    msg="failed to delete interface!"
    if request.method=="DELETE":
        if (Interface.objects.filter(id=id).exists()):
                interfaceObject = Interface.objects.get(id=id)
                ifname=interfaceObject.ifname
                output_service,error= get_old_config()
                if not error:
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
        genericConfigObject = GenericConfig.objects.filter(interface_id=interfaceObject.id)
        genericConfigDict = serializers.serialize("json", genericConfigObject)
        res = json.loads(genericConfigDict)
        genericConfigList = list(genericConfigDict)
        if res != []:
            id = res[0]['pk']
            res[0]['fields']['id'] = id
            res[0].pop('model')
            res[0].pop('pk')
            res[0]['fields'].pop('interface')
            info['genericConfig']=res[0]['fields']
        else:
            info['genericConfig']=[]
        IPV4ConfigObject = IP4Config.objects.filter(interface_id=interfaceObject.id)
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
    return JsonResponse(info)
