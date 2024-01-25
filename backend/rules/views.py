from django.shortcuts import render
from backend.network.serializers import *
from .models import *
# from settings.serializers import *
from rest_framework.parsers import JSONParser
import json
from rest_framework.authentication import SessionAuthentication
from django.core import serializers
from backend.authentification.views import *
from backend.network.address import *
# Version without SSh connection
from .functions import *
from django.db.models import Q
from django.core import serializers
# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
##API to get all Rules
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
              list_rules.append(res[i]['fields'])
             ########## 
            rules_type[elem]=list_rules
          all_rules[resInterface[x]['fields']['name_interface']]=rules_type
 
        return JsonResponse({"Rules:": all_rules})
      

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
###function to delete rule
def deleteRule(request,id):
      if (request.method == 'DELETE'):
        msg="failed to delete rule!!"
        #tester si rule exist ou non
        if (Rule.objects.filter(id=id).exists()):
            rules = Rule.objects.get(id=id)
            rule=rules.rule
            type_rules=rules.type_rule
             #get object of interface type
            interfaceObject= Interface.objects.get(id=rules.interface_id)
            #get interface name to execute command systeme
            ifname=interfaceObject.ifname
             #appel la fonction pour retrouver handle rule à supprimer
            handle=get_handle_rule(ifname,type_rules,rule)
             #appel la fonction pour supprimer  rule avec handle déjà retrouvé(système)
            if handle is not None:
              #appel la fonction pour supprimer  rule avec handle déjà retrouvé  (système)
              return_delete_rule_remote=delete_rule_remote(ifname,type_rules,handle)
              if return_delete_rule_remote is True:
                #appel la fonction pour supprimer  rule de la base de données 
                rules.delete()
                msg="delete rule Successfully!!"
                status=200
              else:
                msg=return_delete_rule_remote
                status=400 
            else:
              msg="Rule not exist in system!!"
              status=400 
        else:
          msg="Rule not exist in database!!"
          status=400
        return JsonResponse({"msg": msg},status=status)
      
    
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def addRule(request,name_interface):
  msg=''
  if (request.method == 'POST'):
    # parse the incoming information
    data =request.data
    #get object of interface type
    interfaceObject= Interface.objects.get(name_interface=name_interface)
    #get interface name to execute command systeme
    ifname=interfaceObject.ifname
    policy = data.get('policy', None)
    saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
    daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
    sport = None if data.get('sport', None) == "" else data.get('sport', None)
    dport = None if data.get('dport', None) == "" else data.get('dport', None)
    protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
    type_rule = data.get('type_rule', None)
    rule_description=data.get('rule_description', None)
    config=get_config_file(ifname)
    #appel la fonction pour initialiser les fichies nftables.conf
    return_init_file_nftables = init_file_nftables(ifname)
    if return_init_file_nftables:
      #appel la fonction pour retourner rule à ajouter 
      rule=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule)
      if not Rule.objects.filter(Q(rule=rule) | Q(rule_description=rule_description)).exists():
      #appel la fonction pour ajouter rule dans le système
        return_add_rule=add_rule_remote(rule,ifname,type_rule,config,rule_description)
        if return_add_rule is True:
          data = {
              'policy': policy,
              'saddr':saddr,
              'daddr': daddr,
              'sport': sport,
              'dport': dport,
              'protocol': protocol,
              'type_rule': type_rule,
              'rule_description': rule_description
              }
          data['interface']=interfaceObject.id
          #appel la fonction pour ajouter rule dans la base de données 
          data={key: value for key, value in data.items() if value is not None}
          data['rule']=rule
          data["rule_status"]=True
          data["type_rule"]=type_rule
          InboundSerializer = RuleSerializer(data=data)
          InboundSerializer.is_valid(raise_exception=True)
          if InboundSerializer.is_valid():
            InboundSerializer.save()
            id=Rule.objects.get(rule=rule).pk
            msg = "Rule added Successfully!!"
            status=200
          else:
            msg = InboundSerializer.errors
            status=400
        else:
          msg = return_add_rule
          status=400
      else:
        msg="Rule already exist!"
        status=400
    else:
      msg = return_init_file_nftables
      status=400
  return JsonResponse({"response": msg},status=status)    
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def updateRule(request,name_interface):
  msg=''
  if (request.method == 'PUT'):
    # parse the incoming information
    data =request.data
    #get object of interface type
    interfaceObject= Interface.objects.get(name_interface=name_interface)
    #get interface name to execute command systeme
    ifname=interfaceObject.ifname
    id=data.get('id', None)
    policy = data.get('policy', None)
    saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
    daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
    sport = None if data.get('sport', None) == "" else data.get('sport', None)
    dport = None if data.get('dport', None) == "" else data.get('dport', None)
    protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
    rule_description=data.get('rule_description', None)
    #test if rule exist or not with id 
    if (id is not None and Rule.objects.filter(id=id).exists()):
      rulesObject = Rule.objects.get(id=id)
      rule=rulesObject.rule
      type_rules=rulesObject.type_rule
      description=rulesObject.rule_description
      file_path="/etc/rules/{}/nftables.conf".format(ifname)
      #appel la fonction pour retourner rule à ajouter 
      ruleupdate=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rules)
      update_remote=update_rule_remote(rule+" #"+description,ruleupdate+" #"+rule_description,file_path)
      if  update_remote is True:
              data = {
              "id":id,
              'policy': policy,
              'saddr':saddr,
              'daddr': daddr,
              'sport': sport,
              'dport': dport,
              'protocol': protocol,
              'rule_description': rule_description
              }
              
              #appel la fonction pour update rule dans la base de données 
              # data={key: value for key, value in data.items() if value is not None}
              data['interface']=rulesObject.interface_id
              data['rule']=ruleupdate
              InboundSerializer = RuleSerializer(rulesObject,data=data)
              # InboundSerializer.is_valid(raise_exception=True)
              if InboundSerializer.is_valid():
                InboundSerializer.save()
                msg = "Rule updated Successfully!!"
                status=200
              else:
                msg= InboundSerializer.errors
                status=400
      else:
          msg=update_remote
          status=400
    else:
        msg="Rule not exist"
        status=400
  return JsonResponse({"response": msg},status=status)    
    