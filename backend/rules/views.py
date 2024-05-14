from django.http import JsonResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes

from backend.network.models import Interface
from backend.rules.functions import add_rule_remote, calculate_subnet_address, delete_rule_remote, get_handle_rule, init_file_nftables, return_rule
from backend.rules.models import Rule
from backend.rules.serializers import RuleSerializer


# Constants
CONSTANT_RULE = _('Rule')
# Success messages
SUCCESS_MESSAGES_CREATING = _("is created")
SUCCESS_MESSAGES_DELETING = _("is deleted")
SUCCESS_MESSAGES_UPDATING = _("is updated")
# Error messages
ERROR_MESSAGES_CREATING = _("Error in creating")
ERROR_MESSAGES_DELETING = _("Error in deleting")
ERROR_MESSAGES_UPDATING = _("Error in updating")
ERROR_MESSAGES_EXISTANT = _("already exist")
ERROR_MESSAGES_INEXISTANT = _("does not exist")


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_rule(request,id):
    """function to delete rule"""
    if (request.method == 'DELETE'):
        #tester si rule exist ou non
        if (Rule.objects.filter(id=id).exists()):
            rules = Rule.objects.get(id=id)
            rule=rules.rule
            type_rules=rules.type_rule
             #get object of interface type
            interface_object= Interface.objects.get(id=rules.interface_id)
            #get interface name to execute command systeme
            ifname=interface_object.ifname
             #appel la fonction pour retrouver handle rule à supprimer
            handle=get_handle_rule(ifname,type_rules,rule)
             #appel la fonction pour supprimer  rule avec handle déjà retrouvé(système)
            if handle:
                #appel la fonction pour supprimer  rule avec handle déjà retrouvé  (système)
                return_delete_rule_remote=delete_rule_remote(ifname,type_rules,handle)
                if return_delete_rule_remote:
                    #appel la fonction pour supprimer  rule de la base de données 
                    rules.delete()
                    return JsonResponse({"msg": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_DELETING}"}, status=200)
                return JsonResponse({"msg": f"{ERROR_MESSAGES_DELETING} {CONSTANT_RULE}"}, status=400)
            return JsonResponse({"msg": f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
        return JsonResponse({"msg": f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_rule(request,name_interface):
    # parse the incoming information
    data =request.data
    #get object of interface type
    interface_object= Interface.objects.get(name_interface=name_interface)
    #get interface name to execute command systeme
    ifname=interface_object.ifname
    policy = data.get('policy', None)
    saddr = None if data.get('saddr', None) == "" else data.get('saddr', None)
    daddr = None if data.get('daddr', None) == "" else data.get('daddr', None)
    sport = None if data.get('sport', None) == "" else data.get('sport', None)
    dport = None if data.get('dport', None) == "" else data.get('dport', None)
    protocol = None if data.get('protocol', None) == "" else data.get('protocol', None)
    type_rule = data.get('type_rule', None)
    rule_description=data.get('rule_description', None)
    # config=get_config_file(ifname)
    #appel la fonction pour initialiser les fichies nftables.conf
    return_init_file_nftables = init_file_nftables(ifname)
    if return_init_file_nftables:
      #appel la fonction pour retourner rule à ajouter 
      rule=return_rule(policy,saddr,daddr,sport,dport,protocol,type_rule)
      # if not Rule.objects.filter(Q(rule=rule) & ((Q(interface_id=interface_object.pk)& Q(type_rule!=type_rule ) )|(Q(interface_id!=interface_object.pk) & Q(type_rule=type_rule )))).exists():
      if not Rule.objects.filter(
            Q(rule=rule) & (
                (Q(interface_id=interface_object.pk) ) &
                (Q(type_rule=type_rule))
            )
        ).exists():
      #appel la fonction pour ajouter rule dans le système
        return_add_rule=add_rule_remote(rule,ifname,type_rule)
        if return_add_rule:
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
          data['interface']=interface_object.id
          #appel la fonction pour ajouter rule dans la base de données 
          data={key: value for key, value in data.items() if value is not None}
          saddr_db=calculate_subnet_address(saddr)
          daddr_db=calculate_subnet_address(daddr)
          rule_db=return_rule(policy,saddr_db,daddr_db,sport,dport,protocol,type_rule)
          data['rule']=rule_db
          data["rule_status"]=True
          data["type_rule"]=type_rule
          rule_serializer = RuleSerializer(data=data)
          # rule_serializer.is_valid(raise_exception=True)
          if rule_serializer.is_valid():
            rule_serializer.save()
            return JsonResponse({"response": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_CREATING}"}, status=200)
          return JsonResponse({"response": rule_serializer.errors}, status=400)
        return JsonResponse({"response": f"{ERROR_MESSAGES_CREATING} {CONSTANT_RULE}"}, status=400)
      return JsonResponse({"response": f"{CONSTANT_RULE} {ERROR_MESSAGES_EXISTANT}"}, status=400)
    return JsonResponse({"response": f"{ERROR_MESSAGES_CREATING} {CONSTANT_RULE}"}, status=400)


@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def update_rule(request,name_interface):
    # parse the incoming information
    data =request.data
    #get object of interface type
    interface_object= Interface.objects.get(name_interface=name_interface)
    #get interface name to execute command systeme
    ifname=interface_object.ifname
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
        rules_object = Rule.objects.get(id=id)
        rule=rules_object.rule
        type_rules=rules_object.type_rule
        #appel la fonction pour retourner rule à ajouter 
        ruleupdate=return_rule(policy,saddr,daddr,sport,dport,protocol,type_rules)
        handle=get_handle_rule(ifname,type_rules,rule)
        if handle:
            return_delete_rule_remote=delete_rule_remote(ifname,type_rules,handle)
            if return_delete_rule_remote:
                return_add_rule=add_rule_remote(ruleupdate,ifname,type_rules)
                if  return_add_rule:
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
                    data['interface']=rules_object.interface_id
                    saddr_db=calculate_subnet_address(saddr)
                    daddr_db=calculate_subnet_address(daddr)
                    rule_db_update=return_rule(policy,saddr_db,daddr_db,sport,dport,protocol,type_rules)
                    data['rule']=rule_db_update
                    rule_serializer = RuleSerializer(rules_object,data=data)
                    if rule_serializer.is_valid():
                        rule_serializer.save()
                        return JsonResponse({"response": f"{CONSTANT_RULE} {SUCCESS_MESSAGES_UPDATING}"}, status=200)
                    return JsonResponse({"response": rule_serializer.errors}, status=400)
            return JsonResponse({"response": f"{ERROR_MESSAGES_UPDATING} {CONSTANT_RULE}"}, status=400)
        return JsonResponse({"response": f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)

    return JsonResponse({"response": f"{CONSTANT_RULE} {ERROR_MESSAGES_INEXISTANT}"}, status=400)
    