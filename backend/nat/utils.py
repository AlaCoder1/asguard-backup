from backend.nat.models import DNat, OneToOneNat, SNat
from backend.nat import utils_system
from django.core import serializers
import json


def save_rules_positions(rules_result:list, nat_type):
    """
    function to update rules positions in database
    """
    nat_type.objects.update(db_position=None)
    for rule in rules_result:
        nat_object = nat_type.objects.get(id=rule['id'])
        nat_object.db_position = rule["db_position"]
        nat_object.save()


def change_position_rule(id_rule:int, new_position:int, nat_type, position_type:str)->list:
    """
    This function changes the position of a rule in the list.
    If the new position is greater than the old position, it moves the rules to the top.
    If the new position is smaller than the old position, it moves the rules to the bottom.
    
    """
    all_rules_object=nat_type.objects.all().order_by(position_type)
    data_rules= json.loads(serializers.serialize("json", all_rules_object))
    all_rules=[{"id":rule['pk'],position_type:rule['fields'][position_type] } for rule in data_rules]
    all_rules_position=[rule[position_type] for rule in all_rules]
    input_rule_update={"id":id_rule,position_type:new_position}
    new_position=input_rule_update[position_type]
    old_position=next((rule for rule in all_rules if rule["id"] == input_rule_update["id"]), None)[position_type]
    result_list = []
    if old_position and new_position:
        if (old_position<new_position):
            result_list=permut_from_top(old_position,new_position,all_rules_position,input_rule_update,
                                        position_type,all_rules)
        elif (old_position>new_position):
            result_list=permut_to_top(old_position,new_position,all_rules_position,input_rule_update,
                                    position_type,all_rules)
    return result_list


def permut_from_top(old_position:int, new_position:int, all_rules_position:list,
                    input_rule_update:dict, position_type:str, all_rules:list[dict] )->list:
    """
    This function takes the old and new position of a rule and returns a list of rules
    that should be in the top of the list before the update.
    """
    result_list=[]
    modified_rules=all_rules[all_rules_position.index(old_position)+1:all_rules_position.index(new_position)+1]
    for i in modified_rules:
        i[position_type]=i[position_type]-1
    result_list=all_rules[0:all_rules_position.index(old_position)]+modified_rules
    result_list.append(input_rule_update)
    result_list+=all_rules[all_rules_position.index(new_position)+1:]
    return result_list


def permut_to_top(old_position:int, new_position:int, all_rules_position:list,
                  input_rule_update:dict, position_type:str, all_rules:list[dict])->list:
    """
    This function takes the old and new position of a rule and returns a list of rules
    that should be in the top of the list after the update.
    """
    result_list=[]
    modified_rules=all_rules[all_rules_position.index(new_position):all_rules_position.index(old_position)]
    for i in modified_rules:
        i[position_type]=i[position_type]+1
    result_list+=all_rules[0:all_rules_position.index(new_position)]
    result_list.append(input_rule_update)
    result_list+=modified_rules+all_rules[all_rules_position.index(old_position)+1:]
    return result_list


def get_rule_handle_position_with_content(rule_content: str, list_nat_rules: list[str]):
    """Get a rule content and extract its handle and position from list of nat rules.
    If the rule doesn't exist in table nat in system then the function return False"""
    for rule_index, rule in enumerate(list_nat_rules):
        if f"{rule} # handle ".find(rule_content) > -1:
            rule_handle = rule.split(" # handle ", 1)[1]
            return rule_handle, rule_index
    return False


def synchronize_rule_database(nat_rule=None, rule_handle=None, rule_position=None, 
                              rule_type="postrouting", is_activated=True):
    """Synchronize nat rule in database with system by updating the rule parameters"""
    nat_rule.rule_status = is_activated
    nat_rule.rule_number = rule_handle
    if rule_type == "postrouting":
        nat_rule.postrouting_position = rule_position
    else:
        nat_rule.prerouting_position = rule_position
    nat_rule.save()


