from django.db.models import Q

from backend.nat.models import DNat, OneToOneNat, SNat
from backend.nat.utils_system import find_nat_in_ruleset
from utils.commands_utils import execute_command_without_arguments


def get_rule_handle_with_position(list_nat_rules:list[str], position):
    """Get a list of nat rules and rule position and return it's handle"""
    
    rule_line = list_nat_rules[position]
    handle_number = rule_line[rule_line.find("# handle "):].replace("# handle ", "")
    return handle_number


def get_rule_handle_in_system(nat_type="postrouting", rule_position=0):
    """Return the last rule handle from ruleset"""
    rule_set = execute_command_without_arguments(["nft", "-a", "list", "table", "nat"])

    list_nat_rules = find_nat_in_ruleset(rule_set.stdout, nat_type)
    handle_number = get_rule_handle_with_position(list_nat_rules, rule_position)
    return handle_number
    
def save_handle_from_system_to_database(list_routing_from_db, list_routing_from_system):
    """Take the list of routing from system (postrouting or prerouting) and save each rule handle in database"""
    # Loop through the list of NAT (SNAT, OneToOne or DNAT) rules reversibly, 
    # get the last rule handle and 
    # remove it from the list 
    for rule_index in range(len(list_routing_from_system)):
        handle_number = get_rule_handle_with_position(list_routing_from_system, rule_index)
        # Save the rule handle in database
        list_routing_from_db[rule_index].rule_number = handle_number
        list_routing_from_db[rule_index].save()


def save_rules_handle_after_reboot():
    # Get list of nat rules from system: postrouting (SNAT and One To One) and prerouting (DNAT)
    ruleset = execute_command_without_arguments(["nft", "-a", "list", "table", "nat"])
    list_postrouting_from_system = find_nat_in_ruleset(ruleset.stdout, "postrouting")
    list_prerouting_from_system = find_nat_in_ruleset(ruleset.stdout, "prerouting")

    # Get all active rules from database
    # Get active rules for chain prerouting (DNAT)
    list_prerouting_from_db = [dnat for dnat in DNat.objects.filter(rule_status=True).order_by("prerouting_position")]
    # Get active rules for chain postrouting (SNAT and OneToOneNat)
    list_postrouting_from_db = [snat for snat in SNat.objects.filter(rule_status=True).order_by("postrouting_position")]
    list_postrouting_from_db.extend([one_to_one_nat for one_to_one_nat in OneToOneNat.objects.filter(rule_status=True).order_by("postrouting_position")])
    # Order by rule number
    list_postrouting_from_db = sorted(list_postrouting_from_db, key=lambda postrouting: postrouting.postrouting_position)
    
    # Save rule handle in database
    save_handle_from_system_to_database(list_postrouting_from_db, list_postrouting_from_system)
    save_handle_from_system_to_database(list_prerouting_from_db, list_prerouting_from_system)


def update_position_nat(chain="postrouting"):
    """Update the activated rules position after the changes like adding or deleting a rule"""
    
    # Get list of nat rules from system: postrouting (SNAT and One To One) or prerouting (DNAT)
    ruleset = execute_command_without_arguments(["nft", "-a", "list", "table", "nat"])
    list_routing_from_system = find_nat_in_ruleset(ruleset.stdout, chain)
    if chain == "postrouting":
        SNat.objects.filter(rule_status=True).update(postrouting_position=None)
        OneToOneNat.objects.filter(rule_status=True).update(postrouting_position=None)
    else:
        DNat.objects.filter(rule_status=True).update(prerouting_position=None)

    for rule_index in range(len(list_routing_from_system)):
        rule_handle = get_rule_handle_with_position(list_routing_from_system, rule_index)
        if chain == "postrouting":
            snat_rules = SNat.objects.filter(rule_number=rule_handle)
            one_to_one_nat_rules = OneToOneNat.objects.filter(rule_number=rule_handle)
            if len(snat_rules) > 0:
                nat_rule = snat_rules[0]
            else:
                nat_rule = one_to_one_nat_rules[0]
            nat_rule.postrouting_position = rule_index + 1
        else:
            nat_rule = DNat.objects.get(rule_number=rule_handle)
            nat_rule.prerouting_position = rule_index + 1
        nat_rule.save()


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


def input_create_snat(snat:SNat):
    source = {"address": snat.source_address,
              "port": snat.source_port}
    destination = {"address": snat.destination_address,
                   "port": snat.destination_port}
    masking = ["masquerade"]
    if snat.snat_type == "Static":
        masking = snat.translation_address_from
        if snat.translation_address_to != "":
            masking += f"""-{snat.translation_address_to}"""
        if snat.translation_port != "":
            masking += f""":{snat.translation_port}"""
        masking = ["snat", "ip", "to",  masking]
    
    return source, destination, masking


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
