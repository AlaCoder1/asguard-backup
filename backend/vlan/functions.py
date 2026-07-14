import subprocess
from backend.network.models import Interface
from backend.network.serializers import InterfaceSerializer
from django.utils.translation import gettext_lazy as _

from backend.vlan.validation import InvalidParentInterError, InvalidVLANPriorityError, InvalidVLANTagError, validate_id_interface, validate_vlan_priority, validate_vlan_tag


#Constants
CONSTANT_VLAN_CONFIG = _('Configuration VLAN')

#Success messages
SUCCESS_MESSAGES_SAVED = _("Saved")

def validate_input_date(data):
    """validate input data"""
    try:
        validate_id_interface(int(data["parent_interface"]))
        validate_vlan_tag(int(data["vlan_tag"]))
        validate_vlan_priority(data['vlan_priority'])
        
    except(InvalidVLANTagError,InvalidVLANPriorityError,InvalidParentInterError) as e:
        return str(e)
def execute_cmd(command):
    """function to excecute system commands"""
    command = "sudo " + command
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

def add_vlan_sys(parent_interface,vlan_tag,vlan_priority):
    """function to add vlan in system"""
    commands= [
    f"nmcli connection add type vlan con-name vlan{vlan_tag} ifname vlan{vlan_tag} dev {parent_interface} id {vlan_tag} ingress {vlan_priority}",
     f"nmcli connection modify vlan{vlan_tag} connection.autoconnect yes",
    "systemctl restart NetworkManager"
          ]
    for cmd in commands:
        _, error = execute_cmd(cmd)
        if error!="":
            return error
    return True

def update_vlan_sys(old_vlan,parent_interface,vlan_tag,vlan_priority):
    """function to update vlan in system"""
    commands=[
        f"nmcli connection modify {old_vlan} con-name  vlan{vlan_tag} ifname vlan{vlan_tag} dev {parent_interface} id {vlan_tag} ingress {vlan_priority}",
        f"nmcli connection modify vlan{vlan_tag} connection.autoconnect yes",
        f"nmcli connection down {old_vlan}   && nmcli connection up {old_vlan} ",
        
        # "systemctl restart NetworkManager"
    ]
   
    for cmd in commands:
        _, error = execute_cmd(cmd)
        if error!="":
            return error
    return True

def delete_vlan_sys(vlan):
    """function to delete vlan in system"""
    ifname = vlan.split('@')[0].strip()

    # Drop the filter table FIRST: the loop below bails out on the first command
    # that writes to stderr (dhcpd4 restart fails when the unit is absent), so
    # anything placed after it may never run. Without this, every deleted VLAN
    # leaves an orphan `table inet filter_vlanX` pointing at a dead interface.
    #
    # /etc/rules/<ifname> is the PERSISTED copy that the firewall reload rebuilds
    # the ruleset from — dropping the live table alone is not enough: the table
    # reappears on the next reload/resync/restore.
    execute_cmd("nft delete table inet filter_{} 2>/dev/null || true".format(ifname))
    execute_cmd("rm -rf /etc/rules/{}".format(ifname))

    commandes= [
        f"nmcli connection delete {vlan}",
        "sed -i '/{}/d' /etc/systemd/system/Asguard-Networking.service".format(ifname),
         '[ -e "/etc/dhcp4_servers/{}/dhcpd.conf" ] && echo -n > /etc/dhcp4_servers/{}/dhcpd.conf '.format(vlan,vlan),
        "systemctl restart dhcpd4.service"
        ]
    for cmd in commandes:
        _, error = execute_cmd(cmd)
        if error!="":
            # print(cmd)
            return error

    return True
def convert_priority(priority):
    match priority:
        case 'Best Effort ( 0 , default )':
            priority="0:1"
        case 'Background ( 1, lowest)':
            priority="1:0"
        case 'Excellent Effort (2)':
            priority="2:2"
        case 'Critical Applications (3)':
            priority="3:3"
        case 'Video (4)':
            priority="4:4"
        case 'Voice (5)':
            priority="5:5"
        case 'Internetwork Control (6)':
            priority="6:6"
        case 'Network Control (7)':
            priority="7:7"
    return priority

def save_in_db(aux_save,interface_serializer):
    if aux_save and interface_serializer.is_valid():
        interface_serializer.save()
        msg=f"{CONSTANT_VLAN_CONFIG} {SUCCESS_MESSAGES_SAVED}"
        status=200
    else:
        msg=str(next(iter(interface_serializer.errors.values()))[0]).strip('.')+"!"
        status=400
    return msg,status

