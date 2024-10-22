from backend.nat.contant_variables import PATH_RULESET_NFT
from utils.commands_utils import execute_command_without_arguments, get_current_directory, write_file_from_system


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
