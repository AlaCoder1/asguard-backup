from django.shortcuts import render
from network.serializers import *
from .models import *
from settings.serializers import *
from rest_framework.parsers import JSONParser
import json
from rest_framework.authentication import SessionAuthentication
from django.core import serializers
from authentification.views import *
from network.address import *
from .functions import *
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def GetAllRules(request):
    if (request.method == 'GET'):
        rules = Rule.objects.all()
        ruleDict = serializers.serialize("json", rules)
        resRules = json.loads(ruleDict)
        return JsonResponse({"Rules:": resRules})
      
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def GetRulesByInterface(request,name_interface):
    if (request.method == 'GET'):
        interfaceObject= Interface.objects.get(name_interface=name_interface)
        rules= Rule.objects.filter(interface=interfaceObject.id)
        ruleDict = serializers.serialize("json", rules)
        resRules = json.loads(ruleDict)
        return JsonResponse({"Rules:": resRules})
      
# @api_view(['GET'])
# @authentication_classes([SessionAuthentication])
# #@permission_classes([IsAuthenticated])
# def GetRulesByType(request,name_interface,type_rule):
#     if (request.method == 'GET'):
#         interfaceObject= Interface.objects.get(name_interface=name_interface)
#         rules= Rule.objects.filter(interface=interfaceObject.id,type_rule=type_rule)
#         ruleDict = serializers.serialize("json", rules)
#         resRules = json.loads(ruleDict)
#         return JsonResponse({"Rules:": resRules})      
####
@csrf_exempt
# @api_view(['GET'])
# @authentication_classes([SessionAuthentication])
# #@permission_classes([IsAuthenticated])
# def GetRulesByType(request,name_interface,type_rule):
#     if (request.method == 'GET'):
#         interfaceObject= Interface.objects.get(name_interface=name_interface)
#         rules= Rule.objects.filter(interface=interfaceObject.id,type_rule=type_rule)
#         ruleDict = serializers.serialize("json", rules)
#         resRules = json.loads(ruleDict)
#         return JsonResponse({"Rules:": resRules})      
####
@csrf_exempt
def GetRulesByType(request,name_interface,type_rule):
    list_rules = []
    if (request.method == 'GET'):
        interfaceObject= Interface.objects.get(name_interface=name_interface)
        rules= Rule.objects.filter(interface=interfaceObject.id,type_rule=type_rule)
        ruleDict = serializers.serialize("json", rules)
        res = json.loads(ruleDict)
        for i in range(0, len(res)):
          interfaceDict=[]
          res[i].pop('model')
          id = res[i]['pk']
          res[i].pop('pk')
          res[i]['fields']['id'] = id
          interface=Interface.objects.get(id=res[i]['fields']['interface'])
          interfaceDict.append({"name":interface.name_interface,"id":interface.id})
          res[i]['fields']['interface']=interfaceDict
          list_rules.append(res[i]['fields'])
        return JsonResponse({"Rules:": list_rules})
        res = json.loads(ruleDict)
        for i in range(0, len(res)):
          interfaceDict=[]
          res[i].pop('model')
          id = res[i]['pk']
          res[i].pop('pk')
          res[i]['fields']['id'] = id
          interface=Interface.objects.get(id=res[i]['fields']['interface'])
          interfaceDict.append({"name":interface.name_interface,"id":interface.id})
          res[i]['fields']['interface']=interfaceDict
          list_rules.append(res[i]['fields'])
        return JsonResponse({"Rules:": list_rules})
          
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def addRule(request,name_interface):
    if (request.method == 'POST'):
        #get object of interface type
        interfaceObject= Interface.objects.get(name_interface=name_interface)
        #get interface name to execute command systeme
        ifname=interfaceObject.ifname
        data = request.data
        policy = data.get('policy', None)
        saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
        daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
        sport = None if data.get('sport', None) == "" else data.get('sport', None)
        dport = data.get('dport', None)
        protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
        type_rule = data.get('type_rule', None)
        Rule_description=data.get('Rule_description', None)
        msg="Failed to add rule"
        #appel la fonction pour initialiser les fichies nftables.conf
        if init_file_nftables(ifname):
          #appel la fonction pour retourner rule à ajouter 
          rule=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule)
          if not Rule.objects.filter(rule=rule).exists():
          #appel la fonction pour ajouter rule dans le système
            add_rule=add_rule_remote(rule,ifname,type_rule)
            if add_rule:
                  data['interface']=interfaceObject.id
                   #appel la fonction pour ajouter rule dans la base de données 
                  if add_rule_DB(data,rule,type_rule):
                      msg="add rule Successufully!!"
               
        return JsonResponse({"msg:": msg})

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
###function to delete rule
# def deleteRule(request,idInter,id):
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
              if return_delete_rule_remote:
                #appel la fonction pour supprimer  rule de la base de données 
                rules.delete()
                msg="delete rule Successfully!!"
              else:
                msg=return_delete_rule_remote
            else:
              msg="Rule not exist in system!!"
        else:
          msg="Rule not exist in database!!"
        return JsonResponse({"msg": msg})
    
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
###function to delete rule
def updateRule(request,id):
      if (request.method == 'PUT'):
        data = request.data
        policy = data.get('policy', None)
        saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
        daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
        sport = None if data.get('sport', None) == "" else data.get('sport', None)
        dport = data.get('dport', None)
        protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
        type_rule = data.get('type_rule', None)
        Rule_description=data.get('Rule_description', None)
        # type_rule = data.get('type_rule', None)
        msg="Failed to update rule!!"
        #tester si rule exist ou non
        if (Rule.objects.filter(id=id).exists()):
            rulesObject = Rule.objects.get(id=id)
            rule=rulesObject.rule
            type_rules=rulesObject.type_rule
             #get object of interface type
            interfaceObject= Interface.objects.get(id=rulesObject.interface_id)
            #get interface name to execute command systeme
            ifname=interfaceObject.ifname
            #appel la fonction pour retrouver handle rule à supprimer
            handle=get_handle_rule(ifname,type_rules,rule)
             #appel la fonction pour supprimer  rule avec handle déjà retrouvé  (système)
            if delete_rule_remote(ifname,type_rules,handle):
                 #appel la fonction pour retourner rule à ajouter 
                ruleupdate=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rules)
                if not Rule.objects.filter(rule=ruleupdate).exists():
                #appel la fonction pour ajouter rule dans le système
                    add_rule=add_rule_remote(ruleupdate,ifname,type_rules)
                    if add_rule:
                      #appel la fonction pour update rule dans la base de données 
                      data['interface']=rulesObject.interface_id
                      if update_rule_DB(ruleupdate,rulesObject,data) :
                        msg="Update rule Successfully!!"
                  
        return JsonResponse({"msg": msg})
