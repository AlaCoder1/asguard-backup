from backend.nat.models import OneToOneNat
from backend.nat.utils import input_create_one_to_one_nat
from backend.nat.utils_system import exist_change_rule_position_in_system, get_rule_content_in_system, get_rule_handle_in_system
from backend.nat.utils_system import delete_nat_rule_in_system, save_ruleset_nft
from utils.commands_utils import execute_command_without_arguments


def create_one_to_one_nat_rule_in_system(oifname, source, destination, translation, next_rule_handle=0, rule_position=0):
    """Create an SNAT rule in system and return the rule handle and content"""
    # Set the basics of rule command
    command_one_to_one_nat = ["sudo", "nft", "insert", "rule", "nat", "postrouting", "oifname", oifname, "ip", "saddr", source]
    # Update the command to insert the rule in a specific position
    if next_rule_handle > 0:
        command_one_to_one_nat.insert(6, "position")
        command_one_to_one_nat.insert(7, f"{next_rule_handle}")
    # Update the command to insert the rule in last position
    elif next_rule_handle < 0:
        command_one_to_one_nat[2] = "add"

    # Set the address and port for source and destination if the user don't choose Any
    ip_addr_destination = []
    if destination != "any":
        ip_addr_destination = ["ip", "daddr", destination]

    # Complete the SNAT rule command
    added_fields_rule = [ip_addr_destination, ["snat", "ip", "to", translation]]
    for command in added_fields_rule:
        command_one_to_one_nat.extend(command)

    # Create the SNAT rule in system
    execute_command_without_arguments(command_one_to_one_nat)

    # Save ruleset in ruleset file
    save_ruleset_nft()

    # Get the rule handle
    handle_number = get_rule_handle_in_system("postrouting", rule_position)
    rule_content = get_rule_content_in_system("postrouting", rule_position)
    return handle_number, rule_content


def delete_one_to_one_nat_rule_in_system(handle_number):
    """Delete an SNAT rule in system"""
    delete_nat_rule_in_system("postrouting", handle_number)

    # Save ruleset in ruleset file
    save_ruleset_nft()


def update_one_to_one_nat_rule_in_system(oifname, source, destination, outgoing_ip_address, handle_number, 
                                         next_rule_handle, rule_position):
    """Update an SNAT rule in system and return the new rule handle and content"""
    delete_nat_rule_in_system("postrouting", handle_number)
    new_handle_number, new_content_number = create_one_to_one_nat_rule_in_system(
        oifname, source, destination, outgoing_ip_address, next_rule_handle, rule_position)

    # Save ruleset in ruleset file
    save_ruleset_nft()
    return new_handle_number, new_content_number


def change_rule_one_to_one_nat_position_in_system(one_to_one_nat: OneToOneNat, new_positon: int):
    """Change an SNAT rule position in system"""
    next_rule_number = exist_change_rule_position_in_system(OneToOneNat, one_to_one_nat, new_positon)
    if next_rule_number:
        delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
        destination = input_create_one_to_one_nat(one_to_one_nat.destination_address)
        create_one_to_one_nat_rule_in_system(
            one_to_one_nat.interface.ifname, one_to_one_nat.source_address, destination, 
            one_to_one_nat.translation_address, 
            next_rule_number, new_positon)
