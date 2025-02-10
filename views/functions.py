import json
import subprocess
from backend.double_mask.functions import is_address_in_subnet
from backend.double_mask.models import DoubleMask
from backend.managementLogs.models import LogrotateData, LogsData
from backend.network.functions import run_command
from backend.network.models import Interface
from backend.rules.models import Rule
from backend.server_dhcp4.models import ServerDhcp4
from backend.vlan.models import Vlan
from django.core import serializers
from backend.vxlan.models import Vxlan
from views.test_address import get_nft_ip_addresses

def delete_inactive_conn():
    result = subprocess.run("sudo nmcli connection show | awk '$NF == \"--\" {print $2}'", shell=True, capture_output=True, text=True)
    if result.stdout.strip():  
        uuids = result.stdout.strip().splitlines()
        for uuid in uuids:
            subprocess.run(f"sudo nmcli connection delete uuid {uuid}", shell=True) 
def get_vlan(request):
    """API to get all vlan from database """
    if (request.method == 'GET'):
        list_vlan=[]
        # parse the incoming information
        vlan_object=Vlan.objects.all()
        vlan = serializers.serialize("json", vlan_object)
        res = json.loads(vlan)
        for i in range(len(res)):
            res[i]['fields']['id']=res[i]["pk"]
            res[i]['fields']['name_interface']=Interface.objects.get(id=res[i]['fields']['parent_interface']).name_interface
            list_vlan.append(res[i]['fields'])
    return list_vlan

def get_vlan_interface(request):
    """API to get all vlan assigned from database """
    if (request.method == 'GET'):
        list_vlan_interface=[]
        # parse the incoming information
        vlan_object = Interface.objects.filter(ifname__startswith='vlan')
        vlans = serializers.serialize("json", vlan_object)
        res = json.loads(vlans)
        for i in range(len(res)):
            vlan_tag=res[i]['fields']['ifname'].split("@")[0].strip("vlan").strip()
            interface=Vlan.objects.get(vlan_tag=vlan_tag).parent_interface_id
            id_vlan=Vlan.objects.get(vlan_tag=vlan_tag).id
            ifname_parent=Interface.objects.get(id=interface).ifname     
            data={
                "id":res[i]['pk'],
                "id_vlan":id_vlan,
                "name_interface":res[i]['fields']['name_interface'],
                "network_port":f"VLAN {vlan_tag} on {ifname_parent}"
            }
            if get_uuid_v2(res[i]['fields']['ifname']) is None:
                int_delete=Interface.objects.get(ifname=res[i]['fields']['ifname'])
                delete_inactive_conn()
                int_delete.delete()
            else:
                list_vlan_interface.append(data)
    return list_vlan_interface

def get_all_server_dhcp4(request):
    """API to get all dhcp4 server from database """
    if (request.method == 'GET'):
        list_dhcp4_server=[]
        # parse the incoming information
        dhcp4_object=ServerDhcp4.objects.all()
        dhcp4 = serializers.serialize("json", dhcp4_object)
        res = json.loads(dhcp4)
        print({"res":res})
        for i in range(len(res)):
            res[i]['fields']['id']=res[i]["pk"]
            ranges_from=res[i]['fields']['range_from'].split(',') if res[i]['fields']['range_from'] is not None else None
            ranges_to=res[i]['fields']['range_to'].split(',') if res[i]['fields']['range_to'] is not None else None
            ranges_address=[]
            if ranges_from is not None :
                for j in range(len(ranges_from)):
                    ranges_address.append({"range_from":ranges_from[j] , "range_to":ranges_to[j]})
            
            res[i]['fields']['ranges_address']=ranges_address
            res[i]['fields'].pop("range_from") if "range_from" in res[i]['fields']  else ""
            res[i]['fields'].pop("range_to") if "range_tos" in res[i]['fields']  else ""
            list_dns=res[i]['fields']['dns_server'].split(',') if res[i]['fields']['dns_server'] is not None else None
            list_dns=[x.strip() for x in list_dns ] if list_dns is not None else None
            res[i]['fields']['dns_server']=list_dns
            
            res[i]['fields']['name_interface']=Interface.objects.get(id=res[i]['fields']['interface']).name_interface
            list_dhcp4_server.append(res[i]['fields'])
            print(list_dhcp4_server)
    return list_dhcp4_server


