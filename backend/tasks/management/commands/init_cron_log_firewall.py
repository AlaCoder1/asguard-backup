import subprocess
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.functions_logs import get_data_system, run_command, save_logs_db
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
           
            cron="*/5 * * * * /usr/bin/journalctl --vacuum-time=3d; /usr/bin/python3 /asguard/asguard/manage.py save_logs_firewall > /var/log/nftables/cron_nftables.log 2>&1"
            try:
                existing_crontab = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=True)
                cron_jobs = existing_crontab.stdout.strip().split("\n")
            except subprocess.CalledProcessError:
                cron_jobs = []  

            if cron not in cron_jobs:
                new_crontab = cron
                commandes=[
                "sudo mkdir -p /var/log/nftables",
                f'(sudo crontab -l 2>/dev/null; sudo echo "{new_crontab}") | sudo crontab -'
                ]
                for cmd in commandes:
                    _,error= run_command(cmd)
                if error!="":
                    self.stdout.write(self.style.ERROR("Failed to save cron job: " + error))
                else:
                    self.stdout.write(self.style.SUCCESS("Cron job saved successfully"))
            else:
                self.stdout.write(self.style.SUCCESS("Cron job already exists"))
              
                    
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR("Error: " + str(e)))