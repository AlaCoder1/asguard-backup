from backend.nat.models import SNat
from backend.nat.utils_snat import input_create_snat
from backend.nat.utils_system import add_nat_rule_in_system, delete_nat_rule_in_system, exist_change_rule_position_in_system, extract_list_rule_nat_from_system, get_added_nat_rule


def create_snat_rule_in_system(oifname, source, destination, protocol, masking, next_rule_handle=0):
    """Create an SNAT rule in system and return the rule handle and content"""
    # Get the list of existing postrouting rules before adding the new one
    previous_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Build the SNAT rule command
    command_snat = build_command_create_snat(
        oifname, source, destination, protocol, masking, next_rule_handle)
    # Create the SNAT rule in system
    add_nat_rule_in_system(command_snat)

    # Get the list of existing postrouting rules after adding the new one
    new_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Get the rule handle and content
    rule_content, handle_number = get_added_nat_rule(
        previous_list_postrouting_rules, new_list_postrouting_rules)
    return handle_number, rule_content


def delete_snat_rule_in_system(handle_number):
    """Delete an SNAT rule in system"""
    delete_nat_rule_in_system("postrouting", handle_number)


def update_snat_rule_in_system(oifname, source, destination, protocol, masking, handle_number, 
                               next_rule_handle):
    """Update an SNAT rule in system and return the new rule handle and content"""
    # Delete the SNAT rule in system with previous params
    delete_nat_rule_in_system("postrouting", handle_number)
    
    # Get the list of existing postrouting rules after deleting the SNAT rule
    previous_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Build the SNAT rule command
    command_snat = build_command_create_snat(
        oifname, source, destination, protocol, masking, next_rule_handle)

    # Create the SNAT rule in system with new params
    add_nat_rule_in_system(command_snat)

    # Get the list of existing postrouting rules after adding the SNAT rule in system with new params
    new_list_postrouting_rules =  extract_list_rule_nat_from_system()

    # Get the rule handle and content
    new_rule_content, new_handle_number = get_added_nat_rule(
        previous_list_postrouting_rules, new_list_postrouting_rules)
    
    return new_handle_number, new_rule_content


def change_rule_snat_position_in_system(snat: SNat, new_positon: int):
    """Change an SNAT rule position in system"""
    next_rule_number = exist_change_rule_position_in_system(SNat, snat, new_positon)
    if next_rule_number:
        delete_snat_rule_in_system(snat.rule_number)
        source, destination, masking = input_create_snat(
                snat.source_address, snat.source_port, 
                snat.destination_address, snat.destination_port,
                snat.snat_type, snat.translation_address_from, snat.translation_address_to, 
                snat.translation_port)
        create_snat_rule_in_system(snat.interface.ifname, source, destination, snat.protocol, masking,
                                   next_rule_number)


def build_command_create_snat(oifname, source, destination, protocol, masking, next_rule_handle):
    """Builds the command-line string used to create an SNAT rule."""
    # Set the basics of rule command
    # Command to create a rule in first position
    command_snat = ["sudo", "nft", "insert", "rule", "nat", "postrouting"]
    # Update the command to insert the rule in a specific position
    if next_rule_handle > 0:
        command_snat.insert(6, "position")
        command_snat.insert(7, f"{next_rule_handle}")
    # Update the command to insert the rule in last position
    elif next_rule_handle < 0:
        command_snat[2] = "add"
    
    # Set the address and port for source and destination if the user don't choose Any
    oifname_command = []
    ip_addr_source = []
    tcp_source = []
    ip_addr_destination = []
    tcp_destination = []
    ip_protocol = []
    if oifname:
        oifname_command = ["oifname", oifname]
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
    added_fields_rule = [oifname_command, ip_addr_source, ip_addr_destination, tcp_source,
                         tcp_destination, ip_protocol, masking]
    for command in added_fields_rule:
        command_snat.extend(command)
    
    return command_snat
