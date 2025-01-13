from backend.nat.utils_system import get_rule_content_in_system
from backend.nat.utils_system import delete_nat_rule_in_system, get_rule_handle_in_system, save_ruleset_nft
from utils.commands_utils import execute_command_without_arguments


def create_snat_rule_in_system(oifname, source, destination, protocol, masking, next_rule_handle=0, 
                               rule_position=0):
    """Create an SNAT rule in system and return the rule handle and content"""
    # Set the basics of rule command
    # Command to create a rule in first position
    command_snat = ["sudo", "nft", "insert", "rule", "nat", "postrouting", "oifname", oifname]
    # Update the command to insert the rule in a specific position
    if next_rule_handle > 0:
        command_snat.insert(6, "position")
        command_snat.insert(7, f"{next_rule_handle}")
    # Update the command to insert the rule in last position
    elif next_rule_handle < 0:
        command_snat[2] = "add"
    
    # Set the address and port for source and destination if the user don't choose Any
    ip_addr_source = []
    tcp_source = []
    ip_addr_destination = []
    tcp_destination = []
    ip_protocol = []
    if source["address"] != "":
        ip_addr_source = ["ip", "saddr", source["address"]]
        if source["port"] != "":
            tcp_source = ["tcp", "sport", source["port"]]
    if destination["address"] != "":
        ip_addr_destination = ["ip", "daddr", destination["address"]]
        if destination["port"] != "":
            tcp_destination = ["tcp", "dport", destination["port"]]
    if protocol != "":
        ip_protocol = ["ip", "protocol", protocol]

    # Complete the SNAT rule command
    added_fields_rule = [ip_addr_source, ip_addr_destination, tcp_source,tcp_destination, ip_protocol, 
                         masking]
    for command in added_fields_rule:
        command_snat.extend(command)

    # Create the SNAT rule in system
    execute_command_without_arguments(command_snat)

    # Save ruleset in ruleset file
    save_ruleset_nft()

    # Get the rule handle
    handle_number = get_rule_handle_in_system("postrouting", rule_position)
    rule_content = get_rule_content_in_system("postrouting", rule_position)
    return handle_number, rule_content


def delete_snat_rule_in_system(handle_number):
    """Delete an SNAT rule in system"""
    execute_command_without_arguments(
        ["sudo", "nft", "delete", "rule", "nat", "postrouting", "handle", f"{handle_number}"])

    # Save ruleset in ruleset file
    save_ruleset_nft()


def update_snat_rule_in_system(oifname, source, destination, protocol, masking, handle_number, 
                               next_rule_handle, rule_position):
    """Update an SNAT rule in system and return the new rule handle and content"""
    delete_nat_rule_in_system("postrouting", handle_number)
    new_handle_number, new_content_number = create_snat_rule_in_system(
        oifname, source, destination, protocol, masking, next_rule_handle, rule_position)

    # Save ruleset in ruleset file
    save_ruleset_nft()
    return new_handle_number, new_content_number
