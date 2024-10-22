import subprocess
from .models import *
from django.conf import settings
import time
from .models import *
####################################################  BD functions  ############################################################### 

####update in Database functions
#function to update config tables
def update_DB(id,data,model,IP4serializer):
    data={key: value for key, value in data.items() if value is not None}
    data['interface']=id
    if model.objects.filter(interface_id=id).exists():
        objectConfig=model.objects.get(interface_id=id)
        # Set all attributes to None
        for field in objectConfig._meta.fields:
            if field.attname not in ["id", "interface_id",'ifname','created_at','updated_at','created_by','updated_by','request_only','prefix_hint','information_only','non_temporary','ipv4_connectivity','prefix_delegation']: 
                setattr(objectConfig, field.attname, None)
        setattr(objectConfig, 'updated_by', settings.CurrentUserId)
        serializerIP4Config = IP4serializer(objectConfig,data=data)
    else:
        serializerIP4Config = IP4serializer(data=data)
    if (serializerIP4Config.is_valid()):
        serializerIP4Config.save()
        return True
    return serializerIP4Config.errors
   

#function to update interface tables  
def update_interface_table(name_interface,data,InterfaceSerializer):
    data={key: value for key, value in data.items() if value is not None}
    objectConfig=Interface.objects.get(name_interface=name_interface)
    # Set all attributes to None
    for field in objectConfig._meta.fields:
        if field.attname not in ["id",'ifname','created_at','updated_at','name_interface','description','private_aux','bogon_aux','is_main']: 
            setattr(objectConfig, field.attname, None)
    serializerInterface= InterfaceSerializer(objectConfig,data=data)
    if serializerInterface.is_valid():
            serializerInterface.save()     
            return True
    return serializerInterface.errors 

### function to get data from interface name
def device_name_interface(name_interface):
    data = Interface.objects.get(name_interface=name_interface)
    return data

#################################################### end BD functions  ############################################################### 

####################################################  system functions  ############################################################### 
def restart_network_manager():
    restart_cmd = "sudo systemctl restart NetworkManager"
    run_command(restart_cmd)
    time.sleep(5)
## function to get uuid connection
def get_uuid_con(ifname):
    ifname=ifname.split("@")[0]if ifname.startswith("vlan")else ifname
    cmd = "sudo nmcli connection show | awk '$NF == \"{}\" {{print}}'".format(ifname)
    output,_=run_command(cmd)
    # print({"cmd":cmd,"output":output})
    if len(output)==0:
        restart_network_manager()
        output,_=run_command(cmd)
        if len(output) == 0:
            return None
    else:
        output = output.split('  ')
        output=[value for value in output if value]
        uuid=output[1]
        return uuid
    
## get config by system NetworkManager
def refresh_conf_system(uuid,aux_main):
    cmd_final=[]
    if not aux_main:
        cmd_final=[ "sudo nmcli conn down {} && sudo nmcli conn up {}".format(uuid, uuid),]
    return cmd_final

##get old configuration in service
def get_old_config():
    cmd = "cat /etc/systemd/system/Asguard-Networking.service"
    output,error=run_command(cmd)
    output=output.split("\n")
    return output,error
   
def add_requirement(ifname,output):
    ifname=ifname.split("@")[0]if ifname.startswith("vlan")else ifname
    index=output.index('[Service]')
    values_to_add=['BindsTo=sys-subsystem-net-devices-{}.device'.format(ifname),
                    'After=sys-subsystem-net-devices-{}.device'.format(ifname)]
    all_interfaces = Interface.objects.all()
    interface_names = [interface.ifname.split("@")[0] if ifname.startswith("vlan") else interface.ifname for interface in all_interfaces ]
    values_to_add = [x for x in values_to_add if x not in output]
    output = output[:index] + values_to_add + output[index:]
    output[:index] = [x for x in output[:index] if (x.startswith("BindsTo") or  x.startswith("After")) and x.split(".")[0].split("-")[-1] in interface_names]
    
    return output

def add_cmd(output,commandes):
    index_cmd=output.index('[Install]') 
    output = output[:index_cmd] + commandes + output[index_cmd:]
    return output 

def clean_old_config(config,typeConf):
    #test si les commentaires #start et #end exists
    if "#Start {}".format(typeConf) in config and "#End {}".format(typeConf) in config: 
        #indice #start
        i=config.index("#Start {}".format(typeConf))
        #indice #end
        j=config.index("#End {}".format(typeConf))
        #remove old config
        config=config[:i]+config[j+1:]
    return config
 

## Function to execute command with timeout
def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

## run command with time
def run_command_with_timeout(type, command, timeout):
    try:
        start_time = time.time()
        # Start the subprocess with a timeout
        process = subprocess.Popen(
            command,
            shell=True,  # Use shell=True to interpret the entire command as a single string
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Use text=True to handle the output as text (Python 3.7+)
        )
        stdout, stderr = process.communicate(timeout=timeout)
        elapsed_time = time.time() - start_time
          # Create a new instance of your model
        new_entry = tempsExucution(type=type, cmd=command, temps=elapsed_time)
        # Save the instance to the database
        new_entry.save()
        # If the subprocess completed within the timeout
        if process.returncode == 0:
            # print(f"Command not too long ({elapsed_time:.2f} seconds). {command}")
            return (stdout, stderr)
        else:
            # print(command,"==============>",process.returncode )
            return None,stderr

    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        # If the subprocess exceeded the timeout, send a Ctrl+C signal
        process.terminate()
        process.wait()
        print(f"Command too long ({elapsed_time:.2f} seconds). {command}")
        return None, "Command timed out and was terminated."
 
def run_all_commands(commandes,setuptypeIP4,timeout):
    for cmd in commandes:
        output,error=run_command_with_timeout(setuptypeIP4, cmd, timeout)
        if output is None and error!="" :
            print(error)
            return error
        if cmd.find("sudo dhclient") == -1   and error!="" and (error is not None and not error.startswith("Warning")):
            return error
    return True

def desactiver_interface_remote(ifname,output):
    ifname=ifname.split("@")[0]if ifname.startswith("vlan")else ifname
    #la liste des commandes pour la désactivation de l'interface dans Asguard Service
    commands=[
         "#Start IP4Config {}".format(ifname),
         "ExecStart=/usr/bin/ip addr flush dev {}".format(ifname),
         "ExecStart=/usr/bin/ip link set dev {} down".format(ifname),        
         "#End IP4Config {}".format(ifname)
    ]
    output=add_requirement(ifname,output)
    output=add_cmd(output,commands)
    #la liste des commandes à executer pour désactiver l'interface
    cmd_final=[ 
        "sudo sed -i '/{}/d' /etc/systemd/system/Asguard-Networking.service".format(ifname),
        "sudo sed -i '/{}/d' /etc/ConfigInterfaces".format(ifname),
        "sudo ip addr flush dev {}".format(ifname),
        "sudo ip link set dev {} down".format(ifname),
        """sudo cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output))
        
        ]
    for cmd in cmd_final:
        output,error=run_command(cmd)
        if error:
            msg=error,"    :"+cmd
            return False
    return True




#################################################### end system functions  ############################################################### 
