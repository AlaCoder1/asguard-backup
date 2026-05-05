from utils.utils_address import is_valid_ipv4_with_mask


def input_create_one_to_one_nat(destination_address: str):
    """Return the input of an OneToOneNAT rule: destination"""
    if destination_address != "":
        return destination_address
    return "any"


def check_payload(data: dict):
    """Check the payload fileds"""
    # Check the validity of the ipv4 addresses
    list_ipv4_address = [data["source_address"], data["destination_address"], data["translation_address"]]
    for ipv4_address in list_ipv4_address:
        if not is_valid_ipv4_with_mask(ipv4_address):
            return False
    # Check if the three addresses are differents
    if len({data["source_address"], data["destination_address"], data["translation_address"]}) != 3:
        return False
    return True
