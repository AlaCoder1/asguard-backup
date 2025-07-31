from utils.utils_address import is_valid_ipv4_with_mask, is_valid_ipv4_without_mask


def input_create_dnat(
        source_address, source_protocol, source_port, source_port_from, source_port_to, external_address, internal_address, 
        destination_protocol, destination_port_forwarding, destination_port_from, destination_port_to, destination_port):
    """Create the input of a DNAT rule: Source and Destination"""
    ### Source ###
    # Source address
    source = {"address": None,
              "protocol": None,
              "port": None,
              }
    if source_address != "":
        source = {"address": source_address}
    # Source port
    if source_protocol:
        # A unique port
        source["source_protocol"] = source_protocol
        if source_port:
            source["port"] = source_port
        # A range port
        elif source_port_from:
            source["source_protocol"] = source_protocol
            source["port"] = source_port_from
            if source_port_to:
                source["port"] += f"""-{source_port_to}"""

    ### Destination ###
    destination = {"external_address": external_address,
                   "internal_address": internal_address,
                   "port_forwarding": None,
                   "port": None,
                   "protocol": None}
    if destination_port_forwarding:
        destination["port_forwarding"] = destination_port_forwarding
        destination["protocol"] = destination_protocol
    elif destination_port_from:
        destination["port_forwarding"] = destination_port_from
        destination["protocol"] = destination_protocol
        if destination_port_to:
            destination["port_forwarding"] = f'{destination_port_from}-{destination_port_to}'
        if destination_port:
            destination["port"] = f' : {destination_port}'

    return source, destination


def check_payload(data: dict):
    """Check the payload fileds"""
    # Check the validity of the protocols for source and destintion
    try:
        if (data["protocol"] != "") and (data["protocol"] not in ["tcp", "udp"]):
            return False
    except KeyError:
        pass
    try:
        if (data["destination_protocol"] != "") and (data["destination_protocol"] not in ["tcp", "udp"]):
            return False
    except KeyError:
        pass
    # Check the validity of the ipv4 addresses
    list_ipv4_address = [data["source_address"]]
    for ipv4_address in list_ipv4_address:
        if not is_valid_ipv4_with_mask(ipv4_address):
            return False
    # Check the validity of the ipv4 addresses
    list_ipv4_address = [data["external_address"], data["internal_address"]]
    for ipv4_address in list_ipv4_address:
        if not is_valid_ipv4_without_mask(ipv4_address):
            return False
    # Check if the source, external and internal addresses are differents
    # Remove the empty addresses
    list_address = [data["source_address"], data["external_address"], data["internal_address"]]
    list_address_valid = [address for address in list_address if address != ""]
    if len ([item for item in list_address_valid if list_address_valid.count(item) == 1]) < len(list_address_valid):
        return False
    return True
