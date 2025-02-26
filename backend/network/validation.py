import re
from django.utils.translation import gettext_lazy as _
import ipaddress
import socket

class InvalidIPAddressException(Exception):
    """Exception raised for invalid IP addresses."""
    def __init__(self, message=None):
        if message is None:
            message = _("Invalid IP address format")
        self.message = message
        super().__init__(self.message)
        
class InvalidNetmaskException(Exception):
    """Exception raised for invalid network mask formats."""
    def __init__(self, message=None):
        if message is None:
            message = _("Invalid network mask format")
        self.message = message
        super().__init__(self.message)

class InvalidMacAddressException(Exception):
    """Exception raised for invalid MAC addresses."""
    def __init__(self, message=_("Invalid MAC address format")):
        self.message = message
        super().__init__(self.message)
        
class InvalidSpeedDuplexException(Exception):
    """Exception raised for invalid speed/duplex configurations."""
    def __init__(self, message=None):
        if message is None:
            message = _("Invalid speed/duplex configuration")
        self.message = message
        super().__init__(self.message)
        
class InvalidSetupIV4Exception(Exception):
    """Exception raised for invalid setup ipv4  configurations."""
    def __init__(self, message=None):
        if message is None:
            message = _("Invalid setup ipv4 configuration")
        self.message = message
        super().__init__(self.message)
class InvalidBooleanxception(Exception):
    """Exception raised for invalid setup aux  configurations."""
    def __init__(self, message=None):
        if message is None:
            message = _("Invalid aux")
        self.message = message
        super().__init__(self.message)
        
class MTUException(Exception):
    """Custom exception to handle invalid MTU values."""
    pass
        
class MSSException(Exception):
    """Custom exception to handle invalid MSS values."""
    pass

    
class HostnameException(Exception):
    """Custom exception for invalid hostnames."""
    pass

class TimeoutException(Exception):
    """Custom exception for invalid timeout values."""
    pass


def validate_mac_address(mac_address):
    """Validate MAC address format (XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX)"""
    mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    if mac_address is not None and not re.match(mac_regex, mac_address):
        raise InvalidMacAddressException(_(f"Invalid MAC address: {mac_address} format like this XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX"))
    return True  

def validate_ip_address(ip):
    """Validate IPv4 and IPv6 addresses."""
    try:
        ipaddress.ip_address(ip)  
    except ValueError:
        raise InvalidIPAddressException(_(f"Invalid IP address: {ip} format like this x.x.x.x") )
    return True  

def validate_netmask(address,netmask):
    """
    Validate an IPv4 netmask in dotted-decimal notation (e.g., '255.255.255.0').
    Raises InvalidNetmaskException if the mask is invalid.
    """
    try:
        ipaddress.IPv4Network(f"{address}/{netmask}", strict=False)
        return True
    except ValueError:
       raise InvalidNetmaskException(
            _("Invalid network mask: '{mask}'").format(mask=netmask)
        )

   

        
def validate_speed_duplex(speed_duplex):
    allowed_values = ['100baseTx-FD', '100baseTx-HD', '10baseT-FD', '10baseT-HD']
    if speed_duplex is not None and speed_duplex not in allowed_values:
        raise InvalidSpeedDuplexException(
            _("Invalid speed/duplex configuration: '{value}'. Allowed values are: {allowed}").format(
                value=speed_duplex,
                allowed=", ".join(allowed_values)
            )
        )
    return True  

def validate_setup_ipv4(setup_ipv4):
    allowed_values = ['STATIC','DHCP','NONE']
    if setup_ipv4 is not None and setup_ipv4.upper() not in allowed_values:
        raise InvalidBooleanxception(
            _("Invalid setup ipv4 configuration: '{value}'. Allowed values are: {allowed}").format(
                value=setup_ipv4,
                allowed=", ".join(allowed_values)
            )
        )
    return True  
def validate_dhcp_ipv4(dhcp_ipv4):
    allowed_values = ['BASE','ADVANCED']
    if dhcp_ipv4 is None or dhcp_ipv4.upper() not in allowed_values:
        raise InvalidBooleanxception(
            _("Invalid dhcp ipv4 configuration: '{value}'. Allowed values are: {allowed}").format(
                value=dhcp_ipv4,
                allowed=", ".join(allowed_values)
            )
        )
    return True  

def validate_boolean(aux):
    if aux is not None and not isinstance(aux, bool):
        raise InvalidBooleanxception(
            _("Invalid boolean value: '{value}'").format(
                value=aux
            )
        )
    return True
def validate_mtu(mtu_value):
    """Set the MTU value for a network interface with basic constraints."""
    min_mtu = 576    
    max_mtu = 9000   
    if mtu_value is not None and (mtu_value < min_mtu or mtu_value > max_mtu):
        raise MTUException(f"MTU value of {mtu_value} is outside the allowed range ({min_mtu}-{max_mtu} bytes).")

    return True 
    

def validate_mss(mtu_value):
    """Calculate the MSS based on the MTU value."""
    if mtu_value is not None and mtu_value < 576:
        raise MSSException(f"MTU value of {mtu_value} is too small. Minimum MTU for MSS is 576 bytes.")

    return True

def validate_hostname(hostname):
    """
    Validates a generic hostname based on RFC 1035 and RFC 1123.
    """
    if hostname is not None and len(hostname) > 253:
        raise HostnameException(f"Hostname '{hostname}' exceeds the maximum length of 253 characters.")
    hostname_pattern = re.compile(
        r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*$'
    )

    if hostname is not None and not hostname_pattern.fullmatch(hostname):
        raise HostnameException(f"Hostname '{hostname}' is invalid. It must contain only letters, digits, or hyphens, and each label must start and end with a letter or digit.")
    return True

def validate_timeout(timeout):
    """
    Validates the timeout value in an API payload.
    """
    if timeout is not None and not isinstance(timeout, (int, float)):
        raise TimeoutException("Timeout must be a number (integer or float).")

    if timeout is not None and  not (1 <= timeout <= 300):
        raise TimeoutException(f"Timeout value {timeout} is out of range. It must be between 1 and 300 seconds.")

    return True