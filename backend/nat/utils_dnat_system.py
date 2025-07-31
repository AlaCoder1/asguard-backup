from backend.nat.models import DNat
from backend.nat.utils_dnat import input_create_dnat
from backend.nat.utils_system import add_nat_rule_in_system, delete_nat_rule_in_system, exist_change_rule_position_in_system, extract_list_rule_nat_from_system, get_added_nat_rule
from utils.errors_utils import CommandExecutionError


def create_dnat_rule_in_system(iifname, source, destination, protocol, next_rule_handle=0):
    """Create an DNAT rule in system and return the rule handle and content"""

    # Build the DNAT rule command
    command_dnat = build_command_create_dnat(
        iifname, source, destination, protocol, next_rule_handle)

    # Create the DNAT rule in system
    rule_content, handle_number = add_nat_rule_in_system(command_dnat, "prerouting")
    return handle_number, rule_content


def delete_dnat_rule_in_system(handle_number):
    """Delete an DNAT rule in system"""
    delete_nat_rule_in_system("prerouting", handle_number)


def update_dnat_rule_in_system(iifname, source, destination, protocol, handle_number, next_rule_handle):
    """Update an DNAT rule in system and return the new rule handle and content"""
    # Delete the DNAT rule in system with previous params
    try:
        delete_nat_rule_in_system("prerouting", handle_number)
    except CommandExecutionError:
        pass

    # Build the DNAT rule command
    command_dnat = build_command_create_dnat(
        iifname, source, destination, protocol, next_rule_handle)

    # Create the DNAT rule in system with new params
    new_rule_content, new_handle_number = add_nat_rule_in_system(command_dnat, "prerouting")
    return new_handle_number, new_rule_content


def change_rule_dnat_position_in_system(dnat: DNat, new_positon: int):
    """Change a DNAT rule position in system"""
    next_rule_number = exist_change_rule_position_in_system(DNat, dnat, new_positon)
    if next_rule_number:
        delete_dnat_rule_in_system(dnat.rule_number)
        source, destination = input_create_dnat(
            dnat.source_address, dnat.source_protocol, dnat.source_port, dnat.source_port_from, dnat.source_port_to,
            dnat.external_address, dnat.internal_address, dnat.destination_protocol,
            dnat.destination_port_forwarding, dnat.destination_port_from, dnat.destination_port_to, dnat.destination_port)
        create_dnat_rule_in_system(dnat.interface.ifname, source, destination, dnat.protocol,
                                   next_rule_number)


def build_command_create_dnat(iifname, source, destination, protocol, next_rule_handle):
    """Builds the command-line string used to create an DNAT rule."""
    # Set the basics of rule command
    command_dnat = ["sudo", "nft", "insert", "rule", "nat", "prerouting"]
    # Update the command to insert the rule in a specific position
    if next_rule_handle > 0:
        command_dnat.insert(6, "position")
        command_dnat.insert(7, f"{next_rule_handle}")
    # Update the command to insert the rule in last position
    elif next_rule_handle < 0:
        command_dnat[2] = "add"

    # Set the address and port for source and destination if the user don't choose Any
    iifname_command = []
    ip_addr_source = []
    tcp_source = []
    ip_addr_destination = []
    tcp_destination = []
    ip_protocol = []
    forwarding_port = []
    outgoing_ip_address = []
    if iifname:
        iifname_command = ["oifname", iifname]
    if source["address"]:
        ip_addr_source = ["ip", "saddr", source["address"]]
    if source['protocol'] and source['port']:
        tcp_source = [source["source_protocol"], "sport", source["port"]]
    if destination["external_address"] != "":
        ip_addr_destination = ["ip", "daddr", destination["external_address"]]
    if destination["port_forwarding"]:
        tcp_destination = [destination["protocol"], "dport", destination["port_forwarding"]]
    if destination["port"]:
        forwarding_port = [destination["port"]]
    if protocol != "":
        ip_protocol = ["ip", "protocol", protocol]
    if destination["internal_address"] != "":
        outgoing_ip_address = ["dnat", "ip", "to", destination["internal_address"]]

    # Complete the DNAT rule command
    added_fields_rule = [iifname_command, ip_addr_source, ip_addr_destination, 
                         tcp_source, tcp_destination, ip_protocol,
                         outgoing_ip_address, forwarding_port]
    for command in added_fields_rule:
        command_dnat.extend(command)
    return command_dnat
