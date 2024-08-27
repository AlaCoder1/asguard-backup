from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ids_ips.function_sys import update_file_timer

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            file_path_timer = "/usr/lib/systemd/system/logrotate.timer"
            contenu_timer = """
[Unit] 
Description=Daily rotation of log files 
Documentation=man:logrotate(8) man:logrotate.conf(5) 
[Timer] 
OnCalendar=hourly 
Persistent=true 
[Install]
WantedBy=timers.target 
            """
           
            aux_update = update_file_timer(file_path_timer, contenu_timer)
            if aux_update is True:
                self.stdout.write(self.style.SUCCESS("Config logrotate timer saved successfully!!"))
            else:
                self.stdout.write(self.style.WARNING(aux_update))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR("Error: " + str(e)))
