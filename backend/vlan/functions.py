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
    cmd= f"nmcli connection add type vlan con-name vlan{vlan_tag} ifname vlan{vlan_tag} dev {parent_interface} id {vlan_tag} ingress {vlan_priority}"
    _, error = execute_cmd(cmd)
    if error=="":
        return True
    print(cmd)
    return error