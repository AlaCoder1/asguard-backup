from backend.nat.contant_variables import PATH_RULESET_NFT
from backend.nat import utils
from utils.commands_utils import execute_command_without_arguments, get_current_directory, write_file_from_system
from utils.errors_utils import CommandExecutionError


def get_list_nat_rules_from_system():
    """Get list of nat rules from system: 
    1. postrouting (SNAT and One To One)
    2. prerouting (DNAT)"""
    list_postrouting_from_system = extract_list_rule_nat_from_system()
    list_prerouting_from_system = extract_list_rule_nat_from_system("prerouting")
    return list_postrouting_from_system, list_prerouting_from_system


def save_ruleset_nft():
    """Save all ruleset in ruleset.nft file. This backup makes it easy to restore the configuration after a system reboot"""
    current_dir = get_current_directory()
    ruleset_process = execute_command_without_arguments(["sudo", "nft", "list", "table", "nat"])
    write_file_from_system(PATH_RULESET_NFT.format(current_dir), ruleset_process.stdout)


def add_nat_rule_in_system(command_line):
    """Execute the command-line to create the rule nat and save it in ruleset nft file"""
    # Execute the NAT rule in system
    execute_command_without_arguments(command_line)

    # Save ruleset in ruleset file
    save_ruleset_nft()


def delete_nat_rule_in_system(chain, handle_number):
    """Execute the command-line to delete the rule nat and save it in ruleset nft file"""
    execute_command_without_arguments(
        ["sudo", "nft", "delete", "rule", "nat", chain, "handle", f"{handle_number}"])

    # Save ruleset in ruleset file
    save_ruleset_nft()


def delete_all_nat_rule_from_system():
    """Getting all nat rule from system and deleting it all"""
    list_postrouting_from_system, list_prerouting_from_system = get_list_nat_rules_from_system()
    for postrouting_rule in list_postrouting_from_system:
        handle_number, _ = utils.get_rule_handle_position_with_content(postrouting_rule, list_postrouting_from_system)
        delete_nat_rule_in_system("postrouting", handle_number)
    for prerouting_rule in list_prerouting_from_system:
        handle_number, _ = utils.get_rule_handle_position_with_content(prerouting_rule, list_prerouting_from_system)
        delete_nat_rule_in_system("prerouting", handle_number)


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


def extract_list_rule_nat_from_system(chain="postrouting"):
    """Extract from nft the list of nat rules (postrouting or prerouting)"""
    rule_set = execute_command_without_arguments(["sudo", "nft", "-a", "list", "table", "nat"])
    list_rules = [line.strip() for line in rule_set.stdout.splitlines()]
    for line_index in range(len(list_rules)):
        if list_rules[line_index].startswith(f"chain {chain}"):
            start_snat_line = line_index + 2
            break
    for line_snat in range(start_snat_line, len(list_rules)):
        if list_rules[line_snat].startswith("}"):
            end_snat_line = line_snat
            break
    return list_rules[start_snat_line:end_snat_line]


def get_added_nat_rule(previous_list_rule: list[str], new_list_rule: list[str]):
    """Identifies and returns the newly added rule from the updated list of SNAT postrouting rules."""
    # Raise an error if no rule was added or if more than one rule was added
    if len(new_list_rule) - len(previous_list_rule) != 1:
        raise CommandExecutionError(message="Expected exactly one new rule, but found none or multiple")
    
    # Loop until founding the new rule
    for rule in new_list_rule:
        if rule not in previous_list_rule:
            rule_content, rule_handle = rule.split(" # handle ", 1)
            return rule_content, rule_handle
    
    # Raise an error if synchronization with system NAT rules failed
    raise CommandExecutionError(message="No matching added rule found in system NAT rules")
