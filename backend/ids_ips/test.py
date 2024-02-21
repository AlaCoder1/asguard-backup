
import subprocess

def update_packet_interface(list_interfaces_af):
    af_packet_conf=[]
    if len(list_interfaces_af)>0:
        for interface in list_interfaces_af:
            interface={cle: valeur for cle, valeur in interface.items() if valeur is not None and cle!="id"}
            for cle, valeur in interface.items():
                if cle=="interface":
                    af_packet_conf.append(f"      - {cle}:{valeur}")
                else:
                    af_packet_conf.append(f"         {cle}:{valeur}")
                    
        out_final=lines[:lines.index('af-packet:')+1]+af_packet_conf+lines[lines.index('# Linux high speed af-xdp capture support'):]   
        return out_final
    
def execute_cmd(command):
    command="sudo "+command
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error
suricata_yaml_path = "/etc/suricata/suricata.yaml"
output,_= execute_cmd("sudo cat " + suricata_yaml_path)
lines=output.split("\n")


list_interfaces=[{
    "id":1,
    "interface":"enp0s8",
    "threads": None,
    "cluster-id": 95,
    "cluster-type": "cluster_flow",
    "defrag": "no",
    "use-mmap": "yes",
    "ring-size": 12000
},
                 {
    "interface":"enp0s17",
    "threads": 2,
    "cluster-id": 95,
    "cluster-type": "cluster_flow",
    " defrag": "no",
    "use-mmap": "yes",
    "ring-size": 12000
}]
# af_packet_conf=[]
# if len(list_interfaces)>0:
#     for interface in list_interfaces:
#         interface={cle: valeur for cle, valeur in interface.items() if valeur is not None}
#         for cle, valeur in interface.items():
#             af_packet_conf.append(f"     {cle}:{valeur}")
# print(af_packet_conf)
# out_final=lines[:lines.index('af-packet:')+1]+af_packet_conf+lines[lines.index('# Linux high speed af-xdp capture support'):]   
out_final=update_packet_interface(list_interfaces)
with open("/etc/suricata.yaml", 'w') as local_file:
    for string in out_final:
        local_file.write(string+"\n")
# print(lines[lines.index('af-packet:'):lines.index('# Linux high speed af-xdp capture support')])
# print(lines[:lines.index('af-packet:')+1]+lines[lines.index('# Linux high speed af-xdp capture support'):])