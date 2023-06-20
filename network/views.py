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
        ###
        #get object of interface type
        interfaceObject= Interface.objects.get(id=id)
        #get interface name to execute command systeme
        ifname=interfaceObject.ifname
        print({"ifname":ifname})
        ####
        # parse the incoming information
        data = JSONParser().parse(request)
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
        

        ###generic config
        mtuV=data.get('mtuV', None)
        addmac=data.get('addmac', None)
        mssV=data.get('mssV', None)
        speed_duplex=data.get('speed_duplex', None)
        ####
        typeIP4=data.get('typeIP4', None)
        typeDHCP=data.get('typeDHCP', None)
        ##blockage addresse
        bogon_aux=data['bogon_aux']
        private_aux=data['private_aux']
        commandes=[]
        commandes_final=[]
        print({'bbbbbb':"commandes_final"})
        ##get old configuration in service
        output,error=get_old_config()
        if error:
            print("error ",error)
        else:
            if len(output)!=0:
                #delete empty value
                output = [x for x in output if x]
                ##add requirement service
                output=add_requirement(ifname,output)
                ##IPV4 configuration cases 
                match typeIP4:
                    case "None":
                        pass
                    case "static":
                        #call function to convert address to static
                        commandes,output=update_conn_static(output,ifname,ip_address,netmask)
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
                        commandes,output=update_conn_dhcp(output,ifname)
                        
                #update changes in DB ip4
                print('changes in DB  ip4/*********************/')
                update_DB(id,data,IP4Config,IP4ConfigSerializer)
                print('/*********************/')
                    
                ##for generic config 
                cmds=[]       
                cmds,output=generic_config(output,ifname,speed_duplex,addmac,mtuV,mssV)
                #update changes in DB generic config
                print('changes in DB generic config/*********************/')
                update_DB(id,data,GenericConfig,GenericConfigSerializer)
                ##blocages des adresses
                cmdsBlock=[]
                configs=[]
                #call function to block address
                configs,cmdsBlock,output=block_address_commandes(output,ifname,bogon_aux,private_aux)
                #update changes in DB interface config
                print('changes in DB interface config/*********************/')
                update_interface_table(id,data,InterfaceSerializer)
                # update_DB(id,data,Interface,InterfaceSerializer)
                #clean list of cmd to block address
                cmdsBlock = [x for x in cmdsBlock if x not in output]
                #contenu final des cmds pour lancer le service (execStart)
                commandes+=cmds+cmdsBlock
                ###call function to add all commandes to the service
                output = add_cmd(output,commandes)
            ####ajouter au liste des commandes finales à executer (ssh.exec_command) 
                commandes_final +=configs+[
                """cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output)),
              
        'sudo systemctl daemon-reload',
        'sudo systemctl restart Asguard-Networking.service',
                ]
                print({"trah":commandes_final})
    # print({'aaaa':commandes_final})
                #lancer au background
                your_background_task(commandes_final)
                process = subprocess.Popen(['sudo','python', 'manage.py', 'process_tasks'])
                
    return JsonResponse({"commandes_finals:": commandes_final})
