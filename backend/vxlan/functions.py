import subprocess
from backend.network.models import Interface
from backend.network.serializers import InterfaceSerializer
from django.utils.translation import gettext_lazy as _




def get_all_nmcli_uuids():
    """function to get list of uuid """
    result = subprocess.run(['nmcli', '-t', 'connection', 'show'], stdout=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("nmcli command failed")
    output = result.stdout
    uuids = []
    for line in output.splitlines():
        fields = line.split(':')
        if len(fields) > 1:
            uuids.append(fields[1])  
    return uuids

def execute_cmd(command):
    """function to excecute system commands"""
    command = "sudo " + command
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

def add_vxlan_sys(parent_interface,vxlan_id,vxlan_interface_name,vxlan_source_address,vxlan_destination_address,vxlan_destination_port,vxlan_connection_uuid):
    """function to add vlan in system"""
    commands= [
    f"nmcli connection add type vxlan ifname {vxlan_interface_name} dev {parent_interface} id {vxlan_id} remote {vxlan_destination_address} local {vxlan_source_address} destination-port {vxlan_destination_port} connection.id {vxlan_connection_uuid}",
    f"nmcli connection modify {vxlan_connection_uuid} connection.autoconnect yes",
    "systemctl restart NetworkManager"
          ]
    for cmd in commands:
        print({"cmd":cmd})
        _, error = execute_cmd(cmd)
        if error!="":
            return error
    return True



def save_in_db(aux_save,interface_serializer):
    if aux_save and interface_serializer.is_valid():
        interface_serializer.save()
        msg="Vxlan configuration saved"
        status=200
    else:
        # msg=str(next(iter(interface_serializer.errors.values()))[0]).strip('.')+"!"
        msg=interface_serializer.errors
        status=400
    return msg,status