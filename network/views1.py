from django.http import JsonResponse
from network.serializers import *
from .models import *
from settings.serializers import *
from rest_framework.parsers import JSONParser
from authentification.views import *
from network.address import *
from .functions1 import *

def device_nameInterface(name_interface):
    data = Interface.objects.get(name_interface=name_interface)
    return data
###########################
@api_view(['PUT'])
@permission_classes([AllowAny])
def conf(request,name_interface,id):
    msg = ""
    if (request.method == 'PUT'):
        deviceInfo = device_nameInterface(name_interface)
        print({"ifname":deviceInfo.ifname})
        print({"name_interface":deviceInfo.name_interface})
        #get interface name to execute command systeme
        ifname=deviceInfo.ifname
        nameInterface=deviceInfo.name_interface
        # parse the incoming information
        data = JSONParser().parse(request)
        setuptypeIP4 = data.get('setuptypeIP4')
        description = data.get('description')
        bogon_aux = data.get('bogon_aux')
        private_aux = data.get('private_aux')
        addmac = data.get('addmac')
        mtuV = data.get('mtuV')
        mssV = data.get('mssV')
        speed_duplex = data.get('speed_duplex') 
        commandes=[]
        commandes_final=[]
        #get old configuration in service
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
                match setuptypeIP4:
                    case "None":
                        pass
                    case "static":
                        ip_address = data.get('value_setup_Ipv4')['ip_address']
                        netmask = data.get('value_setup_Ipv4')['netmask']
                        #gateway ??????????
                        #call function to convert address to static
                        commandes,output=update_conn_static(output,ifname,ip_address,netmask)
                    case "dhcp":
                        typeDHCP = data.get('value_setup_Ipv4')['typeDHCP']
                        if typeDHCP == "Base":
                            alias_add = data.get('value_setup_Ipv4')['alias_add']
                            alias_mask = data.get('value_setup_Ipv4')['alias_mask']
                            reject = data.get('value_setup_Ipv4')['reject']
                            hostname = data.get('value_setup_Ipv4')['hostname']
                            #contenu de dhclient.conf dhcp Base
                            configContenu=return_config_base(ifname,reject,hostname,alias_add,alias_mask)
                        if typeDHCP == "Advanced":
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
                            #contenu de dhclient.conf dhcp advanced
                            configContenu=return_config_advanced(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,send_options_dhcp_client,supersede_domaine_name,prepend_domain_server,send_options_lease_time,request,require)
                        #add commands of create file dhclient to list of commandes to execute    
                        commandes_final+=create_file(ifname,configContenu)
                         #call function to convert address to dhcp advanced /Base  in service
                        commandes,output=update_conn_dhcp(output,ifname)
                # match typeIP6:
                #     case "None":
                #         pass
                #     case "static":
                #         #call function to convert address to static ipv6
                #         commandesIPV6,output=update_conn_static_ipv6(output,ifname,ip6_address,netmask6)
                #     case "dhcp":
                #         if typeDHCP=="Base" :
                #         #contenu de dhclient.conf dhcp Base
                #             configContenu=return_config_base(ifname,reject,hostname,alias_add,alias_mask)
                #         if typeDHCP=="Advanced":
                #         #contenu de dhclient.conf dhcp advanced
                #             configContenu=return_config_advanced(ifname,reject,hostname,alias_add,alias_mask,timeout,retry,reboot,backoff,select_timeout,initial_interval,dhcp_client,domaine_name,domain_server,lease_time,request,require)
                #         #add commands of create file dhclient to list of commandes to execute    
                #         commandes_final+=create_file(ifname,configContenu)
                #             #call function to convert address to dhcp advanced /Base  in service
                #         commandesIPV6,output=update_conn_dhcp(output,ifname)
                
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
                commandesIPV6=[]
                #call function to block address
                configs,cmdsBlock,output=block_address_commandes(output,ifname,bogon_aux,private_aux)
                #update changes in DB interface config
                print('changes in DB interface config/*********************/')
                update_interface_table(id,data,InterfaceSerializer)
                # update_DB(id,data,Interface,InterfaceSerializer)
                #clean list of cmd to block address
                cmdsBlock = [x for x in cmdsBlock if x not in output]
                #contenu final des cmds pour lancer le service (execStart)
                commandes+=commandesIPV6+cmds+cmdsBlock
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

