from django.shortcuts import render
from backend.managementUsers.views import *
from backend.managementUsers.models import User
from django.contrib.auth.decorators import login_required
from backend.managementServers.models import * 
from backend.network.models import *
from backend.rules.models import *
from backend.gateway.models import *
from backend.dashboard.functions import get_system_infomations
from django.db.models import Q
from backend.openvpn.list_servers_clients import get_all_client_openvpn,  get_all_server_openvpn
from backend.managementKeypairs.list_key_pairs import get_all_private_key, get_all_public_key
from backend.ipsec.list_ipsec import get_all_server_ipsec

def getUsers(request):
    list_users = []
    if (request.method == 'GET'):
        users = User.objects.all()
        userDict = serializers.serialize("json", users)
        res = json.loads(userDict)
        for i in range(0, len(res)):
            groupDict = []
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
                    groupDict.append({"name":group.groupname,"id":group.id})
                res[i]['fields']['group']=groupDict
            list_users.append(res[i]['fields'])
        return list_users
def getGroups(request):
    list_group = []
    if (request.method == 'GET'):
        groups = Group.objects.filter(created_by_system=0)
        groupDict = serializers.serialize("json", groups)
        res = json.loads(groupDict)
        for i in range(0, len(res)):
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
def getServers(request):
    list_servers = []
    if (request.method == 'GET'):
        servers = Server.objects.all()
        serverDict = serializers.serialize("json", servers)
        res = json.loads(serverDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            type = Type.objects.get(id=res[i]['fields']['type'])
            res[i]['fields']['id'] = id
            res[i]['fields']['type_name'] = type.type_name
            list_servers.append(res[i]['fields'])
        return list_servers
def GetAllRules(request):
    if (request.method == 'GET'):
        all_rules={}
        set_type=[]
        allinterfaces=Interface.objects.all()
        interfaceDict = serializers.serialize("json", allinterfaces)
        resInterface = json.loads(interfaceDict)
        ########## get all types 
        rules= Rule.objects.all()
        ruleDict = serializers.serialize("json", rules)
        resRules = json.loads(ruleDict)
        for j in range(0, len(resRules)):
            set_type.append(resRules[j]['fields']['type_rule'])
        for x in range(0, len(resInterface)):
          idInterface=resInterface[x]['pk']
          rules_type={}
          # rules= Rule.objects.get(interface=idInterface)
          for elem in list(set(set_type)): 
            rules= Rule.objects.filter(interface=idInterface,type_rule=elem)
            ruleDict = serializers.serialize("json", rules)
            res = json.loads(ruleDict)
            list_rules=[]
            for i in range(0, len(res)):
                interfaceDict=[]
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
          all_rules[resInterface[x]['fields']['name_interface']]=rules_type
        return all_rules
def getAllGateways(request):
    if (request.method == 'GET'):
        gateways = Gateway.objects.all()
        gatewaysDict = serializers.serialize("json", gateways)
        res = json.loads(gatewaysDict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_gateways.append({
                "gwname":res[i]['fields']['gwname'],
                "gwaddress":res[i]['fields']['gwaddress'],
                })
    return list_gateways
def getAllStaticGateways(request,ipv4_gw):
    if (request.method == 'GET'):
        gateways= Gateway.objects.filter(Q(staticgw=True)&Q(ipv4_gw=ipv4_gw))
        gatewaysDict = serializers.serialize("json", gateways)
        res = json.loads(gatewaysDict)
        list_gateways=[]
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            list_gateways.append(res[i]['fields'])
    return  list_gateways

def AllInterfaces(request):
    list_interface = []
    if (request.method == 'GET'):
        interfaces = Interface.objects.all()
        interfaceDict=serializers.serialize("json",interfaces)
        # interfaceDict = serializers.serialize("json", interfaces)
        res = json.loads(interfaceDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            # if not res[i]['fields']['ifname'].lower().startswith(("tun", "tap")):
            list_interface.append(res[i]['fields'])
        return list_interface
####
def AllInterfacesVersion2(request):
    list_interface = []
    if (request.method == 'GET'):
        interfaces = Interface.objects.all()
        interfaceDict=serializers.serialize("json",interfaces)
        # interfaceDict = serializers.serialize("json", interfaces)
        res = json.loads(interfaceDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields']['id'] = id
            if not res[i]['fields']['ifname'].lower().startswith(("tun", "tap")):
                list_interface.append(res[i]['fields'])
        return list_interface    
    
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
        ###
        IPV4ConfigObjectDict = serializers.serialize("json", IPV4ConfigObject)
        resultat = json.loads(IPV4ConfigObjectDict)
       
        if resultat != []:
            id = resultat[0]['pk']
            resultat[0]['fields']['id'] = id
            resultat[0].pop('model')
            resultat[0].pop('pk')
            resultat[0]['fields'].pop('interface')
            resultat[0]['fields']['addrgw']=""
            ### get gateway4 from table intermediaire
            if GatewayInterface.objects.filter(Q(interface=interfaceObject.id)& Q(ipv4_gw_interface=True)).exists():
                GatewayInterfaceObject=GatewayInterface.objects.get(Q(interface=interfaceObject.id)& Q(ipv4_gw_interface=True))
                gateway_id=GatewayInterfaceObject.gateway_id
                addrgw4=Gateway.objects.get(Q(id=gateway_id) & Q(ipv4_gw=True)).gwaddress
                resultat[0]['fields']['addrgw']=addrgw4
            info['IPV4Config']=resultat[0]['fields']
        else:
            info['IPV4Config']=[]
        
        ##############ipv6    
        IPV6ConfigObject = IP6Config.objects.filter(interface_id=interfaceObject.id)
        ###
        IPV6ConfigObjectDict = serializers.serialize("json", IPV6ConfigObject)
        resultat6 = json.loads(IPV6ConfigObjectDict)
       
        if resultat6 != []:
            id = resultat6[0]['pk']
            resultat6[0]['fields']['id'] = id
            resultat6[0].pop('model')
            resultat6[0].pop('pk')
            resultat6[0]['fields'].pop('interface')
            resultat6[0]['fields']['addrgw6']=""
            ### get gateway4 from table intermediaire
            if GatewayInterface.objects.filter(Q(interface=interfaceObject.id)& Q(ipv4_gw_interface=False)).exists():
                GatewayInterfaceObject=GatewayInterface.objects.get(Q(interface=interfaceObject.id)& Q(ipv4_gw_interface=False))
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

@login_required(login_url='/')
def user_certificate_managment_page(request):
    usr=getUsers(request)
    grp=getGroups(request)
    srv=getServers(request)
    context = {'users':usr,"groups":grp,"servers":srv}
    return render(request, 'user_certificate_managment.html',context)

@login_required(login_url='/')
def interface_page(request):
    interfaces=AllInterfacesVersion2(request)
    config={}
    allStaticGateways={}
    for i in range(len(interfaces)):
        IPV4Config=GetInformationsByInterface(request, interfaces[i]['name_interface'])
        config[interfaces[i]['name_interface']]=IPV4Config
    # IPV4Config=GetInformationsByInterface(request, interfaces[0]['name_interface'])
    allStaticGatewaysIPV4=getAllStaticGateways(request,ipv4_gw=True)
    allStaticGatewaysIPV6=getAllStaticGateways(request,ipv4_gw=False)
    allStaticGateways['ipv4_gw']=allStaticGatewaysIPV4
    allStaticGateways['ipv6_gw']=allStaticGatewaysIPV6
    ##pour le moment on ajoute ce ligne
    allStaticGateways=allStaticGatewaysIPV4
    ###
    context = {'interfaces':interfaces,'IPV4Config':config,'allStaticGateways':allStaticGateways}
    return render(request, 'interface_page.html',context)

@login_required(login_url='/')
def firewall_page(request):
    rules=GetAllRules(request)
    interfaces=AllInterfaces(request)
    context = {'rules':rules, 'interfaces':interfaces}
    return render(request, 'firewall_page.html',context)

@login_required(login_url='/')
def settings_page(request):
    return render(request, 'settings_page.html')

@login_required(login_url='/')
def openvpn_page(request):
    servers=get_all_server_openvpn()
    clients=get_all_client_openvpn()
    context = {'servers':servers,'clients':clients}
    return render(request, 'openvpn_page.html', context)
@login_required(login_url='/')
def ipsec_page(request):
    servers=get_all_server_ipsec()
    publicKey =get_all_public_key()
    context = {'servers':servers,'publicKey':publicKey}
    return render(request, 'ipsec_page.html', context)

@login_required(login_url='/')
def keyPair_page(request):
    privateKey =get_all_private_key()
    publicKey =get_all_public_key()
    context = {'privateKey':privateKey,'publicKey':publicKey}
    return render(request, 'keyPair_page.html',context)


def login(request):
    usr=getAllUsers(request)
    print (usr)

    context = {'users':usr}
    print (context)
    return render(request, 'login.html',context)


@login_required(login_url='/')
def index_page(request):
    info=get_system_infomations()
    gateways=getAllGateways(request)
    interfaces=AllInterfacesVersion2(request)
    config=[]
    for i in range(len(interfaces)):
        info_interface={}
        IPV4Config=GetInformationsByInterface(request, interfaces[i]['name_interface'])
        speed_duplex=""
        ip_address=""
        if "speed_duplex" in IPV4Config['genericConfig'] :
            speed_duplex=IPV4Config['genericConfig']['speed_duplex']
        if "ip_address" in IPV4Config['IPV4Config'] :
            ip_address=IPV4Config['IPV4Config']['ip_address']
        info_interface={
            "name_interface":interfaces[i]['name_interface'],
            "speed_duplex":speed_duplex,
            "ip_address":ip_address}
        config.append(info_interface)
    context = {"informations":info,"gateways":json.dumps(gateways),"interfaces":json.dumps(config)}
    print(context)
    return render(request, 'index_page.html',context)

def error_404_view(request, exception):
    return render(request,'404.html',status=404)