
import subprocess
from dashboard.models import Services
from dashboard.serializers import ServiceDataSerializer
from dms.settings import ASGUARD_VERSION
def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output=""
    error=""
    if completed_process.returncode==0:
        output = completed_process.stdout
    else:
        error = completed_process.stderr
    return output, error 
###

def service_action(service, status):
    output,error=run_command("sudo systemctl {} {}".format(status,service))
    if error!="":
        return error
    return True
###########
def update_sevice_DB(service,data):
    objectConfig=Services.objects.get(service_name=service)
    serviceSerializer = ServiceDataSerializer(objectConfig,data=data)
    if serviceSerializer.is_valid():
        serviceSerializer.save()
        return True
    return serviceSerializer.errors
##############
###########
def add_sevice_DB(data):
    serviceSerializer = ServiceDataSerializer(data=data)
    if serviceSerializer.is_valid():
        serviceSerializer.save()
        return True
    return serviceSerializer.errors
##############
def add_service_DB():
    list_info_services=[]
    list_service=[
    'sshd','dhclient@','suricata','squid','nftables','NetworkManager','openvpn','ipsec','clamv','Asguard-Networking'
    ]
    for s in list_service:
        output,error=run_command("sudo systemctl list-unit-files --type service | awk '{print $1}'")
        list_all_services=output.splitlines()
        status_install=False
        status_started=False
        status_enabled=False
        if s+'.service' in list_all_services:
            status_install=True
            aux_enabled,error=run_command("sudo systemctl is-enabled {}".format(s))
            if aux_enabled.strip()=="enabled":
                status_enabled=True
            aux_started,error=run_command("sudo systemctl is-active  {}".format(s))
            if aux_started.strip()=="active":
                status_started=True
        service={
            "service_name":s,
            "description":"Service {}".format(s),
            "status_enabled":status_enabled,
            "status_started":status_started,
            "status_install":status_install
        }
        list_info_services.append(service)
        if Services.objects.filter(service_name=s).exists():
           update_sevice_DB(s,service)
        else:
            add_sevice_DB(service)
       
    return list_info_services
############
def get_system_infomations():
    #########system_version
    cmd_system_version="sudo uname -a | cut -d ' ' -f 3"
    system_version,error=run_command(cmd_system_version)
    #########version_openssl
    cmd_version_openssl="sudo openssl version | cut -d' ' -f1-5 "
    version_openssl,error=run_command(cmd_version_openssl)
    ########cpu_type
    cmd_cpu_type="sudo lscpu | grep \"Model name\" | cut -d':' -f2- | sed 's/^[[:space:]]*//'"
    cpu_type,error=run_command(cmd_cpu_type)
    cpu_type=' '.join(cpu_type.strip().strip('\n').splitlines())
    ####### data to return
    list_info_services=add_service_DB()
    context={
        "version_asguard":ASGUARD_VERSION.strip().strip('\n'),
        "system_version":system_version.strip().strip('\n'),
        "version_openssl":version_openssl.strip().strip('\n'),
        "cpu_type":cpu_type ,
        "list_info_services":list_info_services

        }
    return context