def synchronize_nat_rules():
    """Synchronize nat rules between system and database
    1. Synchronize rules from database to system:
        1.1 Get all activated rules from database
        1.2 Find them in system
        1.3 Extract handle and position for each rules
        1.4 Save this parameters in database
    2. Synchronize rules from system to database"""
    # Delete postrouting and prerouting position saved in database before updating it
    SNat.objects.filter(rule_status=True).update(postrouting_position=None)
    OneToOneNat.objects.filter(rule_status=True).update(postrouting_position=None)
    DNat.objects.filter(rule_status=True).update(prerouting_position=None)
    # Get all activated rules from database
    list_snat = SNat.objects.filter(rule_status=True)
    list_one_to_one_nat = OneToOneNat.objects.filter(rule_status=True)
    list_dnat = DNat.objects.filter(rule_status=True)
    # Get all nat rules in system
    list_postrouting_from_system, list_prerouting_from_system = utils_system.get_list_nat_rules_from_system()
    # Extract handle and position for each rule and synchronize in database
    # SNAT
    for snat in list_snat:
        rule_params = get_rule_handle_position_with_content(snat.rule_content, 
                                                            list_postrouting_from_system)
        if rule_params:
            synchronize_rule_database(snat, rule_params[0], rule_params[1])
        else:
            synchronize_rule_database(snat, is_activated=False)
    
    # One To One NAT
    for one_to_one_nat in list_one_to_one_nat:
        rule_params = get_rule_handle_position_with_content(one_to_one_nat.rule_content, 
                                                            list_postrouting_from_system)
        if rule_params:
            synchronize_rule_database(one_to_one_nat, rule_params[0], rule_params[1])
        else:
            synchronize_rule_database(one_to_one_nat, is_activated=False)
    
    # DNAT
    for dnat in list_dnat:
        rule_params = get_rule_handle_position_with_content(dnat.rule_content, 
                                                            list_prerouting_from_system)
        if rule_params:
            synchronize_rule_database(dnat, rule_params[0], rule_params[1], "prerouting")
        else:
            synchronize_rule_database(dnat, is_activated=False)


def deactivate_all_rules():
    """Deactivating all nat rules:
    1. Deleting them from system
    2. Making rule_status filed False
    3. Making postrouting_position and prerouting_position fields None"""
    utils_system.delete_all_nat_rule_from_system()
    SNat.objects.filter(rule_status=True).update(rule_status=False, 
                                                 postrouting_position=None, 
                                                 rule_number=None)
    OneToOneNat.objects.filter(rule_status=True).update(rule_status=False, 
                                                        postrouting_position=None, 
                                                 rule_number=None)
    DNat.objects.filter(rule_status=True).update(rule_status=False, 
                                                 prerouting_position=None, 
                                                 rule_number=None)


def get_next_nat_handle(rule_nat, chain="postrouting"):
    """Get the next rule handle in system. If the chain is postrouting it must take the minimum between SNAT and OneToOneNat"""
    if chain == "postrouting":
        list_next_snat = SNat.objects.filter(rule_status=True, postrouting_position__gt=rule_nat.postrouting_position)
        list_next_one_to_one_nat = OneToOneNat.objects.filter(rule_status=True, postrouting_position__gt=rule_nat.postrouting_position)
        if len(list_next_snat) > 0:
            next_snat_handle = list_next_snat.order_by('postrouting_position')[0].rule_number
            if len(list_next_one_to_one_nat) > 0:
                next_one_to_one_handle = list_next_one_to_one_nat.order_by('postrouting_position')[0].rule_number
                return min(next_snat_handle, next_one_to_one_handle)
            return next_snat_handle
        elif len(list_next_one_to_one_nat) > 0:
            return list_next_one_to_one_nat.order_by('postrouting_position')[0].rule_number
    else:
        list_next_dnat = DNat.objects.filter(rule_status=True, prerouting_position__gt=rule_nat.prerouting_position)
        if len(list_next_dnat) > 0:
            return list_next_dnat.order_by('prerouting_position')[0].rule_number
    return -1


def input_create_snat(source_address, source_port, destination_address, destination_port, snat_type, 
                      translation_address_from=None, translation_address_to=None, translation_port=None):
    """Return the input of an SNAT rule: source, destination and masking"""
    source = {"address": source_address,
              "port": source_port}
    destination = {"address": destination_address,
                   "port": destination_port}
    masking = ["masquerade"]
    if snat_type == "Static":
        masking = translation_address_from
        if translation_address_to != "":
            masking += f"""-{translation_address_to}"""
        if translation_port != "":
            masking += f""":{translation_port}"""
        masking = ["snat", "ip", "to",  masking]
    
    return source, destination, masking


def input_create_one_to_one_nat(destination_address: str):
    """Return the input of an OneToOneNAT rule: destination"""
    if destination_address != "":
        return destination_address
    return "any"


def input_create_dnat(dnat:DNat):
    source = "any"
    if dnat.source_address != "":
        source = {"address": dnat.source_address,
                    "port": dnat.source_port_from}
        if dnat.source_port_to != "":
            source["port"] += f"""-{dnat.source_port_to}"""

    destination = {"external_address": dnat.external_address,
                    "internal_address": dnat.internal_address}
    
    if dnat.destination_port_from:
        destination["port_forwarding"] = f'{dnat.destination_port_from}-{dnat.destination_port_to}'
        destination["port"] = f' : {dnat.destination_port}'
    else:
        destination["port_forwarding"] = False
    
    return source, destination
