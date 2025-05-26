from backend.nat.models import DNat
from utils.utils_address import is_valid_ipv4_with_mask, is_valid_ipv4_without_mask


def input_create_dnat(dnat: DNat):
    source = "any"
    if dnat.source_address != "":
        source = {"address": dnat.source_address,
                    "port": dnat.source_port_from}
        if dnat.source_port_to != "":
            source["port"] += f"""-{dnat.source_port_to}"""

    destination = {"external_address": dnat.external_address,
                    "internal_address": dnat.internal_address}

    if dnat.destination_port_from:
        destination["port_forwarding"] = f'{dnat.destination_port_from}-{dnat.destination_port_to}'
        destination["port"] = f' : {dnat.destination_port}'
    else:
        destination["port_forwarding"] = False

    return source, destination


def check_payload(data: dict):
    """Check the payload fileds"""
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
    if (data["source_address"] != "" or data["external_address"] != "" or data["internal_address"] != "") and len({data["source_address"], data["external_address"], data["internal_address"]}) != 3:
        return False
    return True
