from django.shortcuts import render
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json
import ast

from backend.managementGroup.models import Group
from backend.managementUsers.models import User
from backend.managementServers.models import Type, Server
from backend.managementUsers.views import getAllUsers
from backend.network.models import GenericConfig, IP4Config, IP6Config, Interface 
from backend.rules.models import Rule
from backend.gateway.models import Gateway, GatewayInterface
from backend.dashboard.functions import get_system_infomations
from backend.clamav.list_configurations import getclamavconfigurations
from backend.openvpn.list_servers_clients import get_list_all_client_openvpn,  get_list_all_server_openvpn
from backend.managementKeypairs.list_key_pairs import get_list_all_private_key, get_list_all_public_key
from backend.ipsec.list_ipsec import get_list_all_server_ipsec, get_status_ipsec
from backend.ids_ips.function_BD import get_home_net_de_la_base_de_donnees, get_ip_addresses
from backend.ids_ips.function_sys import execute_cmd
from backend.ids_ips.models import suricatafile, ids_ips_rule, Alert


def get_users(request):
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
        return list_users


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
        return list_group


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
        # interface_dict = serializers.serialize("json", interfaces)
        res = json.loads(interface_dict)
        for i in range(len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            # if not res[i]['fields']['ifname'].lower().startswith(("tun", "tap")):
            list_interface.append(res[i]['fields'])
        return list_interface


def get_all_interfaces_version2(request):
    list_interface = []
    if (request.method == 'GET'):
        interfaces = Interface.objects.all()
        interface_dict = serializers.serialize("json",interfaces)
        # interface_dict = serializers.serialize("json", interfaces)
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
                GatewayInterfaceObject=GatewayInterface.objects.get(Q(interface=interface_object.id)& Q(ipv4_gw_interface=True))
                gateway_id=GatewayInterfaceObject.gateway_id
                addrgw4=Gateway.objects.get(Q(id=gateway_id) & Q(ipv4_gw=True)).gwaddress
                resultat[0]['fields']['addrgw']=addrgw4
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
                print(gateway_id)
                if Gateway.objects.filter(Q(id=gateway_id) & Q(ipv4_gw=False)).exists():
                    addrgw6=Gateway.objects.get(Q(id=gateway_id) & Q(ipv4_gw=False)).gwaddress
                    resultat6[0]['fields']['addrgw6']=addrgw6
                info['IPV6Config']=resultat6[0]['fields']
        else:
            info['IPV6Config']=[]
        print({"info":info})
    return info


################################################ IDS-IPS #######################################################
############### General configuration suricata #################
## function to get suricata configuration
def general_suricata_configuration(request, id):
    if request.method=="GET":
        # Obtenez le champ HOME_NET du système et de la base de données
        home_net_database, interface_ids = get_home_net_de_la_base_de_donnees(id)

        address_home_net = home_net_database.strip("[]").split(",")
        # Récupérez les adresses IP à partir de la configuration IP4Config
        ip4config_object = IP4Config.objects.all()
        ip4config_dict = serializers.serialize("json", ip4config_object)
        res = json.loads(ip4config_dict)
        interfaces_ids_ip4config = []
        interfaces_address_ip4config = []
        # Parcourez les enregistrements IP4Config pour obtenir les interfaces et leurs adresses
        for i in range(len(res)):
            interfaces_ids_ip4config.append(res[i]['fields']['interface'])
            interfaces_address_ip4config = get_ip_addresses(interfaces_ids_ip4config)
        # Initialisez des listes pour stocker les valeurs finales
        address_home_net_final = []
        interface_ids_final = []
        # Comparez les interfaces et leurs adresses pour déterminer la configuration finale
        if interface_ids is not None:
            interface_ids = ast.literal_eval(interface_ids)
            for i in interface_ids:
                if i in interfaces_ids_ip4config:
                    if address_home_net[interface_ids.index(i)] == interfaces_address_ip4config[interfaces_ids_ip4config.index(i)]:
                        address = address_home_net[interface_ids.index(i)]
                    else:
                        address = interfaces_address_ip4config[interfaces_ids_ip4config.index(i)]
                    address_home_net_final.append(address)
                    interface_ids_final.append(i)

        # Créez une chaîne avec les adresses HOME_NET finales
        home_net_value = ' , '.join(address_home_net_final)
        home_net_value = f'[{home_net_value}]'
        interfaces_ids_value = str(interface_ids_final)
        suricata_yaml_path = "/etc/suricata/suricataTest.yaml"
        # Exécutez la commande 'sudo cat' pour lire le contenu du fichier
        output, error = execute_cmd("sudo cat " + suricata_yaml_path)
        # Mettez à jour la configuration dans le système
        if output:
            # Lit les lignes du fichier
            lines = output.split('\n')
            updated_lines = []
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("#"):
                    updated_lines.append(line + '\n')
                    # Conserve les lignes de commentaire telles quelles
                elif "HOME_NET:" in stripped_line:
                    # Met à jour la ligne HOME_NET avec la nouvelle valeur
                    updated_lines.append(f'    HOME_NET: "{home_net_value}"'+'\n')
                else:
                    # Conserve les autres lignes telles quelles
                    updated_lines.append(line + '\n')
                    with open(suricata_yaml_path, 'w') as local_file:
                        for string in updated_lines:
                            local_file.write(string)
        # Mettez à jour la configuration dans la base de données
        suricata_instance = suricatafile.objects.get(id=id)
        suricata_instance.interface_ids = interfaces_ids_value
        suricata_instance.home_net = home_net_value
        suricata_instance.save()
        current_configuration = {
            "id":id,
            "promisc": suricata_instance.promisc,
            "eve_log": suricata_instance.eve_log,
            "syslog": suricata_instance.syslog,
            "mpm_algo": suricata_instance.mpm_algo,
            "profile": suricata_instance.profile,
            "copy_mode": suricata_instance.copy_mode, 
            "status_enabled":suricata_instance.status_enabled
            }
    return json.dumps({"configuration": current_configuration, "interface_ids": interface_ids_final, "address_home_net": address_home_net_final})


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
            # res[i]['fields']['msg']=res[i]['fields']['msg'].strip("'")
            rules_list.append(res[i]['fields'])
    # Renvoyer la liste des règles au format JSON
    return json.dumps(rules_list)
############### End Rules suricata #################
############### Alerts suricata #################


def get_alerts_from_database(request):
    if request.method=="GET":
        alert_list=[]
        # alerts_object = alert.objects.all()  # Récupérer toutes les alertes de la base de données
        alerts_object = Alert.objects.all().order_by('-id')[:10] 
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
    usr=get_users(request)
    grp=get_groups(request)
    srv=get_servers(request)
    context = {'users':usr,"groups":grp,"servers":srv}
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
    context = {'rules':rules, 'interfaces':interfaces}
    return render(request, 'firewall_page.html',context)

@login_required(login_url='/')
def settings_page(request):
    return render(request, 'settings_page.html')


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
    print('status:', status)
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
    return render(request, 'squid_proxy.html')


@login_required(login_url='/')
def clamav_page(request):
    config= getclamavconfigurations()
    context = {'config':config}
    print('******************** :',context)
    return render(request, 'clamaV_page.html',context)


@login_required(login_url='/')
def subscription_page(request):
    context = {}
    return render(request, 'subscription_page.html', context)


def login(request):
    usr=getAllUsers(request)
    print (usr)

    context = {'users':usr}
    print (context)
    return render(request, 'login.html',context)


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
    print(context)
    return render(request, 'index_page.html',context)


def error_404_view(request, exception):
    return render(request,'404.html',status=404)

@login_required(login_url='/')
def suricata(request):
    object_suricata=suricatafile.objects.all()
    suricata = serializers.serialize("json", object_suricata)
    res = json.loads(suricata)
    id=res[0]['pk']
    general_config_suricata=general_suricata_configuration(request, id)
    rules_suricata=get_rules_from_database(request)
    alerts_suricata=get_alerts_from_database(request)
    interfaces=get_all_interfaces_version2(request)
    context={"general_config_suricata":general_config_suricata,"rules_suricata":rules_suricata,"alerts_suricata":alerts_suricata,"all_interfaces":interfaces}
    return render(request, 'ids_ips.html',context)