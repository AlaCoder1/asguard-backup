

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ids_ips.function_sys import init_script_bash

class Command(BaseCommand):
        
    def handle(self, *args, **kwargs):
        try:
            script = r"""
#!/bin/bash
# Set variables 
LOG_FILE="\$1"
DEST_DIR="\$2"
SERVICE="\$3"
# Truncate or clear log file depending on its path
if [ "\$LOG_FILE" == "/var/log/modsec_audit.log" ||  "\$LOG_FILE" == "/var/log/openvpn/openvpn.log"]; then
    # Clear the log file
    > "\$LOG_FILE"
else
    # Truncate the log file to the last 10,000 lines
    tail -n 10000 "\$LOG_FILE" > "\${LOG_FILE}.tmp" && mv "\${LOG_FILE}.tmp" "\$LOG_FILE"
fi

# Create backup directory 
mkdir -p "\$DEST_DIR" 

# Copy log files to backup directory 
for file in $LOG_FILE-*.gz; do
    if [ ! -e "${DEST_DIR}/$(basename "$file")" ]; then
                python /asguard/newdms/manage.py init_logrotate_db -f "$file" -s "$SERVICE"
                mv "$file" "$DEST_DIR"
fi
done
"""
            script_path = "/usr/local/bin/logrotate-script.sh"       
            aux_script = init_script_bash(script, script_path)
            
            if aux_script is True:
                self.stdout.write(self.style.SUCCESS("Script saved successfully!"))
            else:
                self.stdout.write(self.style.ERROR("Failed to save the script: " + aux_script))
           
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR("Error: " + str(e)))
