from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.functions_logs import get_data_system, save_logs_db
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            data_save=get_data_system()
            if not isinstance(data_save, str):
                aux=save_logs_db(data_save)
                if aux is True:
                    return  self.stdout.write(self.style.SUCCESS("All logs Firewall saved successfully!"))
                else:
                    return  self.stdout.write(self.style.ERROR("Error: " + str(aux)))
            else:
                return  self.stdout.write(self.style.ERROR("Error: "+str(data_save)))
                
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR("Error: " + str(e)))