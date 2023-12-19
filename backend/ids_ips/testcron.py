from datetime import datetime
from function_sys import execute_cmd

max_size=10000
suricata_log_path = "/var/log/suricata/fast.log"
cmd_read = f"cat {suricata_log_path}"
output, error = execute_cmd(cmd_read)
if not error:
    logs = output.splitlines()
    nb_lines=len(logs)
    print({"nblines finales":nb_lines})
    if nb_lines>max_size:
        nb_iter=nb_lines//max_size
        print({"nblines initiales":nb_lines})
        print(nb_iter)
        if nb_lines%max_size!=0:
            nb_lines=nb_iter*max_size
            print(nb_lines)
        logs_add=logs[:nb_lines]
        date_systeme = datetime.now().date()     
        print({"logs_add":len(logs_add),"log reste":len(logs[nb_lines:]),"nb_lines":nb_lines,"nb_iter":nb_iter})  
        
        
