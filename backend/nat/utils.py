from backend.nat.models import DNat, OneToOneNat, SNat
from backend.nat.utils_system import find_nat_in_ruleset
from utils.commands_utils import execute_command_without_arguments


def get_last_rule_handle(list_nat_rules:list[str]):
    """Get a list of nat rules and return the last rule handle"""
    
    last_rule = list_nat_rules[-1]
    handle_number = last_rule[last_rule.find("# handle "):].replace("# handle ", "")
    return handle_number


def get_rule_handle_in_system(nat_type="postrouting"):
    """Return the last rule handle from ruleset"""
    rule_set = execute_command_without_arguments(["nft", "-a", "list", "table", "nat"])

    list_nat_rules = find_nat_in_ruleset(rule_set.stdout, nat_type)
    handle_number = get_last_rule_handle(list_nat_rules)
    return handle_number


def save_handle_from_system_to_database(list_routing_from_db, list_routing_from_system):
    """Take the list of routing from system (postrouting or prerouting) and save each rule handle in database"""
    # Loop through the list of NAT (SNAT, OneToOne or DNAT) rules reversibly, 
    # get the last rule handle and 
    # remove it from the list 
    for rule_index in range(len(list_routing_from_db) -1, -1, -1):
        handle_number = get_last_rule_handle(list_routing_from_system)
        # Save the rule handle in database
        list_routing_from_db[rule_index].rule_number = handle_number
        list_routing_from_db[rule_index].save()
        # Remove the rule
        list_routing_from_system.pop()


def save_rules_handle_after_reboot():
    """Synchronize rules handle (SNAT, OneToOne or DNAT) between system and database after rebooting machine."""
    # Get all active rules from database
    # Get active rules for chain prerouting (DNAT)
    list_prerouting_from_db = [dnat for dnat in DNat.objects.filter(rule_status=True).order_by("rule_number")]
    # Get active rules for chain postrouting (SNAT and OneToOneNat)
    list_postrouting_from_db = [snat for snat in SNat.objects.filter(rule_status=True).order_by("rule_number")]
    list_postrouting_from_db.extend([one_to_one_nat for one_to_one_nat in OneToOneNat.objects.filter(rule_status=True).order_by("rule_number")])
    # Order by rule number
    list_postrouting_from_db = sorted(list_postrouting_from_db, key=lambda postrouting: postrouting.rule_number)
    
    # Get list of nat rules from system: postrouting (SNAT and One To One) and prerouting (DNAT)
    ruleset = execute_command_without_arguments(["nft", "-a", "list", "table", "nat"])
    list_postrouting_from_system = find_nat_in_ruleset(ruleset.stdout, "postrouting")
    list_prerouting_from_system = find_nat_in_ruleset(ruleset.stdout, "prerouting")

    # Synchronize handle number for each rule from system to database
    save_handle_from_system_to_database(list_postrouting_from_db, list_postrouting_from_system)
    save_handle_from_system_to_database(list_prerouting_from_db, list_prerouting_from_system)
