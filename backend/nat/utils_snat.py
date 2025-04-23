from utils.utils_address import is_valid_ipv4_with_mask, is_valid_ipv4_without_mask


def input_create_snat(source_address, source_port, destination_address, destination_port, snat_type,
                      translation_address_from=None, translation_address_to=None, translation_port=None):
    """Return the input of an SNAT rule: source, destination and masking"""
    source = {"address": source_address,
              "port": source_port}
    destination = {"address": destination_address,
                   "port": destination_port}
    masking = ["masquerade"]
    if snat_type == "Static":
        masking = translation_address_from
        if translation_address_to != "":
            masking += f"""-{translation_address_to}"""
        if translation_port != "":
            masking += f""":{translation_port}"""
        masking = ["snat", "ip", "to",  masking]

    return source, destination, masking


def check_payload(data: dict):
    """Check the payload fileds"""
    # Check the validity of the ipv4 addresses
    list_ipv4_address = [data["source_address"], data["destination_address"]]
    for ipv4_address in list_ipv4_address:
        if not is_valid_ipv4_with_mask(ipv4_address):
            return False
    # Check the validity of the ipv4 addresses in static mode
    if data["snat_type"] == "Static":
        list_ipv4_address = [data["translation_address_from"], data["translation_address_to"]]
        for ipv4_address in list_ipv4_address:
            if not is_valid_ipv4_without_mask(ipv4_address):
                return False
    # Check if the source and destination addresses are differents
    if len({data["source_address"], data["destination_address"]}) != 2:
        return False
    # Check if the translation addresses from and to are differents in static mode
    if data["snat_type"] == "Static":
        if len({data["translation_address_from"], data["translation_address_to"]}) != 2:
            return False
    return True
