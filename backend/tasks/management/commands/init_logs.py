import subprocess
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.managementLogs.functions import get_attributes_logs, get_logs_sys, save_logs_database
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            output=get_logs_sys()
            logs=output.splitlines()
            for log in logs:
                date, process, message=get_attributes_logs(log)
                data = {
                    "date": date,
                    "process": process,
                    "message": message,
                }
                save_logs_database(data)
            return "All logs saved successfully!"
                
        except IntegrityError as e:
            return "Error: " + str(e)