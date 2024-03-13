import subprocess


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
    f"nmcli connection add type vlan con-name vlan{vlan_tag}@{parent_interface} ifname vlan{vlan_tag} dev {parent_interface} id {vlan_tag} ingress {vlan_priority}",
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
        f"nmcli connection modify {old_vlan} con-name  vlan{vlan_tag}@{parent_interface} ifname vlan{vlan_tag} dev {parent_interface} id {vlan_tag} ingress {vlan_priority}",
        "systemctl restart NetworkManager"
    ]
   
    for cmd in commands:
        _, error = execute_cmd(cmd)
        if error!="":
            return error
    return True

def delete_vlan_sys(vlan):
    """function to update vlan in system"""
    # print(vlan.split('@')[0].strip())
    commandes= [
        f"nmcli connection delete {vlan}",
        "sed -i '/{}/d' /etc/systemd/system/Asguard-Networking.service".format(vlan.split('@')[0].strip())]
    for cmd in commandes:
        _, error = execute_cmd(cmd)
        if error!="":
            return error
        # print(cmd)
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
        msg="Interface saved Successfully!"
        status=200
    else:
        msg=str(next(iter(interface_serializer.errors.values()))[0]).strip('.')+"!"
        status=400
    return msg,status