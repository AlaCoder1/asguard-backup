import subprocess
from django.shortcuts import redirect, render
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json
import ast
from backend.LdapServer.list_Remote_servers import get_list_ad_servers
from backend.managementGroup.models import Group
from backend.managementUsers.models import User
from backend.managementServers.models import Type, Server
from backend.managementUsers.views import get_all_users
from backend.nat.list_nat import get_list_all_dnat, get_list_all_one_to_one_nat, get_list_all_snat
from backend.network.models import GenericConfig, IP4Config, IP6Config, Interface 
from backend.routing.list_routing import get_list_all_gateway, get_list_all_routing
from backend.rules.models import Rule
from backend.gateway.models import Gateway, GatewayInterface
from backend.dashboard.functions import get_system_infomations
from backend.openvpn.list_servers_clients import get_list_all_client_openvpn,  get_list_all_server_openvpn
from backend.managementKeypairs.list_key_pairs import get_list_all_private_key, get_list_all_public_key
from backend.ipsec.list_ipsec import get_list_all_server_ipsec, get_status_ipsec
from backend.ids_ips.function_BD import get_home_net_de_la_base_de_donnees, get_ip_addresses, get_suricata_packet
from backend.ids_ips.function_sys import execute_cmd, read_from_yaml, save_in_yaml
from backend.ids_ips.models import *
from backend.ids_ips.serializers import AlertSerializer, SuricataFileSerializer
import ast
from backend.proxy.views import *
from backend.proxy.models import *
from backend.sdwan.list_area import get_list_all_area
from backend.sdwan.list_sdwan_rule import get_list_all_sdwan_rule
from backend.subscription.models import plan, plansSubscription,plansFeatures,Features
import ruamel.yaml
from backend.settings.models import *
from collections import defaultdict
from backend.waf.list_waf import get_alerts, get_list_all_waf_application, get_list_all_waf_rule, get_one_waf_config
from backend.ztna.list_ztna import get_edge_router_policies, get_host_configs, get_identities, get_intercept_configs, get_routers, get_service_policies, get_services
from backend.ztna.utils import get_Zt_Token
from backend.ztna.list_ztna import get_service_edge_router_policies
from views.functions import get_logrotate_data, get_vlan, get_vlan_interface, get_vxlan, get_vxlan_interface

from views.functions import get_all_server_dhcp4, get_vlan, get_vlan_interface
def get_squid_status_from_bd():
    server_status= ServerSatus.objects.get(id=1)
    return server_status.status_server

