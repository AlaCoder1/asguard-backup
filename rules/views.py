from django.shortcuts import render
from network.serializers import *
from .models import *
from settings.serializers import *
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
from authentification.views import *
from network.address import *
from .functions import *
from django.core import serializers
# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def GetAllRules(request):
    if (request.method == 'GET'):
        rules = Rule.objects.all()
        ruleDict = serializers.serialize("json", rules)
        resRules = json.loads(ruleDict)
        return JsonResponse({"Rules:": resRules})
      
@api_view(['GET'])
@permission_classes([AllowAny])
def GetRulesByInterface(request,id):
    if (request.method == 'GET'):
        rules= Rule.objects.filter(interface_id=id)
        print("rules",rules)
        ruleDict = serializers.serialize("json", rules)
        resRules = json.loads(ruleDict)
        return JsonResponse({"Rules:": resRules})
            
@api_view(['POST'])
@permission_classes([AllowAny])
def addRule(request,id):
    if (request.method == 'POST'):
        #get object of interface type
        interfaceObject= Interface.objects.get(id=id)
        #get interface name to execute command systeme
        ifname=interfaceObject.ifname
        data = JSONParser().parse(request)
        policy=data.get('policy', None)
        saddr = data.get('saddr', None)
        daddr = data.get('daddr', None)
        sport = data.get('sport', None)
        dport = data.get('dport', None)
        protocol = data.get('protocol', None)
        type_rule = data.get('type_rule', None)
        Rule_description=data.get('Rule_description', None)
        msg="Failed to add rule"
        if init_file_nftables(ifname):
          rule=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule)
          if not Rule.objects.filter(rule=rule).exists():
            add_rule=add_rule_remote(rule,ifname,type_rule)
            if add_rule:
                  data['interface']=id
                  if add_rule_DB(data,rule,type_rule):
                      msg="add rule Successufully!!"
               
        return JsonResponse({"msg:": msg})

@api_view(['DELETE'])
@permission_classes([AllowAny])
###function to delete rule
def deleteRule(request,idInter,id):
      if (request.method == 'DELETE'):
        msg="failed to delete rule!!"
        if (Rule.objects.filter(id=id).exists()):
            rules = Rule.objects.get(id=id)
            rule=rules.rule
            type_rules=rules.type_rule
            # print(rules.interface)
             #get object of interface type
            interfaceObject= Interface.objects.get(id=idInter)
            #get interface name to execute command systeme
            ifname=interfaceObject.ifname
            handle=get_handle_rule(ifname,type_rules,rule)
            print(rules.rule)
            if delete_rule_remote(ifname,type_rules,handle):
                  rules.delete()
                  msg="delete rule Successfully!!"
        return JsonResponse({"msg": msg})
    
@api_view(['PUT'])
@permission_classes([AllowAny])
###function to delete rule
def updateRule(request,idInter,id):
      if (request.method == 'PUT'):
        data = JSONParser().parse(request)
        policy=data.get('policy', None)
        saddr = data.get('saddr', None)
        daddr = data.get('daddr', None)
        sport = data.get('sport', None)
        dport = data.get('dport', None)
        protocol = data.get('protocol', None)
        Rule_description=data.get('Rule_description', None)
        # type_rule = data.get('type_rule', None)
        msg="Failed to update rule!!"
        if (Rule.objects.filter(id=id).exists()):
            rules = Rule.objects.get(id=id)
            rule=rules.rule
            type_rules=rules.type_rule
             #get object of interface type
            interfaceObject= Interface.objects.get(id=idInter)
            #get interface name to execute command systeme
            ifname=interfaceObject.ifname
            handle=get_handle_rule(ifname,type_rules,rule)
            if delete_rule_remote(ifname,type_rules,handle):
                rule=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rules)
                if not Rule.objects.filter(rule=rule).exists():
                    add_rule=add_rule_remote(rule,ifname,type_rules)
                    if add_rule:
                      if update_rule_DB(rule,rules,data) :
                        msg="Update rule Successfully!!"
                  
        return JsonResponse({"msg": msg})
       
    