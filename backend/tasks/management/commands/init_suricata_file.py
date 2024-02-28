from django.core.management.base import BaseCommand
from django.db import IntegrityError

from backend.ids_ips.function_sys import execute_cmd, save_config


class Command(BaseCommand):
    def find_file_log(self,stripped_line,updated_lines,line,new_file_log,log_type):
        next_log=False
        next_filename=False
        if "stats:" in stripped_line:
            next_log = True  
            updated_lines.append(line + '\n') 
        elif next_log:
            if "enabled:" in stripped_line:
                next_filename=True
                updated_lines.append(line + '\n') 
            elif next_filename:
                updated_lines.append(f'    filename: {new_file_log}\n')
                next_filename = False
                next_log=False
        return updated_lines
    def update_filenames(self,lines):
        try:
            updated_lines = []
            next_eve_log = False
            next_fastlog = False
            next_stats=False
            next_filename=False
            new_eve_log="/var/log/suricata/eve.json"
            new_fastlog="/var/log/suricata/fast.log"
            stats_log="/var/log/suricata/stats.log"
            # Ajout de la logique de testa() ici
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("#"):
                    updated_lines.append(line + '\n')
                # elif "stats:" in stripped_line:
                #     next_stats = True  
                #     updated_lines.append(line + '\n') 
                # elif next_stats:
                #     if "enabled:" in stripped_line:
                #         next_stats=True
                #         updated_lines.append(line + '\n') 
                #     elif next_stats:
                #         updated_lines.append(f'    filename: {stats_log}\n')
                #         next_stats=False
                    
                ####configgg eve.log
                elif "eve-log:" in stripped_line:
                    next_eve_log = True  
                    updated_lines.append(line + '\n') 
                elif next_eve_log:
                    if "filetype:" in stripped_line:
                        next_filename=True
                        updated_lines.append(line + '\n') 
                    elif next_filename:
                        updated_lines.append(f'      filename: {new_eve_log}\n')
                        next_eve_log=False
                        next_filename=False
                          ####configgg fast.log
                elif "fast:" in stripped_line:
                    next_fastlog = True  
                    updated_lines.append(line + '\n') 
                elif next_fastlog:
                    if "enabled:" in stripped_line:
                        updated_lines.append(line + '\n') 
                    elif next_fastlog:
                        updated_lines.append(f'      filename: {new_fastlog}\n')
                        next_fastlog=False
               
                else:
                  
                    # Conserve les autres lignes telles quelles
                    updated_lines.append(line + '\n')
            return updated_lines
        except Exception:
            # Capture toute autre exception et affiche un message d'erreur
            return None
        
    def handle(self, *args, **kwargs):
        try:
            suricata_yaml_path="/etc/suricata/suricata.yaml"
            output,_= execute_cmd("sudo cat " + suricata_yaml_path)
            status_enabled=True
            if output:
                lines = output.split('\n')
                updated_lines=self.update_filenames(lines)
                # self.save_changes(updated_lines,suricata_yaml_path)
                aux_save=save_config(updated_lines,suricata_yaml_path,status_enabled)
                if aux_save is True:     
                    return "Config saved successfully!"
                else:
                    return aux_save
        except IntegrityError as e:
            return "Error: " + str(e)    