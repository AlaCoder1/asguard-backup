from django.shortcuts import render
from managementUsers.views import *
from managementUsers.models import User
from django.contrib.auth.decorators import login_required
from managementServers.models import * 
from network.models import *
from rules.models import *
from gateway.models import *
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
        groups = Group.objects.filter(createdBySystem=0)
        groupDict = serializers.serialize("json", groups)
        res = json.loads(groupDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('createdBySystem')
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
        print(res)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            type = Type.objects.get(id=res[i]['fields']['type'])
            print(type.type_name)
            res[i]['fields']['id'] = id
            res[i]['fields']['type_name'] = type.type_name
            list_servers.append(res[i]['fields'])
        return list_servers

# def GetAllRules(request):
#     if (request.method == 'GET'):
#         interfaceObject= Interface.objects.get(name_interface=name_interface)
#         rules= Rule.objects.filter(interface=interfaceObject.id,type_rule=type_rule)
#         ruleDict = serializers.serialize("json", rules)
#         res = json.loads(ruleDict)
#         for i in range(0, len(res)):
#           interfaceDict=[]
#           res[i].pop('model')
#           id = res[i]['pk']
#           res[i].pop('pk')
#           res[i]['fields']['id'] = id
#           interface=Interface.objects.get(id=res[i]['fields']['interface'])
#           interfaceDict.append({"name":interface.name_interface,"id":interface.id})
#           res[i]['fields']['interface']=interfaceDict
#           list_rules.append(res[i]['fields'])
#         return list_rules
###############
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
              list_rules.append(res[i]['fields'])
             ########## 
            rules_type[elem]=list_rules
          all_rules[resInterface[x]['fields']['name_interface']]=rules_type
        return all_rules
#################"Gateways
############ getAll
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
            list_gateways.append(res[i]['fields'])
    return list_gateways
############# GET static
def getAllStaticGateways(request):
    if (request.method == 'GET'):
        gateways= Gateway.objects.filter(staticgw=True)
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

##########    
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
            list_interface.append(res[i]['fields'])
        return list_interface

#########
@login_required(login_url='/')
def index_page(request):
    usr=getUsers(request)
    grp=getGroups(request)
    srv=getServers(request)
    context = {'users':usr,"groups":grp,"servers":srv}
    print(context)
    return render(request, 'index_page.html',context)

@login_required(login_url='/')
def user_certificate_managment_page(request):
    usr=getUsers(request)
    grp=getGroups(request)
    srv=getServers(request)
    context = {'users':usr,"groups":grp,"servers":srv}
    print(context)
    return render(request, 'user_certificate_managment.html',context)

@login_required(login_url='/')
def lan_page(request):
    return render(request, 'lan_page.html')
    lan=getNetworkData(request)
    context = {'lan':lan}
    return render(request, 'lan_page.html',context)

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
    return render(request, 'openvpn_page.html')

def login(request):
    usr=getAllUsers(request)
    context = {'users':usr}
    return render(request, 'login.html',context)

def index_page_test(request):
    
    tab = "fefef"
    context = {'tab':tab}
    return render(request, 'index_page_test.html' ,context)
