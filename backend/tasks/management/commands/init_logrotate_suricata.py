import subprocess
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ids_ips.function_sys import init_logrotate_conf, init_script_bash, update_file_timer
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            contenu_logrotate="""
/var/log/suricata/fast.log {
        hourly 
        rotate 24 
        maxsize 10M 
        compress 
        missingok 
        notifempty 
        copy 
        dateext 
        dateformat -%Y-%m-%d-%H:%M:%S 
        lastaction 
            /usr/local/bin/logrotate-script.sh 
        endscript 
    }
            """
            script="""
#!/bin/bash
# Set variables 
LOG_FILE="/var/log/suricata/fast.log" 
DEST_DIR="/var/log/suricata/backup_logs" 
# Truncate log file 
tail -n 10000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE" 
# Create backup directory 
mkdir -p "$DEST_DIR" 
# Copy log files to backup directory 
for file in /var/log/suricata/fast.*.gz; do 
    [ ! -e "${DEST_DIR}$(basename "$file")" ] && mv "$file" "${DEST_DIR}" 
done 
#command to update in database: NB you have to modify path of project!! 
python /asguard/newdms/manage.py init_alerts_suricata_cron 
            """ 
            file_path_log="/etc/logrotate.d/suricata"
            script_path="/usr/local/bin/logrotate-script.sh"
            aux_log=init_logrotate_conf(contenu_logrotate,file_path_log)
            file_path_timer="/usr/lib/systemd/system/logrotate.timer"
            contenu_timer="""
[Unit] 
Description=Daily rotation of log files 
Documentation=man:logrotate(8) man:logrotate.conf(5) 
[Timer] 
OnCalendar=hourly 
Persistent=true 
[Install]
WantedBy=timers.target 
            """
            if aux_log is True:
                aux_script=init_script_bash(script,script_path)
                if aux_script is True:
                        aux_update=update_file_timer(file_path_timer,contenu_timer)
                        if aux_update is True:
                            return "Config saved successfully"
                        else:
                            return aux_update
                else:
                    return aux_script
            else:
                return aux_log
        except IntegrityError as e:
            return "Error: " + str(e)