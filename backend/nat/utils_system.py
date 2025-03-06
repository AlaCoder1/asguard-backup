from backend.nat.contant_variables import PATH_RULESET_NFT
from backend.nat import utils
from utils.commands_utils import execute_command_without_arguments, get_current_directory, write_file_from_system


def get_list_nat_rules_from_system():
    """Get list of nat rules from system: 
    1. postrouting (SNAT and One To One)
    2. prerouting (DNAT)"""
    ruleset = execute_command_without_arguments(["sudo", "nft", "-a", "list", "table", "nat"])
    list_postrouting_from_system = utils.find_nat_in_ruleset(ruleset.stdout, "postrouting")
    list_prerouting_from_system = utils.find_nat_in_ruleset(ruleset.stdout, "prerouting")
    return list_postrouting_from_system, list_prerouting_from_system


def save_ruleset_nft():
    """Save all ruleset in ruleset.nft file. This backup makes it easy to restore the configuration after a system reboot"""
    current_dir = get_current_directory()
    ruleset_process = execute_command_without_arguments(["sudo", "nft", "list", "table", "nat"])
    write_file_from_system(PATH_RULESET_NFT.format(current_dir), ruleset_process.stdout)


def delete_nat_rule_in_system(chain, handle_number):
    execute_command_without_arguments(["sudo", "nft", "delete", "rule", "nat", chain, "handle", f"{handle_number}"])


def delete_all_nat_rule_from_system():
    """Getting all nat rule from system and deleting it all"""
    list_postrouting_from_system, list_prerouting_from_system = get_list_nat_rules_from_system()
    for rule_index in range(len(list_postrouting_from_system)):
        handle_number = utils.get_rule_handle_with_position(list_postrouting_from_system, rule_index)
        delete_nat_rule_in_system("postrouting", handle_number)
    for rule_index in range(len(list_prerouting_from_system)):
        handle_number = utils.get_rule_handle_with_position(list_prerouting_from_system, rule_index)
        delete_nat_rule_in_system("prerouting", handle_number)


def get_rule_handle_in_system(nat_type="postrouting", rule_position=0):
    """Return the last rule handle from ruleset"""
    rule_set = execute_command_without_arguments(["sudo", "nft", "-a", "list", "table", "nat"])

    list_nat_rules = utils.find_nat_in_ruleset(rule_set.stdout, nat_type)
    handle_number = utils.get_rule_handle_with_position(list_nat_rules, rule_position)
    return handle_number


def get_rule_content_in_system(nat_type="postrouting", rule_position=0):
    """Return the last rule handle from ruleset"""
    rule_set = execute_command_without_arguments(["sudo", "nft", "-a", "list", "table", "nat"])

    list_nat_rules = utils.find_nat_in_ruleset(rule_set.stdout, nat_type)
    handle_number = utils.get_rule_content_with_position(list_nat_rules, rule_position)
    return handle_number


def exist_change_rule_position_in_system(type_nat, rule_nat, new_position)->int:
    """Function that get a rule NAT and it's new position and 
    check if there is a changes will be affected on system.
    The function return the next rule_number wich will be used in changing position on system.
    If there is no changes than the function will return False."""
    if rule_nat.rule_status:
        next_rule = get_next_active_rule(type_nat, rule_nat.db_position, new_position)
        if next_rule:
            return next_rule.rule_number
        return -1
    return False


def get_next_active_rule(type_nat, old_position, new_position):
    """Function that retrieves the NAT rule and its new position and finds the next active rule by position.
    If there are no active rules below this rule after the position change, then the function will return False"""
    # Get the list of next rules below the changed rule
    # If the rule is changed to down than the list must start from the rule with position grather than the new position
    if old_position < new_position:
        list_next_rule = type_nat.objects.filter(rule_status=True, db_position__gt=new_position)
    # If the rule is changed to up than the list must start from the rule with position grather or equal than the new position
    else:
        list_next_rule = type_nat.objects.filter(rule_status=True, db_position__gte=new_position)
    if len(list_next_rule) > 0:
        return list_next_rule.order_by("db_position").first()
    return False