def get_squid_status():
    try:
        result = subprocess.run(['systemctl', 'status', 'squid.service'], capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if 'Active:' in line:
                status = line.split(':')[1].strip()
                return status
    except subprocess.CalledProcessError as e:
        return None
    
def getGeneraleInfo(request):
    if (request.method == 'GET'):
        squid_conf_path = '/etc/squid/squid.conf'
        command = "cat "+squid_conf_path
        stdout, stderr = run_command(command)
        resultat=stdout.split('\n')
        for line in resultat:
            line = line.strip()
            if line.startswith('http_port'):
                parts = line.split()
                if len(parts) >= 2:
                    port = parts[1].split(':')[0]
                    
        squid_status = get_squid_status()
        if squid_status:
            if 'active' in squid_status:
                return {"Port":port,"status":True}
        else:
            return {"Port":port,"status":False}
def get_all_proxy_rules(request):
    if (request.method == 'GET'):
        list_proxyRules =[]
        data = ProxyRules.objects.all()
        proxyRulesDict = serializers.serialize("json", data)
        res = json.loads(proxyRulesDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_proxyRules.append(res[i]['fields'])
        return list_proxyRules

def statusEnableAuth(request):
    if (request.method == 'GET'):
        list_line = []
        config_file_path = '/etc/squid/squid.conf'
        lines_to_check = [
            "#http_access allow allowed_subnet_by_auth authenticated_users\n",
            "#http_access allow allowed_ip_by_auth authenticated_users\n",
            "#http_access allow allowed_domain_by_auth authenticated_users\n"
        ]
        with open(config_file_path, 'r') as file:
                content = file.readlines()
        for line in content:
            if line.strip().startswith('#'):
                list_line.append(line)
        for i in lines_to_check:
            if i in list_line:
                enable = True
            else:
                enable =False
        return enable
def allProxyUsers(request):
    if (request.method == 'GET'):
        list_proxyUsers =[]
        data = ProxyUser.objects.all()
        proxyUsersDict = serializers.serialize("json", data)
        res = json.loads(proxyUsersDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_proxyUsers.append(res[i]['fields'])
        return list_proxyUsers
def allGProxyroups(request):
    if (request.method == 'GET'):
        list_line = []
    list_groups = []
    config_file_path = '/etc/squid/squid.conf'
    with open(config_file_path, 'r') as file:
                content = file.readlines()
    for line in content:
        if "squid/acl/" in line:
            list_line.append(line)
            

    pattern = re.compile(r'acl (\w+) url_regex')

    groups = [pattern.findall(line)[0] for line in list_line if pattern.findall(line)]
    for i in groups:
        target_line = 'http_access deny '+i
        rslt = get_line_from_file(config_file_path,target_line)
        list_groups.append({"name":i,"status":rslt})
    return list_groups
def getUsers(request):
    list_users = []
    if (request.method == 'GET'):
        users = User.objects.all()
        user_dict = serializers.serialize("json", users)
        res = json.loads(user_dict)
        for i in range(len(res)):
            group_dict = []
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('password')
            res[i]['fields'].pop('last_login')
            res[i]['fields'].pop('token_last_expired')
            res[i]['fields']['id'] = id
            if len(res[i]['fields']['group'])!=0:
                for k in res[i]['fields']['group']:
                    group=Group.objects.get(id=k)
                    group_dict.append({"name":group.groupname,"id":group.id})
                res[i]['fields']['group']=group_dict
            list_users.append(res[i]['fields'])
        return json.dumps(list_users)


def get_groups(request):
    list_group = []
    if (request.method == 'GET'):
        groups = Group.objects.filter(created_by_system=0)
        group_dict = serializers.serialize("json", groups)
        res = json.loads(group_dict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('created_by_system')
            res[i]['fields']['id'] = id
            if res[i]['fields']['id'] != 1:
                res[i]['fields']['sudoers']=False
            else:
                res[i]['fields']['sudoers']=True
            list_group.append(res[i]['fields'])
        return json.dumps(list_group)


def get_servers(request):
    list_servers = []
    if (request.method == 'GET'):
        servers = Server.objects.all()
        server_dict = serializers.serialize("json", servers)
        res = json.loads(server_dict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            type = Type.objects.get(id=res[i]['fields']['type'])
            res[i]['fields']['id'] = id
            res[i]['fields']['type_name'] = type.type_name
            list_servers.append(res[i]['fields'])
        return list_servers


def get_all_rules(request):
    if (request.method == 'GET'):
        all_rules={}
        set_type=[]
        allinterfaces=Interface.objects.all()
        interface_dict = serializers.serialize("json", allinterfaces)
        res_interface = json.loads(interface_dict)
        ########## get all types 
        rules= Rule.objects.all()
        rule_dict = serializers.serialize("json", rules)
        res_rules = json.loads(rule_dict)
        for j in range(len(res_rules)):
            set_type.append(res_rules[j]['fields']['type_rule'])
        for x in range(len(res_interface)):
          id_interface = res_interface[x]['pk']
          rules_type = {}
          # rules= Rule.objects.get(interface=id_interface)
          for elem in list(set(set_type)): 
            rules= Rule.objects.filter(interface=id_interface,type_rule=elem)
            rule_dict = serializers.serialize("json", rules)
            res = json.loads(rule_dict)
            list_rules=[]
            for i in range(len(res)):
                interface_dict=[]
                res[i].pop('model')
                id = res[i]['pk']
                res[i].pop('pk')
                res[i]['fields']['id'] = id
                res[i]['fields'].pop("interface")
                res[i]['fields'].pop("rule")
                list_protocols=[]
                if res[i]['fields']['protocol'].find("{")!=-1:
                        list_protocols=res[i]['fields']['protocol'].strip('{').strip('}').split(',')
                else:
                        list_protocols.append(res[i]['fields']['protocol'])
                res[i]['fields']['protocol']=list_protocols
                list_rules.append(res[i]['fields'])
             ########## 
            rules_type[elem]=list_rules
          all_rules[res_interface[x]['fields']['name_interface']]=rules_type
        return all_rules


def get_all_gateways(request):
    if (request.method == 'GET'):
        gateways = Gateway.objects.all()
        gateways_dict = serializers.serialize("json", gateways)
        res = json.loads(gateways_dict)
        list_gateways=[]
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_gateways.append({
                "gwname":res[i]['fields']['gwname'],
                "gwaddress":res[i]['fields']['gwaddress'],
                })
    return list_gateways


def get_all_static_gateways(request,ipv4_gw):
    if (request.method == 'GET'):
        gateways= Gateway.objects.filter(Q(staticgw=True)&Q(ipv4_gw=ipv4_gw))
        gateways_dict = serializers.serialize("json", gateways)
        res = json.loads(gateways_dict)
        list_gateways=[]
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_gateways.append(res[i]['fields'])
    return  list_gateways


def get_all_interfaces(request):
    list_interface = []
    if (request.method == 'GET'):
        interfaces = Interface.objects.all()
        interface_dict=serializers.serialize("json",interfaces)
        res = json.loads(interface_dict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_interface.append(res[i]['fields'])
        return list_interface


def get_all_interfaces_version2(request):
    list_interface = []
    if (request.method == 'GET'):
        interfaces = Interface.objects.all()
        interface_dict = serializers.serialize("json",interfaces)
        res = json.loads(interface_dict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            if not res[i]['fields']['ifname'].lower().startswith(("tun", "tap")):
                list_interface.append(res[i]['fields'])
        return list_interface    


def get_informations_by_interface(request,name_interface):
    info={}
    interface={}
    if (request.method == 'GET'):
        interface_object = Interface.objects.get(name_interface=name_interface)
        interface['id']=interface_object.id
        interface['ifname']=interface_object.ifname
        interface['private_aux']=interface_object.private_aux
        interface['bogon_aux']=interface_object.bogon_aux
        interface['service_status']=interface_object.service_status
        interface['name_interface']=interface_object.name_interface
        interface['description']=interface_object.description
        info['interface']=interface
        generic_config_object = GenericConfig.objects.filter(interface_id=interface_object.id)
        generic_config_dict = serializers.serialize("json", generic_config_object)
        res = json.loads(generic_config_dict)
        if res != []:
            id = res[0]['pk']
            res[0]['fields']['id'] = id
            res[0].pop('model')
            res[0].pop('pk')
            res[0]['fields'].pop('interface')
            info['genericConfig']=res[0]['fields']
        else:
            info['genericConfig']=[]
        ipv4_config_object = IP4Config.objects.filter(interface_id=interface_object.id)
        ###
        ipv4_config_object_dict = serializers.serialize("json", ipv4_config_object)
        resultat = json.loads(ipv4_config_object_dict)
       
        if resultat != []:
            id = resultat[0]['pk']
            resultat[0]['fields']['id'] = id
            resultat[0].pop('model')
            resultat[0].pop('pk')
            resultat[0]['fields'].pop('interface')
            resultat[0]['fields']['addrgw']=""
            ### get gateway4 from table intermediaire
            if GatewayInterface.objects.filter(Q(interface=interface_object.id)& Q(ipv4_gw_interface=True)).exists():
                list_gateway=[]
                GatewayInterfaceObject=GatewayInterface.objects.filter(Q(interface=interface_object.id)& Q(ipv4_gw_interface=True))
                for gateway_interface in GatewayInterfaceObject:
                    gateway_id=gateway_interface.gateway_id
                    addrgw4=Gateway.objects.get(Q(id=gateway_id) & Q(ipv4_gw=True)).gwaddress
                    list_gateway.append(addrgw4)                
                resultat[0]['fields']['addrgw']=' , '.join(list_gateway) if len(list_gateway)>0 else list_gateway[0]
            info['IPV4Config']=resultat[0]['fields']
        else:
            info['IPV4Config']=[]
        
        ##############ipv6    
        ipv6_config_object = IP6Config.objects.filter(interface_id=interface_object.id)
        ###
        ipv6_config_object_dict = serializers.serialize("json", ipv6_config_object)
        resultat6 = json.loads(ipv6_config_object_dict)
       
        if resultat6 != []:
            id = resultat6[0]['pk']
            resultat6[0]['fields']['id'] = id
            resultat6[0].pop('model')
            resultat6[0].pop('pk')
            resultat6[0]['fields'].pop('interface')
            resultat6[0]['fields']['addrgw6']=""
            ### get gateway4 from table intermediaire
            if GatewayInterface.objects.filter(Q(interface=interface_object.id)& Q(ipv4_gw_interface=False)).exists():
                GatewayInterfaceObject=GatewayInterface.objects.get(Q(interface=interface_object.id)& Q(ipv4_gw_interface=False))
                gateway_id=GatewayInterfaceObject.gateway_id
                if Gateway.objects.filter(Q(id=gateway_id) & Q(ipv4_gw=False)).exists():
                    addrgw6=Gateway.objects.get(Q(id=gateway_id) & Q(ipv4_gw=False)).gwaddress
                    resultat6[0]['fields']['addrgw6']=addrgw6
                info['IPV6Config']=resultat6[0]['fields']
        else:
            info['IPV6Config']=[]
    return info


################################################ IDS-IPS #######################################################
############### General configuration suricata #################
def general_suricata_configuration(request, id):
    """function to get informations suricata with update config if neeeded"""
    if request.method=="GET":
        liste_interfaces=get_suricata_packet(id)
        interface_ids_final=[d['id_interface'] for d in liste_interfaces]
        interfaces_address_ip4config = get_ip_addresses(interface_ids_final)
        # Créez une chaîne avec les adresses HOME_NET finales
        home_net_value_sys = f'[{",".join(list(set(interfaces_address_ip4config)))}]'
        home_net_value = f'[{",".join(interfaces_address_ip4config)}]'
        suricata_yaml_path = "/etc/suricata/suricata.yaml"
        yaml_class = ruamel.yaml.YAML()
        data_input=read_from_yaml(suricata_yaml_path,yaml_class)
        ##HOME_NET
        data_input['vars']['address-groups']['HOME_NET']=home_net_value_sys
        save_in_yaml(suricata_yaml_path,data_input,yaml_class) 
        # Mettez à jour la configuration dans la base de données
        suricata_instance = suricatafile.objects.get(id=id)
        data_updated={
            "home_net" : home_net_value
        }
        suricata_serializer=SuricataFileSerializer(suricata_instance,data=data_updated)
        if suricata_serializer.is_valid():
            suricata_serializer.save()
        
        current_configuration = {
            "id":id,
            "promisc": suricata_instance.promisc,
            "eve_log": suricata_instance.eve_log,
            "syslog": suricata_instance.syslog,
            "mpm_algo": suricata_instance.mpm_algo,
            "profile": suricata_instance.profile,
            "status_enabled":suricata_instance.status_enabled,
            "liste_interfaces":liste_interfaces,
            "mode_inline":suricata_instance.mode_inline=='yes'
            }
    return json.dumps({"configuration": current_configuration, "interface_ids": interface_ids_final, "address_home_net":interfaces_address_ip4config })

############### End General configuration suricata #################
############### Rules suricata #################
def get_rules_from_database(request):
    if request.method=="GET":
        rules_list = []
        # Récupérer toutes les règles de la base de données
        rules_from_db = ids_ips_rule.objects.all()
        rule_suricata = serializers.serialize("json", rules_from_db)
        res = json.loads(rule_suricata)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            res[i]['fields'].pop("rule")
            # res[i]['fields'].pop("msg")
            res[i]['fields']['msg']=res[i]['fields']['msg'].strip('"')
            res[i]['fields']['action']=res[i]['fields']['action'].strip('#')
            rules_list.append(res[i]['fields'])
    # Renvoyer la liste des règles au format JSON
    return json.dumps(rules_list)
############### End Rules suricata #################
############### Alerts suricata #################


def get_alerts_from_database(request):
    if request.method=="GET":
        alert_list=[]
        alerts_object = Alert.objects.all()  # Récupérer toutes les alertes de la base de données
        # alerts_object = Alert.objects.all().order_by('-id')[:10] 
        alerts = serializers.serialize("json", alerts_object)
        res = json.loads(alerts)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            # res[i]['fields'].pop("alert")
            alert_list.append(res[i]['fields'])
    return json.dumps(alert_list)


@login_required(login_url='/')
def user_certificate_managment_page(request):
    usr=getUsers(request)
    grp=get_groups(request)
    servers=get_list_ad_servers()
    context = {'users':usr,"groups":grp,"servers":servers}
    return render(request, 'user_certificate_managment.html',context)


@login_required(login_url='/')
def interface_page(request):
    interfaces=get_all_interfaces_version2(request)
    config={}
    all_static_gateways={}
    for i in range(len(interfaces)):
        ipv4_config=get_informations_by_interface(request, interfaces[i]['name_interface'])
        config[interfaces[i]['name_interface']]=ipv4_config
    # ipv4_config=GetInformationsByInterface(request, interfaces[0]['name_interface'])
    all_static_gateways_ipv4=get_all_static_gateways(request,ipv4_gw=True)
    all_static_gateways_ipv6=get_all_static_gateways(request,ipv4_gw=False)
    all_static_gateways['ipv4_gw']=all_static_gateways_ipv4
    all_static_gateways['ipv6_gw']=all_static_gateways_ipv6
    ##pour le moment on ajoute ce ligne
    all_static_gateways=all_static_gateways_ipv4
    ###
    context = {'interfaces':interfaces,'IPV4Config':config,'allStaticGateways':all_static_gateways}
    return render(request, 'interface_page.html',context)


@login_required(login_url='/')
def firewall_page(request):
    rules=get_all_rules(request)
    interfaces=get_all_interfaces(request)
    last_subscription=list_features_about_last_subscription(request)
    context = {'rules':json.dumps(rules), 'interfaces':interfaces,'last_subscription':json.dumps(last_subscription)}
    return render(request, 'firewall_page.html',context)

@login_required(login_url='/')
def openvpn_page(request):
    servers=get_list_all_server_openvpn()
    clients=get_list_all_client_openvpn()
    context = {'servers':servers,'clients':clients}
    return render(request, 'openvpn_page.html', context)


@login_required(login_url='/')
def ipsec_page(request):
    servers=get_list_all_server_ipsec()
    public_key =get_list_all_public_key()
    status = get_status_ipsec()
    context = {'servers': servers, 'publicKey': public_key, 'status': status}
    return render(request, 'ipsec_page.html', context)


@login_required(login_url='/')
def key_pair_page(request):
    private_key = get_list_all_private_key()
    public_key = get_list_all_public_key()
    context = {'privateKey': private_key,'publicKey': public_key}
    return render(request, 'keyPair_page.html',context)


@login_required(login_url='/')
def squid_proxy(request):
    proxyUser = allProxyUsers(request)
    generalInfo = getGeneraleInfo(request)
    statusEnable = statusEnableAuth(request)
    proxyRule = get_all_proxy_rules(request)
    proxyGroups = allGProxyroups(request)
    statusServer = get_squid_status_from_bd()
    context = {'proxyUser': json.dumps(proxyUser),'generalInfo' : json.dumps(generalInfo),'statusEnable' : json.dumps(statusEnable),'proxyRule' : json.dumps(proxyRule),'proxyGroups' : json.dumps(proxyGroups),'statusServer' : json.dumps(statusServer)}
    return render(request, 'squid_proxy.html',context)

@login_required(login_url='/')
def sdwan_page(request):
    allArea = get_list_all_area()
    allRule = get_list_all_sdwan_rule()
    context = {'allArea': json.dumps(allArea),'allRule': json.dumps(allRule)}
    return render(request, 'sdwan_page.html',context)

@login_required(login_url='/')
def waf_page(request):
    waf_conf = get_one_waf_config()
    list_rules = get_list_all_waf_rule()
    list_waf_app = get_list_all_waf_application()
    waf_alert = get_alerts()
    context = {'waf_conf': json.dumps(waf_conf),'list_rules': json.dumps(list_rules),'list_waf_app': json.dumps(list_waf_app),'waf_alert': json.dumps(waf_alert)}
    return render(request, 'waf_page.html',context)


@login_required(login_url='/')
def ztna_page(request):
    identities = get_identities()
    routers = get_routers()
    hostconfigs = get_host_configs()
    interceptconfigs = get_intercept_configs()
    services = get_services()
    router_policies = get_edge_router_policies()
    service_policies = get_service_policies()
    service_edge_router_policies = get_service_edge_router_policies()
    token = get_Zt_Token()
    context = {'identities': json.dumps(identities),
               'routers':json.dumps(routers) ,
               'hostconfigs':json.dumps(hostconfigs),
               'interceptconfigs':json.dumps(interceptconfigs),
               'token':json.dumps(token),
               'services': json.dumps(services), 
               'router_policies': json.dumps(router_policies), 
               'service_policies': json.dumps(service_policies), 
               'service_edge_router_policies':json.dumps(service_edge_router_policies)}
    return render(request,'ztna.html',context)


@login_required(login_url='/')
def profile_page(request):
    return render(request, 'profile_page.html')

@login_required(login_url='/')
def system_log(request):
    return render(request, 'system_log.html')

@login_required(login_url='/')
def setting_page(request):
    network_info = []
    generale_settings=get_generale_settings(request,id=1)
    network = Network.objects.all()
    for i in network:
        network_info.append(i.server_dns)
    time_zone = time_zones(request)
    gateway=gatways_information(request)
    context = {'time_zone':json.dumps(time_zone),'generale_settings':json.dumps(generale_settings),"network_info":json.dumps(network_info),"gateway":json.dumps(gateway)}
    return render(request, 'settings_page.html',context)




@login_required(login_url='/')
def subscription_page(request):
    subscription_information=subscription_info(request)
    allfeature = all_feature(request)
    context = {'subscription_information':json.dumps(subscription_information),'allfeature':json.dumps(allfeature)}
    return render(request, 'subscription_page.html', context)
 
#comment to test git command
def login(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return render(request, 'login.html')


@login_required(login_url='/')
def index_page(request):
    info=get_system_infomations()
    gateways=get_all_gateways(request)
    interfaces=get_all_interfaces_version2(request)
    config=[]
    for i in range(len(interfaces)):
        info_interface = {}
        ipv4_config = get_informations_by_interface(request, interfaces[i]['name_interface'])
        speed_duplex = ""
        ip_address = ""
        if "speed_duplex" in ipv4_config['genericConfig'] :
            speed_duplex = ipv4_config['genericConfig']['speed_duplex']
        if "ip_address" in ipv4_config['IPV4Config'] :
            ip_address = ipv4_config['IPV4Config']['ip_address']
        info_interface = {
            "name_interface":interfaces[i]['name_interface'],
            "speed_duplex":speed_duplex,
            "ip_address":ip_address}
        config.append(info_interface)
    context = {"informations":info,"gateways":json.dumps(gateways),"interfaces":json.dumps(config)}
    return render(request, 'index_page.html',context)


def error_404_view(request, exception):
    return render(request,'404.html',status=404)

def success(request):
    return render(request,'success.html')

@login_required(login_url='/')
def suricata(request):
    object_suricata=suricatafile.objects.all()
    suricata = serializers.serialize("json", object_suricata)
    res = json.loads(suricata)
    id=res[0]['pk']
    general_config_suricata=general_suricata_configuration(request, id)
    # rules_suricata=get_rules_from_database(request)
    # alerts_suricata=get_alerts_from_database(request)
    interfaces=get_all_interfaces_version2(request)
    context={"general_config_suricata":general_config_suricata,"all_interfaces":interfaces}
    return render(request, 'ids_ips.html',context)


def list_features_about_last_subscription(request):
    list_features = []
    if request.method == 'GET':
        last_subscription = plansSubscription.objects.order_by('start_at').last()
        if last_subscription !=None:
            last_subscription_dict = last_subscription.__dict__
            if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
                plan_features= plansFeatures.objects.filter(plan = last_subscription.plan.pk)
                plan_features_dict = serializers.serialize("json", plan_features)
                res = json.loads(plan_features_dict)
                for i in res:
                    for key, value in i.items():
                        if key == 'fields':
                            list_features.append(i['fields']['description'])
        else:
            list_features = []
        return list_features
    
    
def subscription_info(request):
    subscription_info = {}
    if request.method == 'GET':
        last_subscription = plansSubscription.objects.order_by('start_at').last()
        if last_subscription != None:
            last_subscription_dict = last_subscription.__dict__
            # if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
            plan_info = plan.objects.get(id = last_subscription_dict['plan_id'])
            subscription_info['type_pack'] =plan_info.slug
            subscription_info['date_start'] =last_subscription_dict['start_at'].strftime('%Y-%m-%d %H:%M:%S')
            subscription_info['end_at'] =last_subscription_dict['end_at'].strftime('%Y-%m-%d %H:%M:%S')
            subscription_info['expiration_date'] =last_subscription_dict['end_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            subscription_info = {}
        return subscription_info
    
def all_feature(request):
    features = []
    feature_element = {}
    if request.method == 'GET':
        features_from_bd = Features.objects.all()
        for feature in features_from_bd:
            feature_element["name"] = feature.features
            feature_element["price"] = feature.price
            feature_element["id"] = feature.pk
            features.append(feature_element)
            feature_element = {}
        return features
    
@login_required(login_url='/')
def openvpn_monitoring(request):
    return render(request, 'vpnmonitoring.html')
@login_required(login_url='/')
def nat_page(request):
    listNat= get_list_all_snat()
    listDNat= get_list_all_dnat()
    listOneToOne= get_list_all_one_to_one_nat()
    context = {'listNat':listNat,'listDNat':listDNat,'listOneToOne':listOneToOne}
    return render(request, 'nat.html',context)

@login_required(login_url='/')
def vlan_page(request):
    list_vlan=get_vlan(request)
    list_vlan_interface= get_vlan_interface(request)
    context = {'list_vlan':list_vlan,'list_vlan_interface':list_vlan_interface}
    return render(request, 'vlan.html',context)

@login_required(login_url='/')
def vxlan_page(request):
    list_vxlan=get_vxlan(request)
    list_vxlan_interface= get_vxlan_interface(request)
    context = {'list_vxlan':list_vxlan,'list_vxlan_interface':list_vxlan_interface}
    return render(request, 'vxlan.html',context)

@login_required(login_url='/')
def routing_page(request):

    listAllRouting = get_list_all_routing()
    listAllGateway=get_list_all_gateway()
    context = {'listAllRouting':listAllRouting,'listAllGateway':listAllGateway}
    return render(request, 'routing.html',context)


@login_required(login_url='/')
def interface_type(request):
    list_vlan=get_vlan(request)
    list_vxlan=get_vxlan(request)
    list_vlan_interface= get_vlan_interface(request)
    list_vxlan_interface= get_vxlan_interface(request)
    context = {'list_vlan':json.dumps(list_vlan),'list_vlan_interface':json.dumps(list_vlan_interface),'list_vxlan':json.dumps(list_vxlan),'list_vxlan_interface':json.dumps(list_vxlan_interface)}
    return render(request, 'interfaceType.html',context)

@login_required(login_url='/')
def server_dhcp4_page(request):
    list_dhcp4_server=get_all_server_dhcp4(request)
    context = {'list_dhcp4_server':list_dhcp4_server}
    return render(request, 'dhcp4_server.html',context)

@login_required(login_url='/')
def logrotate_page(request):
    list_logrotate=get_logrotate_data(request)
    list_logrotate=json.dumps(list_logrotate)
    context = {'logrotate':list_logrotate}
    return render(request, 'logrotate.html',context)

################## generale information ##################

def get_generale_settings(request,id):
    """get information system from database"""
    if (request.method == 'GET'):
        system_object = System.objects.get(id=id)
        time_zone = Timezone.objects.get(name = system_object.time_zone.name)
        system_dict = {
            "hostname":system_object.hostname,
            "domaine":system_object.domaine,
            "time_zone":{
                "name" :time_zone.name,
                "id":time_zone.pk
            }
        }
        return system_dict
    
def time_zones(request):
    """get list of all time zone"""
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
        return list_timezones
    
def gatways_information(request):
    """get all gateways informations"""
    gatways_information=[]
    if (request.method == 'GET'):
        gateway=GatewayInterface.objects.all()
        gatewayDict = serializers.serialize("json", gateway)
        res = json.loads(gatewayDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            interface = Interface.objects.get(id = res[i]['fields']['interface'])
            res[i]['fields']['name_interface'] = interface.name_interface
            gatways_information.append(res[i]['fields'])
        output_data = defaultdict(list)

        for item in gatways_information:
            gateway = item["gateway"]
            fetch_gateway = Gateway.objects.get(id = gateway)
            del item["gateway"]
            output_data[gateway].append(item)
        output_data = [
            {
                "gateway": {"id": gateway, "address": fetch_gateway.gwaddress},
                "info": info
            } for gateway, info in output_data.items()
        ]
        return output_data

        # return JsonResponse({"gatways_information": output_data})
    
    
################## generale information ##################