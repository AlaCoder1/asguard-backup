import re
from django.utils.translation import gettext_lazy as _
import ipaddress
from django.db.models import Q
from backend.gateway.models import Gateway
from backend.network.models import Interface
VLAN_MIN = 1
VLAN_MAX = 4094
DEFAULT_VLAN = 1

class InvalidVLANTagError(Exception):
    """Exception raised when the VLAN tag is invalid."""
    pass

class InvalidVLANPriorityError(Exception):
    """Exception raised when the VLAN priority is invalid."""
    pass
class InvalidParentInterError(Exception):
    """Exception raised when the VLAN priority is invalid."""
    pass
def validate_id_interface(id):
    """Validate  interface exist or not """
    print(Interface.objects.filter(id=id))
    if not Interface.objects.filter(id=id).exclude(Q(name_interface__startswith='VLAN') | Q(name_interface__startswith='VXLAN')).exists() :
        raise InvalidParentInterError(_("Parent Interface does not exist!"))
    return True  
def validate_vlan_tag(vlan_id):
    """
    Validate if the provided VLAN ID is within the valid range.
    """
    if not isinstance(vlan_id, int):
        raise InvalidVLANTagError(_("VLAN ID must be an integer."))
    if vlan_id < VLAN_MIN or vlan_id > VLAN_MAX:
        raise InvalidVLANTagError(_("VLAN ID must be between ")+ f"{VLAN_MIN} - {VLAN_MAX}." )
    return True

def validate_vlan_priority(vlan_priority):
    """
    Validate the priority in a VLAN tag (PCP). 
    """
    allowed_values =["Best Effort ( 0 , default )",
                      'Background ( 1, lowest)',
                      'Excellent Effort (2)',
                      'Critical Applications (3)',
                      'Video (4)',
                      'Voice (5)',
                      'Internetwork Control (6)',
                      'Network Control (7)'
                      
                      ]
    if vlan_priority is not None and vlan_priority not in allowed_values:
        raise InvalidVLANPriorityError(
            _("Invalid VLAN priority. Allowed values are: ")+", ".join(allowed_values)
        )
    return True  
    
