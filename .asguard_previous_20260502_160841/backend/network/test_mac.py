import re

def validate_mac_address(mac: str) -> bool:
    """
    Validate the MAC address against common constraints.
    
    Constraints:
    - Must follow the pattern XX:XX:XX:XX:XX:XX where X is a hexadecimal digit.
    - Must not be all zeros.
    - Must be a unicast address (first octet's least-significant bit must be 0).
    """
    # Check format using a regular expression
    pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
    if not re.match(pattern, mac):
        print("MAC address format is invalid.")
        return False

    # Avoid all zeros MAC address if not allowed
    if mac.lower() == "00:00:00:00:00:00":
        print("MAC address cannot be all zeros.")
        return False

    # Convert the first octet to an integer and check if it's a unicast address.
    first_octet = int(mac.split(':')[0], 16)
    if (first_octet & 1):
        print("MAC address is a multicast address; it must be unicast.")
        return False

    # All checks passed
    return True

# Example usage:
mac_address = "00:00:00:00:00:01"  # Replace with the desired MAC address

if validate_mac_address(mac_address):
    print(f"The MAC address {mac_address} is valid and can be used.")
else:
    print(f"The MAC address {mac_address} is invalid. Please use a correct format and valid address.")
