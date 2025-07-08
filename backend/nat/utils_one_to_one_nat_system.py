from backend.nat.models import OneToOneNat
from backend.nat.utils_one_to_one_nat import input_create_one_to_one_nat
from backend.nat.utils_system import add_nat_rule_in_system, delete_nat_rule_in_system, exist_change_rule_position_in_system, extract_list_rule_nat_from_system, get_added_nat_rule


def create_one_to_one_nat_rule_in_system(oifname, source, destination, translation, next_rule_handle=0):
    """Create an OneToOneNat rule in system and return the rule handle and content"""
    # Get the list of existing postrouting rules before adding the new one
    previous_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Build the OneToOneNat rule command
    command_one_to_one_nat = build_command_create_one_to_one_nat(
        oifname, source, destination, translation, next_rule_handle)

    # Create the OneToOneNat rule in system
    add_nat_rule_in_system(command_one_to_one_nat)

    # Get the list of existing postrouting rules after adding the new one
    new_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Get the rule handle and content
    rule_content, handle_number = get_added_nat_rule(
        previous_list_postrouting_rules, new_list_postrouting_rules)
    return handle_number, rule_content


def delete_one_to_one_nat_rule_in_system(handle_number):
    """Delete an OneToOneNat rule in system"""
    delete_nat_rule_in_system("postrouting", handle_number)


def update_one_to_one_nat_rule_in_system(oifname, source, destination, translation, handle_number, 
                                         next_rule_handle):
    """Update an OneToOneNat rule in system and return the new rule handle and content"""
    # Delete the OneToOneNat rule in system with previous params
    delete_nat_rule_in_system("postrouting", handle_number)
    
    # Get the list of existing postrouting rules after deleting the OneToOneNat rule
    previous_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Build the OneToOneNat rule command
    command_one_to_one_nat = build_command_create_one_to_one_nat(
        oifname, source, destination, translation, next_rule_handle)

    # Create the OneToOneNat rule in system with new params
    add_nat_rule_in_system(command_one_to_one_nat)

    # Get the list of existing postrouting rules after adding the OneToOneNat rule in system with new params
    new_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Get the rule handle and content
    new_content, new_handle_number = get_added_nat_rule(
        previous_list_postrouting_rules, new_list_postrouting_rules)
    return new_handle_number, new_content


def change_rule_one_to_one_nat_position_in_system(one_to_one_nat: OneToOneNat, new_positon: int):
    """Change an OneToOneNat rule position in system"""
    next_rule_number = exist_change_rule_position_in_system(OneToOneNat, one_to_one_nat, new_positon)
    if next_rule_number:
        delete_one_to_one_nat_rule_in_system(one_to_one_nat.rule_number)
        destination = input_create_one_to_one_nat(one_to_one_nat.destination_address)
        create_one_to_one_nat_rule_in_system(
            one_to_one_nat.interface.ifname, one_to_one_nat.source_address, destination, 
            one_to_one_nat.translation_address, next_rule_number)


def build_command_create_one_to_one_nat(oifname, source, destination, translation, next_rule_handle):
    """Builds the command-line string used to create a OneToOne NAT rule."""
    # Set the basics of rule command
    command_one_to_one_nat = ["sudo", "nft", "insert", "rule", "nat", "postrouting"]
    # Update the command to insert the rule in a specific position
    if next_rule_handle > 0:
        command_one_to_one_nat.insert(6, "position")
        command_one_to_one_nat.insert(7, f"{next_rule_handle}")
    # Update the command to insert the rule in last position
    elif next_rule_handle < 0:
        command_one_to_one_nat[2] = "add"

    # Set the address and port for source and destination if the user don't choose Any
    oifname_command = []
    ip_addr_destination = []
    if oifname:
        oifname_command = ["oifname", oifname]
    ip_addr_source = ["ip", "saddr", source]
    if destination != "any":
        ip_addr_destination = ["ip", "daddr", destination]
    ip_translation = ["snat", "ip", "to", translation]

    # Complete the OneToOneNat rule command
    added_fields_rule = [oifname_command, ip_addr_source, ip_addr_destination, ip_translation]
    for command in added_fields_rule:
        command_one_to_one_nat.extend(command)
    
    return command_one_to_one_nat
