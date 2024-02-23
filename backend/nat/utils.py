from backend.nat.models import DNat, SNat
from backend.nat.utils_system import find_nat_in_ruleset
from utils.commands_utils import execute_command_without_arguments


def get_last_rule_handle(list_snat_rules:list[str]):
    """Get a list of nat rules and return the last rule handle"""
    
    last_rule = list_snat_rules[-1]
    handle_number = last_rule[last_rule.find("# handle "):].replace("# handle ", "")
    return handle_number


def get_rule_handle_in_system(nat_type="postrouting"):
    """Return the last rule handle from ruleset"""
    rule_set = execute_command_without_arguments(["nft", "-a", "list", "ruleset"])

    list_snat_rules = find_nat_in_ruleset(rule_set.stdout, nat_type)
    handle_number = get_last_rule_handle(list_snat_rules)
    return handle_number



def save_rules_handle_after_reboot(nat_type="postrouting"):
    """Synchronize rules handle (SNAT, OneToOne or DNAT) between system and database after rebooting machine."""
    # Get all active rules
    if nat_type == "postrouting":
        list_active_rules = SNat.objects.filter(rule_status=True).order_by("rule_number")
    else:
        list_active_rules = DNat.objects.filter(rule_status=True).order_by("rule_number")

    # Get list of snat rules from system
    ruleset = execute_command_without_arguments(["nft", "-a", "list", "ruleset"])
    list_snat_rules = find_nat_in_ruleset(ruleset.stdout, nat_type)

    # Loop through the list of rules reversibly, get the last rule handle and remove it from the list 
    for rule_index in range(len(list_active_rules) -1, -1, -1):
        handle_number = get_last_rule_handle(list_snat_rules)
        # Save the rule handle in database
        list_active_rules[rule_index].rule_number = handle_number
        list_active_rules[rule_index].save()
        # Remove the rule
        list_snat_rules.pop()
