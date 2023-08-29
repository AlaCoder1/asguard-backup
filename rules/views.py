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
        policy=data.get('policy', None)
        saddr = data.get('saddr', None)
        daddr = data.get('daddr', None)
        sport = data.get('sport', None)
        dport = data.get('dport', None)
        protocol = data.get('protocol', None)
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
              if delete_rule_remote(ifname,type_rules,handle):
                #appel la fonction pour supprimer  rule de la base de données 
                    rules.delete()
                    msg="delete rule Successfully!!"
        return JsonResponse({"msg": msg})
    
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
###function to delete rule
def updateRule(request,id):
      if (request.method == 'PUT'):
        data = request.data
        policy=data.get('policy', None)
        saddr = data.get('saddr', None)
        daddr = data.get('daddr', None)
        sport = data.get('sport', None)
        dport = data.get('dport', None)
        protocol = data.get('protocol', None)
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
       
    