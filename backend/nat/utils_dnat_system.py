from backend.nat.utils_system import get_rule_content_in_system, get_rule_handle_in_system
from backend.nat.utils_system import delete_nat_rule_in_system, save_ruleset_nft
from utils.commands_utils import execute_command_without_arguments


def create_dnat_rule_in_system(iifname, source, destination, protocol, next_rule_handle=0, rule_position=0):
    """Create an DNAT rule in system"""
    # Set the basics of rule command
    command_dnat = ["sudo", "nft", "insert", "rule", "nat", "prerouting", "iifname", iifname]
    # Update the command to insert the rule in a specific position
    if next_rule_handle > 0:
        command_dnat.insert(6, "position")
        command_dnat.insert(7, f"{next_rule_handle}")
    # Update the command to insert the rule in last position
    elif next_rule_handle < 0:
        command_dnat[2] = "add"

    # Set the address and port for source and destination if the user don't choose Any
    ip_addr_source = []
    tcp_source = []
    ip_addr_destination = []
    tcp_destination = []
    ip_protocol = []
    forwarding_port = []
    if source != "any":
        ip_addr_source = ["ip", "saddr", source["address"]]
        if source['port']:
            tcp_source = ["tcp", "sport", source["port"]]
    ip_addr_destination = ["ip", "daddr", destination["external_address"]]
    if destination["port_forwarding"]:
        tcp_destination = ["tcp", "dport", destination["port_forwarding"]]
        forwarding_port = [destination["port"]]
    if protocol != "":
        ip_protocol = ["ip", "protocol", protocol]
    outgoing_ip_address = ["dnat", "ip", "to", destination["internal_address"]]

    # Complete the DNAT rule command
    added_fields_rule = [ip_addr_source, ip_addr_destination, tcp_source,tcp_destination, ip_protocol,
                         outgoing_ip_address, forwarding_port]
    for command in added_fields_rule:
        command_dnat.extend(command)

    # Create the DNAT rule in system
    execute_command_without_arguments(command_dnat)

    # Save ruleset in ruleset file
    save_ruleset_nft()

    # Get the rule handle
    handle_number = get_rule_handle_in_system("prerouting", rule_position)
    rule_content = get_rule_content_in_system("prerouting", rule_position)
    return handle_number, rule_content


def delete_dnat_rule_in_system(handle_number):
    """Update an DNAT rule in system"""
    delete_nat_rule_in_system("prerouting", handle_number)

    # Save ruleset in ruleset file
    save_ruleset_nft()


def update_dnat_rule_in_system(iifname, source, destination, protocol, handle_number, next_rule_handle, 
                               rule_position):
    """Update an DNAT rule in system"""
    delete_nat_rule_in_system("prerouting", handle_number)
    new_handle_number, new_rule_content = create_dnat_rule_in_system(
        iifname, source, destination, protocol, next_rule_handle, rule_position)

    # Save ruleset in ruleset file
    save_ruleset_nft()
    return new_handle_number, new_rule_content
