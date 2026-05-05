from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ids_ips.function_sys import init_logrotate_conf

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-f', '--file', type=str, help='Define a ztna file generated')
   
    def handle(self, *args, **kwargs):
        try:
            file = kwargs['file']
            rot_file=file.split("/")[-1].strip(".log")
            rotation={"service":"ZTNA","path":file ,"time":"daily","size":"10M","number":1,"file":f"/etc/logrotate.d/{rot_file}"},
            service=rotation['service']
            path = rotation['path']
            time = rotation['time']
            size = rotation['size']
            number = rotation['number']
            file_path_log = rotation['file']
            folder_path = "/".join(path.split("/")[:-1]) + "/backup_logs"
            contenu_logrotate = f"""
{path} {{
    {time}
    rotate {number}
    maxsize {size}
    compress
    missingok
    notifempty
    copy
    dateext
    dateformat -%Y-%m-%d-%H:%M:%S
    lastaction
        /usr/local/bin/logrotate-script.sh {path} {folder_path} {service}
    endscript
}}
"""

            aux_log = init_logrotate_conf(contenu_logrotate, file_path_log)
        
            if aux_log is True:
                self.stdout.write(self.style.SUCCESS("Config saved successfully"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to save config: {aux_log}"))
                    
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
