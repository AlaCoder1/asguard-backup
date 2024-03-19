from django.core.management.base import BaseCommand
import subprocess
from backend.settings.models import Timezone

def run_command(command):
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cmd = "timedatectl list-timezones"
        stdout, stderr = run_command(cmd)
        if(stderr == ''):
            listesOfTimezone = stdout.split('\n')
            listesOfTimezone.pop()
            for time_data in listesOfTimezone:
                timezone = Timezone(name=time_data)
                timezone.save()
            print ("timezones added successfully.")
        else:
            print("erreur.")
    