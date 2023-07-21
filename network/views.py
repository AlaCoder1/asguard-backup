from django.http import JsonResponse
from network.serializers import *
from .models import *
from settings.serializers import *
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
from authentification.views import *
from network.address import *
from .functions import *
#################################
@api_view(['POST'])
@permission_classes([AllowAny])
def add_interface(request):
    data = JSONParser().parse(request)
    serializerIP4Config = InterfaceSerializer(data=data)
    print(serializerIP4Config.is_valid())
    if (serializerIP4Config.is_valid()):
        serializerIP4Config.save()
    return JsonResponse({"msg:": "interface added successfully!!!!!"})

###########################
@api_view(['PUT'])
@permission_classes([AllowAny])
def conf(request,id):
    msg = ""
    if (request.method == 'PUT'):
        #get object of interface type
        interfaceObject= Interface.objects.get(id=id)
        #get interface name to execute command systeme
        ifname=interfaceObject.ifname
        print({"ifname":ifname})
        ####
        # parse the incoming information
        data = JSONParser().parse(request)
        ##########IPV4
        ##static
        ip_address = data.get('ip_address', None)
        netmask = data.get('netmask', None)
        # gateway = data.get('gateway', None)
        ##DHCP
        ####case of ipvs dhcp and button is basic /advanced
        reject = data.get('reject', None)
        hostname = data.get('hostname', None)
        alias_add = data.get('alias_add', None)
        alias_mask = data.get('alias_mask', None)
        ###case of ipvs dhcp and button is advanced
        ##time protocol
        timeout = data.get('timeout', None)
        retry = data.get('retry', None)
        reboot = data.get('reboot', None)
        backoff = data.get('backoff', None)
        select_timeout = data.get('select_timeout', None)
        initial_interval = data.get('initial_interval', None)
        ###other
        dhcp_client = data.get('dhcp_client', None)
        domaine_name = data.get('domaine_name', None)
        domain_server = data.get('domain_server', None)
        lease_time = data.get('lease_time', None)
        request = data.get('request', None)
        require = data.get('require', None)
         ####
        typeIP4=data.get('typeIP4', None)
        typeDHCP=data.get('typeDHCP', None)
        ##########IPV6
        #static 
        ip6_address = data.get('ip6_address', None)
        netmask6 = data.get('netmask6', None)
        #static
        ###Base
        Request_only = data.get('Request_only', None)
        Prefix_delegation = data.get('Prefix_delegation', None)
        prefix_hint = data.get('prefix_hint', None)
        IPv4_connectivity = data.get('IPv4_connectivity', None)
        VLAN_priority = data.get('VLAN_priority', None)
        ####
        typeIP6=data.get('typeIP6', None)
        typeDHCP6=data.get('typeDHCP6', None)        
        ###generic config
        mtuV=data.get('mtuV', None)
        addmac=data.get('addmac', None)
        mssV=data.get('mssV', None)
        speed_duplex=data.get('speed_duplex', None)
        ##blockage addresse
        bogon_aux=data['bogon_aux']
        private_aux=data['private_aux']
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
                ##IPV4 configuration cases 
                match typeIP4:
                    case "None":
                        pass
                    case "static":
                        #call function to convert address to static
                        commandes,output_service,cmd_final_ipv4=update_conn_static(output_service,ifname,ip_address,netmask)
                    case "dhcp":
                        if typeDHCP=="Base" :
                        #contenu de dhclient.conf dhcp Base
                            configContenu=return_config_base(ifname,reject,hostname,alias_add,alias_mask)
                        if typeDHCP=="Advanced":
                        #contenu de dhclient.conf dhcp advanced
                            configContenu=return_config_advanced(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domaine_name,domain_server,lease_time,request,require)
                        #add commands of create file dhclient to list of commandes to execute    
                        commandes_final+=create_file(ifname,configContenu)
                        #call function to convert address to dhcp advanced /Base  in service
                        commandes,output_service,cmd_final_ipv4=update_conn_dhcp(output_service,ifname)
                match typeIP6:
                    case "None":
                        pass
                    case "static":
                        #call function to convert address to static ipv6
                        commandesIPV6,output_service,cmd_final_ipv6=update_conn_static_ipv6(output_service,ifname,ip6_address,netmask6)
                    case "dhcp":
                        if typeDHCP=="Base" :
                        #contenu de dhclient.conf dhcp Base
                            configContenu=return_config_base_ipv6(ifname,id,Request_only,Prefix_delegation,prefix_hint,IPv4_connectivity,VLAN_priority)
                        if typeDHCP=="Advanced":
                        #contenu de dhclient.conf dhcp advanced
                            configContenu=return_config_advanced_ipv6(ifname,id,Request_only,Prefix_delegation,prefix_hint,IPv4_connectivity,VLAN_priority)
                        #add commands of create file dhclient to list of commandes to execute    
                        commandes_final+=create_file_ipv6(ifname,configContenu)
                        #call function to convert address to dhcp advanced /Base  in service
                        commandesIPV6,output_service,cmd_final_ipv6=update_conn_dhcp_ipv6(output_service,ifname)
                        
                #update changes in DB ip4
                print('changes ip4 in DB /*********************/')
                update_DB(id,data,IP4Config,IP4ConfigSerializer)
                print('/*********************/')
                 #update changes in DB ip9
                print('changes ip6 in DB /*********************/')
                update_DB(id,data,IP6Config,IP6ConfigSerializer)
                print('/*********************/')
                ##for generic config 
                cmds=[]       
                cmds,output_service,cmd_final_Gen=generic_config(output_service,ifname,speed_duplex,addmac,mtuV,mssV)
                #update changes in DB generic config
                print('changes in DB generic config/*********************/')
                update_DB(id,data,GenericConfig,GenericConfigSerializer)
                ##blocages des adresses
                cmdsBlock=[]
                configs=[]
                #call function to block address
                configs,cmdsBlock,output_service,cmd_final_Block=block_address_commandes(output_service,ifname,bogon_aux,private_aux)
                #update changes in DB interface config
                print('changes interface config in DB /*********************/')
                update_interface_table(id,data,InterfaceSerializer)
                #clean list of cmd to block address
                cmdsBlock = [x for x in cmdsBlock if x not in output_service]
                #contenu final des cmds pour lancer le service (execStart)
                commandes+=commandesIPV6+cmds+cmdsBlock
                ###call function to add all commandes to the service
                output_service = add_cmd(output_service,commandes)
                #ajouter au liste des commandes finales à executer (ssh.exec_command) 
                commandes_final+=configs+cmd_final_ipv4+cmd_final_ipv6+cmd_final_Gen+cmd_final_Block
                print({"trah":commandes_final})
    for cmd in commandes_final:
        stdin, stdout, stderr = ssh.exec_command('{}'.format(cmd))
        error = stderr.read().decode('utf-8')
        output = stdout.read().decode('utf-8').split('\n')

        if error:
            msg=error,"    :"+cmd
            break
        else:
            print("service created successufully!!",cmd) 

    stdin, stdout, stderr = ssh.exec_command('{}'.format(
            """cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output_service)),
            ))
    return JsonResponse({"commandes_finals:": commandes_final})
