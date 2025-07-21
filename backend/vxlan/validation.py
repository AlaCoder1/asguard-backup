import re
from django.utils.translation import gettext_lazy as _
import ipaddress
from django.db.models import Q
from backend.gateway.models import Gateway
from backend.network.models import Interface
VXLAN_MIN = 1
VXLAN_MAX = 16777215
DEFAULT_VXLAN = 1

class InvalidVXLANTagError(Exception):
    """Exception raised when the VXLAN tag is invalid."""
    pass

def validate_vxlan_tag(vlan_id):
    """
    Validate if the provided VXLAN ID is within the valid range.
    """
    if not isinstance(vlan_id, int):
        raise InvalidVXLANTagError(_("VXLAN ID must be an integer."))
    if vlan_id < VXLAN_MIN or vlan_id > VXLAN_MAX:
        raise InvalidVXLANTagError(_("VXLAN ID must be between ")+ f"{VXLAN_MIN} - {VXLAN_MAX}." )
    return True

