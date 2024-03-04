from backend.nat.utils import get_rule_handle_in_system
from backend.nat.utils_system import delete_nat_rule_in_system, save_ruleset_nft
from utils.commands_utils import execute_command_without_arguments


def create_snat_rule_in_system(oifname, source, destination, protocol, outgoing_ip_address):
    """Create an SNAT rule in system"""
    # Set the basics of rule command
    command_snat = ["sudo", "nft", "add", "rule", "nat", "postrouting", "oifname", oifname]

    # Set the address and port for source and destination if the user don't choose Any
    ip_addr_source = []
    tcp_source = []
    ip_addr_destination = []
    tcp_destination = []
    ip_protocol = []
    if source != "any":
        ip_addr_source = ["ip", "saddr", source["address"]]
        tcp_source = ["tcp", "sport", source["port"]]
    if destination != "any":
        ip_addr_destination = ["ip", "daddr", destination["address"]]
        tcp_destination = ["tcp", "dport", destination["port"]]
    if protocol != "":
        ip_protocol = ["ip", "protocol", protocol]

    # Complete the SNAT rule command
    added_fields_rule = [ip_addr_source, ip_addr_destination, tcp_source,tcp_destination, ip_protocol, outgoing_ip_address]
    for command in added_fields_rule:
        command_snat.extend(command)

    # Create the SNAT rule in system
    execute_command_without_arguments(command_snat)

    # Save ruleset in ruleset file
    save_ruleset_nft()

    # Get the rule handle
    handle_number = get_rule_handle_in_system()
    return handle_number


def delete_snat_rule_in_system(handle_number):
    """Update an SNAT rule in system"""
    delete_nat_rule_in_system("postrouting", handle_number)

    # Save ruleset in ruleset file
    save_ruleset_nft()


def update_snat_rule_in_system(oifname, source, destination, protocol, outgoing_ip_address, handle_number):
    """Update an SNAT rule in system"""
    delete_nat_rule_in_system("postrouting", handle_number)
    new_handle_number = create_snat_rule_in_system(oifname, source, destination, protocol, outgoing_ip_address)

    # Save ruleset in ruleset file
    save_ruleset_nft()
    return new_handle_number
