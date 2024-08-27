import subprocess
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ids_ips.function_sys import init_logrotate_conf

class Command(BaseCommand):
   
    def handle(self, *args, **kwargs):
        try:
            list_rotation=[
            {"service":"WAF","path":"/var/log/modsec_audit.log" ,"time":"daily","size":"10M","number":1,"file":"/etc/logrotate.d/waf"},
            {"service":"OpenVPN","path":"/var/log/openvpn/openvpn.log" ,"time":"daily","size":"10M","number":1,"file":"/etc/logrotate.d/openvpn"},
            {"service":"IDS/IPS","path":"/var/log/suricata/fast.log" ,"time":"hourly","size":"10M","number":24,"file":"/etc/logrotate.d/suricata_fast"},
            {"service":"IDS/IPS","path":"/var/log/suricata/stats.log" ,"time":"hourly","size":"10M","number":24,"file":"/etc/logrotate.d/suricata_stats"},
            {"service":"IDS/IPS","path":"/var/log/suricata/suricata.log" ,"time":"hourly","size":"10M","number":24,"file":"/etc/logrotate.d/suricata"},
            {"service":"Squid","path":"/var/log/squid/cache.log" ,"time":"daily","size":"10M","number":1,"file":"/etc/logrotate.d/squid_cache"},
            {"service":"Squid","path":"/var/log/squid/access.log" ,"time":"daily","size":"10M","number":1,"file":"/etc/logrotate.d/squid_access"},
            {"service":"Squid","path":"/var/log/squid/store.log" ,"time":"daily","size":"10M","number":1,"file":"/etc/logrotate.d/squid_store"},
                
            ]
            for service in list_rotation:
                service=service['service']
                path = service['path']
                time = service['time']
                size = service['size']
                number = service['number']
                file_path_log = service['file']
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
