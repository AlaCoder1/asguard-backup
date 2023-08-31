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
      
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def GetRulesByType(request,name_interface,type_rule):
    if (request.method == 'GET'):
        interfaceObject= Interface.objects.get(name_interface=name_interface)
        rules= Rule.objects.filter(interface=interfaceObject.id,type_rule=type_rule)
        ruleDict = serializers.serialize("json", rules)
        resRules = json.loads(ruleDict)
        return JsonResponse({"Rules:": resRules})      
####

          
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
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def saveRules(request,name_interface):
  msgs=[]
  # msg=''
  if (request.method == 'POST'):
    # parse the incoming information
      data_list = JSONParser().parse(request)
      # data_list = request.data
      #get object of interface type
      interfaceObject= Interface.objects.get(name_interface=name_interface)
      #get interface name to execute command systeme
      ifname=interfaceObject.ifname
      for data in data_list:
        id=None if data.get('id', None) == "" else data.get('id', None)
        policy = data.get('policy', None)
        saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
        daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
        sport = None if data.get('sport', None) == "" else data.get('sport', None)
        dport = data.get('dport', None)
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
        #return rule with attributs
        rule=return_rule(ifname,policy,saddr,daddr,sport,dport,protocol,type_rule)
        #test if rule exist or not with id 
        if (id is not None and Rule.objects.filter(id=id).exists()):
          #test if function update rules is executed successfully
          if update_rules(data,id,ifname,policy,saddr,daddr,sport,dport,protocol):
            #msg to inform successfully updated 
            msg="Your rules was updated successfully!! "
        else:
          #test if rule exist or not with rule
          if not Rule.objects.filter(rule=rule).exists():
            #executed add 
            aux,id=add_rules(data,interfaceObject,ifname,policy,saddr,daddr,sport,dport,protocol,type_rule)
            if aux:
              msg="Your rules was saved successfully!! "
          else:
              id=Rule.objects.get(rule=rule).id
              msg="Nothing to change!! \n" 
        response={"id":id,"rule":rule,"msg":msg}
        msgs.append(response)
  return JsonResponse({"response": msgs})    