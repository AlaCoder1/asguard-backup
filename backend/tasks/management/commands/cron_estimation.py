from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.functions_logs import  run_command
from datetime import datetime
import pytz
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            cmd_taille="sudo ls -lh /var/log/nftables/nftables.log | awk '{print $5}'"
            cmd_num_line="sudo wc -l /var/log/nftables/nftables.log | awk '{print $1}'"
            cmd_number_backup="test -d /var/log/nftables/backup_logs/ && echo $(ls -1 /var/log/nftables/backup_logs/ | wc -l) || echo 0"
            cmd_size_backup="test -d /var/log/nftables/backup_logs/ && echo $(ls -lh /var/log/nftables/backup_logs/ | awk '{print $2}') || echo 0"
            taille, _ = run_command(cmd_taille)
            num_line,_=run_command(cmd_num_line)
            number_backup,_=run_command(cmd_number_backup)
            size_backup,_=run_command(cmd_size_backup)
            size_backup=size_backup.splitlines()[0].split(" ")[0]
            tunisian_tz = pytz.timezone('Africa/Tunis')
            date = datetime.now(tunisian_tz).strftime("%Y-%m-%d %H:%M:%S")
            data={"date":date,
                  "size_file":taille.strip("\n"),
                  "num_line":int(num_line.strip("\n")),
                  "number_backup":int(number_backup.strip("\n")),
                  "size_backup":size_backup
                  }
            self.stdout.write(self.style.SUCCESS(str(data)))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR("Error: " + str(e)))