# @api_view(['POST'])
# @authentication_classes([SessionAuthentication])

@csrf_exempt
def saveRules(request,name_interface):
  msgs=[]
  msg=''
  if (request.method == 'POST'):
    # parse the incoming information
    data_list = JSONParser().parse(request)
    #get object of interface type
    interfaceObject= Interface.objects.get(name_interface=name_interface)
    #get interface name to execute command systeme
    ifname=interfaceObject.ifname
    for data in data_list:
      id=data.get('id', None)
      policy = data.get('policy', None)
      saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
      daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
      sport = None if data.get('sport', None) == "" else data.get('sport', None)
      dport = None if data.get('dport', None) == "" else data.get('dport', None)
      protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
      type_rule = data.get('type_rule', None)
      Rule_description=data.get('Rule_description', None)
      data = {
        "id":id,
        'policy': policy,
        'saddr':saddr,
        'daddr': daddr,
        'sport': sport,
        'dport': dport,
        'protocol': protocol,
        'type_rule': type_rule,
        'Rule_description': Rule_description
        }
      #test if rule exist or not with id 
      if (id is not None and Rule.objects.filter(id=id).exists()):
        rulesObject = Rule.objects.get(id=id)
        rule=rulesObject.rule
        type_rules=rulesObject.type_rule
        #appel la fonction pour retrouver handle rule à supprimer
        handle=get_handle_rule(ifname,type_rules,rule)
        #appel la fonction pour supprimer  rule avec handle déjà retrouvé  (système)
        return_delete_rule_remote=delete_rule_remote(ifname,type_rules,handle)
        if return_delete_rule_remote:
          #appel la fonction pour retourner rule à ajouter 
          ruleupdate=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rules)
          if not Rule.objects.filter(rule=ruleupdate).exists():
          #appel la fonction pour ajouter rule dans le système
            return_add_rule=add_rule_remote(ruleupdate,ifname,type_rules)
            if return_add_rule:
                #appel la fonction pour update rule dans la base de données 
                data={key: value for key, value in data.items() if value is not None}
                data['interface']=rulesObject.interface_id
                data['rule']=rule
                InboundSerializer = RuleSerializer(rulesObject,data=data)
                InboundSerializer.is_valid(raise_exception=True)
                if InboundSerializer.is_valid():
                  InboundSerializer.save()
                  msg = "ya3tik esa7a sar el update"
                else:
                  msg= InboundSerializer.errors
            else:
              msg= return_add_rule
          else:
            msg = "hathi mawjouda y 3ami"
        else:
          msg = return_delete_rule_remote
      else:
        #appel la fonction pour initialiser les fichies nftables.conf
        return_init_file_nftables = init_file_nftables(ifname)
        if return_init_file_nftables:
          #appel la fonction pour retourner rule à ajouter 
          rule=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule)
          if not Rule.objects.filter(rule=rule).exists():
          #appel la fonction pour ajouter rule dans le système
            return_add_rule=add_rule_remote(rule,ifname,type_rule)
            if return_add_rule:
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
                
                msg = "Rule Saved Successfully!!"
              else:
                msg = InboundSerializer.errors
          else:
            msg = return_add_rule
        else:
          msg = return_init_file_nftables
  return JsonResponse({"response": msg})    