def get_vxlan_interface(request):
    """API to get all vlan assigned from database """
    if (request.method == 'GET'):
        list_vlan_interface=[]
        # parse the incoming information
        vlan_object = Interface.objects.filter(name_interface__startswith='VXLAN')
        vlans = serializers.serialize("json", vlan_object)
        res = json.loads(vlans)
        for i in range(len(res)):
            vlan_ifname=res[i]['fields']['ifname']
            
            interface=Vxlan.objects.get(vxlan_interface_name=vlan_ifname).parent_interface_id
            ifname_parent=Interface.objects.get(id=interface).ifname
            id_vxlan=Vxlan.objects.get(vxlan_interface_name=vlan_ifname).id
            vxlan_tag=Vxlan.objects.get(vxlan_interface_name=vlan_ifname).vxlan_id
            data={
                "id":res[i]['pk'],
                "id_vxlan":id_vxlan,
                "name_interface":res[i]['fields']['name_interface'],
                "network_port":f"VXLAN {vxlan_tag} on {ifname_parent}"
            }
            print({"ifname":res[i]['fields']['ifname'],"uuid":get_uuid_v2(res[i]['fields']['ifname'])})
            if get_uuid_v2(res[i]['fields']['ifname']) is None:
                int_delete=Interface.objects.get(ifname=res[i]['fields']['ifname'])
                delete_inactive_conn()
                int_delete.delete()
            else:
                list_vlan_interface.append(data)
    return list_vlan_interface


def get_vxlan(request):
    """API to get all vxlan from database """
    if (request.method == 'GET'):
        list_vxlan=[]
        # parse the incoming information
        vxlan_object=Vxlan.objects.all()
        vxlan = serializers.serialize("json", vxlan_object)
        res = json.loads(vxlan)
        for i in range(len(res)):
            res[i]['fields']['id']=res[i]["pk"]
            res[i]['fields']['name_interface']=Interface.objects.get(id=res[i]['fields']['parent_interface']).name_interface
            list_vxlan.append(res[i]['fields'])
    return list_vxlan

def get_logs_data(request):
    """API to get the last 1000 logs from the database"""
    if request.method == 'GET':
        list_logs = []
        logs_object = LogsData.objects.all().order_by('-id')[:1000]
        print({'logs_object': logs_object})
        logs = serializers.serialize("json", logs_object)
        res = json.loads(logs)
        for log in res:
            log['fields']['id'] = log["pk"]
            list_logs.append(log['fields'])
        return  list_logs
    
    
    
    

    
    
    
    

def get_logrotate_data(request,service):
    """
    API to retrieve all logrotate data .

    Parameters:
    request (HttpRequest): The incoming request object.

    Returns:
    JsonResponse: A JSON response containing the logrotate data .
    
    """
    if request.method == 'GET':
        list_logs = []
        logs_object = LogrotateData.objects.filter(service=service).order_by('-id')
        logs = serializers.serialize("json", logs_object)
        res = json.loads(logs)
        for log in res:
            log['fields']['id'] = log["pk"]
            list_logs.append(log['fields'])
        return list_logs
    
    
def get_uuid_v2(ifname):
    ifname=ifname.split("@")[0]if ifname.find("@")!=-1 else ifname
    cmd = "sudo nmcli connection show | awk '$NF == \"{}\" {{print}}'".format(ifname)
    output,_=run_command(cmd)
    if len(output)==0:
        return None
    else:
        output = output.split('  ')
        output=[value for value in output if value]
        uuid=output[1]
        return uuid
    
def get_double_mask(request):
    """API to get the double mask status from the database"""
    if request.method == 'GET':
        output,_=run_command('sudo lsmod | grep "calculateDM"')
        if output=="":
            active=False
        else:
            active=True
        if DoubleMask.objects.all().count()==1:
            double_mask_object=DoubleMask.objects.all().first()
            double_mask_object.active=active
            double_mask_object.save()
        else:
            double_mask_object=DoubleMask(active=active)
            double_mask_object.save()
    return active
    
    
def get_compr_ratio(request):
    """
    API to get compression ratioo.
    
    This function handles the GET request to get the compression ratio of double mask.
    
    
    """
    if request.method == 'GET':
        output,error=run_command('sudo dmesg | grep "The Double mask for"')
        if output=="":
            ratio=0
        else:
            ruleset_list,n=get_nft_ip_addresses()
            subnet_double=output.split("is")[1].split("/")[0:1]
            subnet=subnet_double[0]+"/"+subnet_double[1]
            ruleset_compr=[x for x in ruleset_list if is_address_in_subnet(x,subnet) ]
            ratio=(len(ruleset_compr)/n)
        return ratio