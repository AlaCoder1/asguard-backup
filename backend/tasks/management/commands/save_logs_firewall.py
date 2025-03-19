from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.functions_logs import get_data_system, save_logs_db
from datetime import datetime
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            aux=get_data_system()
            if aux is True:
                    return  self.stdout.write(self.style.SUCCESS(f"{datetime.now()} All logs Firewall saved successfully!"))
            else:
                    return  self.stdout.write(self.style.ERROR("Error: " + str(aux)))
                
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR("Error: " + str(e)))