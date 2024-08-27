import subprocess
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ids_ips.function_sys import init_logrotate_conf
from backend.managementLogs.serializers import LogrotateDataSerializer

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-f', '--file', type=str, help='Define a backup file')
        parser.add_argument('-s', '--service', type=str, help='Define a backup service')
    def handle(self, *args, **kwargs):
        try:
                file = kwargs['file']
                service = kwargs['service']
                filename =file.split('/')[-1]
                original_path = file.split("-")[0]
                backup_path = "/".join(file.split("/")[:-1])
                backup_path+="/backup_logs/"
                date="-" .join(filename.split("-")[1:]).strip('.gz')
                data={
                    "service":service,
                    "filename": filename,
                    "original_path": original_path,
                    "backup_path": backup_path,
                    "date": date,
                }
                logrotate_serializer=LogrotateDataSerializer(data=data)
                if logrotate_serializer.is_valid():
                    logrotate_serializer.save()
                    self.stdout.write(self.style.SUCCESS("File backup saved successfully"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to save config: {logrotate_serializer.errors}"))
                    
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
