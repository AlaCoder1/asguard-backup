from backend.nat.contant_variables import PATH_RULESET_NFT
from backend.nat import utils
from utils.commands_utils import execute_command_without_arguments, get_current_directory, write_file_from_system


def get_list_nat_rules_from_system():
    """Get list of nat rules from system: 
    1. postrouting (SNAT and One To One)
    2. prerouting (DNAT)"""
    ruleset = execute_command_without_arguments(["sudo", "nft", "-a", "list", "table", "nat"])
    list_postrouting_from_system = find_nat_in_ruleset(ruleset.stdout, "postrouting")
    list_prerouting_from_system = find_nat_in_ruleset(ruleset.stdout, "prerouting")
    return list_postrouting_from_system, list_prerouting_from_system


def find_nat_in_ruleset(rule_set:str, chain="postrouting"):
    """Return list of NAT rules with it's type: SNAT, OneToOne or DNAT"""
    list_rules = [line.strip() for line in rule_set.splitlines()]
    for line_index in range(len(list_rules)):
        if list_rules[line_index].startswith(f"chain {chain}"):
            start_snat_line = line_index + 2
            break
    for line_snat in range(start_snat_line, len(list_rules)):
        if list_rules[line_snat].startswith("}"):
            end_snat_line = line_snat
            break
    return list_rules[start_snat_line:end_snat_line]


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
