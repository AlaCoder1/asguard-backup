from django.shortcuts import render
from network.serializers import *
from .models import *
from settings.serializers import *
from rest_framework.parsers import JSONParser
import json
from django.core import serializers
from authentification.views import *
from network.address import *
from .functionsVersion1 import *
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
      
@api_view(['POST'])
@permission_classes([AllowAny])
def addRule(request):
    if (request.method == 'POST'):
        data = JSONParser().parse(request)
        policy=data.get('policy', None)
        saddr = data.get('saddr', None)
        daddr = data.get('daddr', None)
        sport = data.get('sport', None)
        dport = data.get('dport', None)
        protocol = data.get('protocol', None)
        type_rule = data.get('type_rule', None)
        rule=return_rule(policy,saddr,daddr,sport,dport,protocol,type_rule)
        error=add_rule_remote(rule,'/etc/rules/{}.conf'.format(type_rule))
        msg="Failed to add rule!!"
        if error:
              if add_rule_DB(rule,type_rule):
                  msg="Successufully add rule!! "
        return JsonResponse({"msg:": msg})

@api_view(['DELETE'])
@permission_classes([AllowAny])
###function to delete rule
def deleteRule(request,id):
      if (request.method == 'DELETE'):
        msg="failed to delete rule!!"
        if (Rule.objects.filter(id=id).exists()):
            rules = Rule.objects.get(id=id)
            rule=rules.rule
            type_rules=rules.type_rule
            print(rules.rule)
            if delete_rule_remote(rule,"/etc/rules/{}.conf".format(type_rules)):
                  rules.delete()
                  msg="delete rule Successfully!!"
        return JsonResponse({"msg": msg})
    
@api_view(['PUT'])
@permission_classes([AllowAny])
###function to delete rule
def updateRule(request,id):
      if (request.method == 'PUT'):
        data = JSONParser().parse(request)
        policy=data.get('policy', None)
        saddr = data.get('saddr', None)
        daddr = data.get('daddr', None)
        sport = data.get('sport', None)
        dport = data.get('dport', None)
        protocol = data.get('protocol', None)
        # type_rule = data.get('type_rule', None)
        msg="Failed to update rule!!"
        if (Rule.objects.filter(id=id).exists()):
            rules = Rule.objects.get(id=id)
            rule=rules.rule
            type_rules=rules.type_rule
            if delete_rule_remote(rule,"/etc/rules/{}.conf".format(type_rules)):
                rule=return_rule(policy,saddr,daddr,sport,dport,protocol,type_rules)
                error=add_rule_remote(rule,"/etc/rules/{}.conf".format(type_rules))
                if error:
                  if update_rule_DB(rule,rules,data) :
                    msg="Update rule Successfully!!"
                  
        return JsonResponse({"msg": msg})
       
    