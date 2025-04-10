import subprocess
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.functions_logs import  run_command
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            line_to_add = 'module(load="imjournal")'
            rsyslog_config = """:msg, contains, "___nftables" /var/log/nftables/nftables.log
& stop"""

            commandes = [
            "sudo mkdir -p /var/spool/rsyslog",
            "sudo chmod 755 /var/spool/rsyslog",
            "sudo mkdir -p /etc/rsyslog.d /var/log/nftables",
            "sudo touch /var/log/nftables/nftables.log",
            "sudo chmod 640 /var/log/nftables/nftables.log",
           f"""sudo bash -c 'sed -i "/module(load=\"imjournal\")/c\\{line_to_add}" /etc/rsyslog.conf || echo "{line_to_add}" >> /etc/rsyslog.conf'""",
            f"sudo echo '{rsyslog_config}' | sudo tee /etc/rsyslog.d/10-nftables.conf > /dev/null",
            "sudo systemctl enable rsyslog --quiet  && sudo systemctl restart rsyslog"
]
            for cmd in commandes:
                _,error= run_command(cmd)
            if error!="":
                self.stdout.write(self.style.ERROR("Failed to save log config " + error))
            else:
                self.stdout.write(self.style.SUCCESS("Config log firewall saved successfully!"))
      
              
                    
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR("Error: " + str(e)))